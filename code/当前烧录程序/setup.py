# 开机启动画面 - 立创·庐山派-K230-CanMV
# 显示 setup.png 并播放 setup.wav，快速点击屏幕 3 下可跳过

import os, time, image
from media.display import *
from media.media import *
from media.pyaudio import *
import media.wave as wave
from machine import Pin
from machine import FPIOA
from machine import TOUCH

# ============================================================
# 路径
# ============================================================
SETUP_IMG = "/data/code/setup/setup.png"
SETUP_WAV = "/data/code/setup/setup.wav"
AMP_PIN   = 10
TAP_COUNT = 1        # 需要点击次数
TAP_WINDOW_MS = 2000  # 点击有效时间窗口

# ============================================================
# 全局
# ============================================================
_amp_inited = False
HT_CTRL = None

# ============================================================
# 功放
# ============================================================
def init_amp():
    global _amp_inited, HT_CTRL
    if not _amp_inited:
        fpioa = FPIOA()
        fpioa.set_function(AMP_PIN, FPIOA.GPIO10)
        _amp_inited = True
    HT_CTRL = Pin(AMP_PIN, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    HT_CTRL.high()

def deinit_amp():
    global HT_CTRL
    try:
        if HT_CTRL:
            HT_CTRL.low()
    except:
        pass

# ============================================================
# 跳过检测（机械按键式消抖：上升沿 + 时间窗口 + 最小间隔）
# ============================================================
_tap_times = []             # 记录每次有效点击时间
_last_press_time = 0        # 上次按下时刻
_touch_was_pressed = False  # 触摸状态
DEBOUNCE_MS = 150           # 消抖时间（两次点击最小间隔）

def check_skip(tp):
    """检测触摸屏快速点击（机械按键消抖），返回 True 表示需要跳过"""
    global _tap_times, _touch_was_pressed, _last_press_time

    now = time.ticks_ms()

    # 清理超过时间窗口的旧记录
    _tap_times = [t for t in _tap_times
                  if time.ticks_diff(now, t) < TAP_WINDOW_MS]

    points = tp.read(5)
    if points:
        # 上升沿检测（未按下 → 按下）
        if not _touch_was_pressed:
            # 消抖：距离上次有效点击必须超过最小间隔
            if time.ticks_diff(now, _last_press_time) > DEBOUNCE_MS:
                _tap_times.append(now)
                _last_press_time = now
            _touch_was_pressed = True
    else:
        _touch_was_pressed = False

    return len(_tap_times) >= TAP_COUNT

# ============================================================
# 播放 WAV（非阻塞，可中断）
# ============================================================
def play_wav_skippable(filepath, tp):
    wf = None
    p = None
    stream = None
    skipped = False
    try:
        wf = wave.open(filepath, 'rb')
        framerate = wf.get_framerate()
        channels  = wf.get_channels()
        sampwidth = wf.get_sampwidth()
        chunk = int(framerate / 25)

        p = PyAudio()
        stream = p.open(
            format=p.get_format_from_width(sampwidth),
            channels=channels,
            rate=framerate,
            output=True,
            frames_per_buffer=chunk,
        )
        stream.volume(vol=100)

        data = wf.read_frames(chunk)
        while data:
            # 每写 2 个块检查一次触摸（频繁检查会导致卡顿）
            for _ in range(2):
                if data:
                    stream.write(data)
                    data = wf.read_frames(chunk)

            # 检查跳过
            if check_skip(tp):
                print("[启动画面] 用户跳过")
                skipped = True
                break

        if not skipped:
            print("[启动画面] 音频播放完毕")
    except BaseException as e:
        print("[启动画面] 音频异常: " + str(e))
    finally:
        try:
            if stream:
                stream.stop_stream()
                stream.close()
        except:
            pass
        try:
            if p:
                p.terminate()
        except:
            pass
        try:
            if wf:
                wf.close()
        except:
            pass

# ============================================================
# 显示 PNG 图片
# ============================================================
def show_setup_image():
    try:
        img = image.Image(SETUP_IMG)
        print("[启动画面] 图片尺寸: " + str(img.width()) + "x" + str(img.height()))
        Display.show_image(img.to_rgb565())
    except BaseException as e:
        print("[启动画面] 图片异常: " + str(e))

# ============================================================
# 主流程
# ============================================================
def main():
    print("[启动画面] 开始 (快速点击屏幕 %d 下可跳过)" % TAP_COUNT)

    init_amp()
    Display.init(Display.ST7701, width=800, height=480, to_ide=True)
    MediaManager.init()

    tp = TOUCH(0)

    try:
        show_setup_image()
        play_wav_skippable(SETUP_WAV, tp)
    except BaseException as e:
        print("[启动画面] 异常: " + str(e))
    finally:
        Display.deinit()
        time.sleep_ms(60)
        MediaManager.deinit()
        deinit_amp()

    print("[启动画面] 结束，进入主界面")

if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()
