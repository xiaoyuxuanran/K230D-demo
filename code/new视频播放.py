# 视频播放器（修复版） - 立创·庐山派-K230-CanMV
# 修复：无声（功放未使能）、马赛克卡顿（未初始化显示/媒体管线）

import os, sys, time
from media.player import *
from media.display import *
from media.media import *
from machine import Pin
from machine import FPIOA

# ============================================================
# 参数
# ============================================================
DISPLAY_WIDTH  = 800
DISPLAY_HEIGHT = 480
AMP_PIN        = 10
VIDEO_PATH     = "/data/code/video/new.mp4"

# ============================================================
# 功放使能
# ============================================================
_amp_inited = False
HT_CTRL = None

def init_amp():
    global _amp_inited, HT_CTRL
    if not _amp_inited:
        fpioa = FPIOA()
        fpioa.set_function(AMP_PIN, FPIOA.GPIO10)
        _amp_inited = True
    HT_CTRL = Pin(AMP_PIN, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    HT_CTRL.high()

def deinit_amp():
    try:
        if HT_CTRL:
            HT_CTRL.low()
    except:
        pass

# ============================================================
# 视频播放
# ============================================================
start_play = False

def player_event(event, data):
    global start_play
    if event == K_PLAYER_EVENT_EOF:
        start_play = False

def play_video(filename):
    global start_play
    print("[视频] 播放: " + filename)

    # 1. Player 内部会初始化显示管线，这里只初始化 VB 缓冲池和功放
    MediaManager.init()
    init_amp()

    # 2. 创建播放器（Player 自行管理 Display.ST7701 初始化）
    player = Player(Display.ST7701)
    player.load(filename)
    player.set_event_callback(player_event)
    player.start()
    start_play = True

    # 4. 等待播放结束
    try:
        while start_play:
            time.sleep(0.1)
            os.exitpoint()
    except KeyboardInterrupt:
        print("[视频] 用户停止")
    except BaseException as e:
        print("[视频] 异常: " + str(e))
        sys.print_exception(e)

    # 5. 清理（Display 由 Player 内部管理，不重复 deinit）
    player.stop()
    deinit_amp()
    time.sleep_ms(60)
    MediaManager.deinit()
    print("[视频] 播放结束")

if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    play_video(VIDEO_PATH)
