# 录音机功能 - 立创·庐山派-K230-CanMV
# 参照 庐山派-lite-V1-1 麦克风和功放喇叭 示例代码

import os, time, image
from media.display import *
from media.media import *
from media.pyaudio import *
import media.wave as wave
from machine import TOUCH
from machine import Pin
from machine import FPIOA

# ============================================================
# 参数
# ============================================================
DISPLAY_WIDTH  = 800
DISPLAY_HEIGHT = 480
AUDIO_DIR      = "/data/code/audio"
MAX_REC_SEC    = 30
AMP_PIN        = 10

# ============================================================
# 功放（参照基础测试代码：麦克风和功放喇叭）
# ============================================================
HT_CTRL = None

def init_amp():
    global HT_CTRL
    fpioa = FPIOA()
    fpioa.set_function(AMP_PIN, FPIOA.GPIO10)
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
# 文件管理
# ============================================================
def ensure_dir():
    try:
        os.stat(AUDIO_DIR)
    except:
        os.mkdir(AUDIO_DIR)

def scan_files():
    files = []
    try:
        for f in os.listdir(AUDIO_DIR):
            if f.lower().endswith('.wav'):
                files.append(f)
        files.sort(reverse=True)
    except:
        pass
    return files

def get_wav_duration_ms(filepath):
    try:
        wf = wave.open(filepath, 'rb')
        sz = os.stat(filepath)[6]
        sw = wf.get_sampwidth()
        ch = wf.get_channels()
        fr = wf.get_framerate()
        wf.close()
        total = (sz - 44) // (sw * ch)
        return int(total / fr * 1000)
    except:
        return 0

# ============================================================
# 全局状态
# ============================================================
is_recording = False
is_playing = False
rec_elapsed_ms = 0
play_elapsed_ms = 0
play_duration_ms = 0
app_should_exit = False
rec_file_list = []

# ============================================================
# 音频引擎（参照基础测试代码的 PyAudio 生命周期）
# ============================================================
_p = None
_stream = None
_chunk = 0
_rec_frames = []
_rec_frame_count = 0

# 播放专用
_wf = None
_play_should_stop = False

def _audio_open_input(rate=44100):
    """打开音频输入流（参照基础测试代码 record_audio）"""
    global _p, _stream, _chunk, _rec_frames, _rec_frame_count
    _chunk = int(rate / 25)
    _rec_frames = []
    _rec_frame_count = 0
    _p = PyAudio()
    _stream = _p.open(
        format=paInt16, channels=1, rate=rate,
        input=True, frames_per_buffer=_chunk,
    )

def _audio_open_output(wf):
    """打开音频输出流（参照基础测试代码 play_audio）"""
    global _p, _stream, _chunk, _wf
    _wf = wf
    framerate = wf.get_framerate()
    _chunk = int(framerate / 25)
    _p = PyAudio()
    _stream = _p.open(
        format=_p.get_format_from_width(wf.get_sampwidth()),
        channels=wf.get_channels(),
        rate=framerate,
        output=True, frames_per_buffer=_chunk,
    )
    _stream.volume(vol=80)

def _audio_close():
    """关闭当前音频流（参照基础测试代码 finally 块）"""
    global _p, _stream, _wf
    try:
        if _stream:
            _stream.stop_stream()
            _stream.close()
    except:
        pass
    _stream = None
    try:
        if _p:
            _p.terminate()
    except:
        pass
    _p = None
    _chunk = None  # 不赋值，让下次重新计算
    try:
        if _wf:
            _wf.close()
    except:
        pass
    _wf = None

# ============================================================
# 录音操作
# ============================================================
def rec_start():
    global is_recording, rec_elapsed_ms
    _audio_close()
    _audio_open_input(44100)
    is_recording = True
    rec_elapsed_ms = 0
    print("[录音机] 开始录音")

def rec_stop():
    global is_recording, _rec_frame_count
    if not is_recording:
        return
    is_recording = False

    ensure_dir()
    files = scan_files()
    idx = len(files) + 1
    filename = AUDIO_DIR + "/rec_" + ("%03d" % idx) + ".wav"

    try:
        wf = wave.open(filename, 'wb')
        wf.set_channels(1)
        wf.set_sampwidth(_p.get_sample_size(paInt16))
        wf.set_framerate(44100)
        wf.write_frames(b''.join(_rec_frames))
        wf.close()
        dur = rec_elapsed_ms // 1000
        print("[录音机] 已保存: " + filename + " (" + str(dur) + "s)")
    except Exception as e:
        print("[录音机] 保存失败: " + str(e))

    _audio_close()
    _rec_frame_count = 0

def rec_update():
    """每帧采集一个音频块"""
    global rec_elapsed_ms, _rec_frame_count, is_recording
    if not is_recording or _stream is None:
        return
    try:
        data = _stream.read()
        _rec_frames.append(data)
        _rec_frame_count += 1
        rec_elapsed_ms = int(_rec_frame_count * _chunk / 44100 * 1000)
        if rec_elapsed_ms >= MAX_REC_SEC * 1000:
            rec_stop()
    except:
        pass

# ============================================================
# 播放操作
# ============================================================
def play_start(filepath):
    global is_playing, play_elapsed_ms, play_duration_ms, _play_should_stop

    play_do_stop()
    _audio_close()

    try:
        wf = wave.open(filepath, 'rb')
        play_duration_ms = get_wav_duration_ms(filepath)
        play_elapsed_ms = 0
        _play_should_stop = False

        _audio_open_output(wf)
        is_playing = True
        print("[录音机] 播放: " + filepath)
    except Exception as e:
        print("[录音机] 播放失败: " + str(e))
        try:
            wf.close()
        except:
            pass
        _audio_close()

def play_request_stop():
    global _play_should_stop, is_playing
    if is_playing:
        _play_should_stop = True
        is_playing = False

def play_do_stop():
    global is_playing, _play_should_stop
    if not _play_should_stop and not is_playing:
        # 没有活跃播放且没有待停止请求
        return
    _play_should_stop = False
    is_playing = False
    _audio_close()

def play_update():
    """每帧写入多个音频块，保持 DMA 缓冲区充满"""
    global play_elapsed_ms, is_playing, _play_should_stop

    if _play_should_stop:
        play_do_stop()
        return
    if not is_playing or _stream is None:
        return

    # 每帧写入 4 个块，防止缓冲区欠载导致卡顿
    for _ in range(4):
        if _play_should_stop:
            break
        try:
            data = _wf.read_frames(_chunk)
            if data:
                _stream.write(data)
                play_elapsed_ms = play_elapsed_ms + int(_chunk / _wf.get_framerate() * 1000)
            else:
                print("[录音机] 播放完毕")
                play_do_stop()
                break
        except:
            play_do_stop()
            break

# ============================================================
# UI 布局
# ============================================================
EXIT_X, EXIT_Y, EXIT_W, EXIT_H = 682, 14, 104, 36
BTN_REC_X, BTN_REC_Y   = 160, 138
BTN_STOP_X, BTN_STOP_Y = 400, 138
BTN_PLAY_X, BTN_PLAY_Y = 640, 138
BTN_R = 36
LIST_X, LIST_Y, LIST_W, LIST_H = 30, 225, 740, 235
ITEM_H = 38
LIST_SCROLL = 0

# ============================================================
# 触摸
# ============================================================
_touch_pressed = False
_debounce_until = 0

def in_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx + rw and ry <= py <= ry + rh

def in_circle(px, py, cx, cy, r):
    return (px - cx) ** 2 + (py - cy) ** 2 <= r ** 2

def handle_touch(points):
    global app_should_exit, _touch_pressed, _debounce_until
    global is_recording, is_playing

    now = time.ticks_ms()
    if not points:
        _touch_pressed = False
        return
    if time.ticks_diff(_debounce_until, now) > 0:
        return

    pt = points[0]
    x, y = pt.x, pt.y
    is_down = not _touch_pressed
    _touch_pressed = True
    if not is_down:
        return

    # 退出
    if in_rect(x, y, EXIT_X - 8, EXIT_Y - 8, EXIT_W + 16, EXIT_H + 16):
        if is_recording:
            rec_stop()
        if is_playing:
            play_request_stop()
        app_should_exit = True
        _debounce_until = time.ticks_add(now, 400)
        return

    # 录音按钮
    if in_circle(x, y, BTN_REC_X, BTN_REC_Y, BTN_R + 8):
        if is_playing:
            play_request_stop()
        if is_recording:
            rec_stop()
        else:
            rec_start()
        _debounce_until = time.ticks_add(now, 400)
        return

    # 停止按钮
    if in_circle(x, y, BTN_STOP_X, BTN_STOP_Y, BTN_R + 8):
        if is_recording:
            rec_stop()
        if is_playing:
            play_request_stop()
        _debounce_until = time.ticks_add(now, 400)
        return

    # 文件列表
    if in_rect(x, y, LIST_X, LIST_Y, LIST_W, LIST_H):
        files = scan_files()
        idx = (y - LIST_Y - 10) // ITEM_H
        if 0 <= idx < len(files):
            if is_playing:
                play_request_stop()
            else:
                play_start(AUDIO_DIR + "/" + files[idx])
            _debounce_until = time.ticks_add(now, 400)
        return

# ============================================================
# 绘制
# ============================================================
def _draw_circle_btn(img, cx, cy, r, label, color_bg, is_active):
    img.draw_circle(cx, cy + 2, r + 1, color=(30, 30, 40), thickness=2, fill=True)
    c = color_bg if is_active else (70, 74, 90)
    img.draw_circle(cx, cy, r, c, thickness=3, fill=True)
    hl = (min(c[0] + 30, 255), min(c[1] + 30, 255), min(c[2] + 30, 255))
    img.draw_circle(cx, cy, r, hl, thickness=1, fill=False)
    lw = len(label) * 10
    img.draw_string_advanced(cx - lw // 2, cy + r + 10, 14, label, color=(200, 205, 220))

def draw_ui(img):
    img.clear()
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, color=(20, 22, 35), fill=True)

    # 标题栏
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, 50, color=(30, 33, 48), fill=True)
    img.draw_string_advanced(20, 12, 20, "录音机", color=(255, 255, 255))

    # 退出按钮
    img.draw_rectangle(EXIT_X, EXIT_Y, EXIT_W, EXIT_H,
                       color=(220, 60, 50), fill=True)
    img.draw_string_advanced(EXIT_X + 21, EXIT_Y + 8, 16, "退出", color=(255, 255, 255))

    # 状态文字
    status_y = 80
    if is_recording:
        sec = rec_elapsed_ms // 1000
        ms = (rec_elapsed_ms % 1000) // 100
        txt = "● 录音中...  %02d.%ds / %ds" % (sec, ms, MAX_REC_SEC)
        clr = (255, 80, 60)
    elif is_playing:
        sec = play_elapsed_ms // 1000
        tot = play_duration_ms // 1000
        txt = "▶ 播放中...  %02ds / %02ds" % (sec, tot)
        clr = (60, 200, 160)
    else:
        txt = "准备录音"
        clr = (160, 165, 180)
    txt_w = len(txt) * 14
    img.draw_string_advanced((800 - txt_w) // 2, status_y, 14, txt, color=clr)

    # 进度条
    bar_x, bar_y, bar_w, bar_h = 80, 112, 640, 8
    img.draw_rectangle(bar_x, bar_y, bar_w, bar_h, color=(50, 54, 72), fill=True)
    if is_recording:
        fill = int(bar_w * rec_elapsed_ms / (MAX_REC_SEC * 1000))
        fc = (255, 80, 60)
    elif is_playing and play_duration_ms > 0:
        fill = int(bar_w * play_elapsed_ms / play_duration_ms)
        fc = (60, 200, 160)
    else:
        fill = 0
        fc = (80, 85, 105)
    if fill > 0:
        img.draw_rectangle(bar_x, bar_y, min(fill, bar_w), bar_h, color=fc, fill=True)

    # 圆形按钮
    _draw_circle_btn(img, BTN_REC_X, BTN_REC_Y, BTN_R,
                     "停止录音" if is_recording else "开始录音",
                     (255, 70, 55) if not is_recording else (180, 50, 40), True)
    _draw_circle_btn(img, BTN_STOP_X, BTN_STOP_Y, BTN_R,
                     "停止", (100, 105, 130), is_recording or is_playing)
    files = scan_files()
    _draw_circle_btn(img, BTN_PLAY_X, BTN_PLAY_Y, BTN_R,
                     "暂停" if is_playing else "播放",
                     (60, 200, 160), len(files) > 0 and not is_recording)

    # 文件列表
    img.draw_rectangle(LIST_X, LIST_Y, LIST_W, LIST_H,
                       color=(28, 31, 46), fill=True)
    img.draw_rectangle(LIST_X, LIST_Y, LIST_W, LIST_H,
                       color=(50, 54, 72), thickness=1, fill=False)

    list_top = LIST_Y + 6
    visible = (LIST_H - 16) // ITEM_H
    if len(files) == 0:
        img.draw_string_advanced(LIST_X + 20, LIST_Y + 40, 16, "暂无录音文件",
                                 color=(120, 125, 140))
    else:
        for i in range(min(visible, len(files))):
            fname = files[i]
            item_y = list_top + i * ITEM_H
            bg_c = (36, 39, 55) if i % 2 == 0 else (30, 33, 48)
            img.draw_rectangle(LIST_X + 4, item_y, LIST_W - 8, ITEM_H - 2,
                               color=bg_c, fill=True)
            short = fname if len(fname) <= 30 else fname[:28] + ".."
            img.draw_string_advanced(LIST_X + 14, item_y + 8, 14, short,
                                     color=(210, 215, 225))
            dur_ms = get_wav_duration_ms(AUDIO_DIR + "/" + fname)
            img.draw_string_advanced(LIST_X + LIST_W - 80, item_y + 8, 13,
                                     str(dur_ms // 1000) + "s", color=(140, 145, 160))
            img.draw_string_advanced(LIST_X + LIST_W - 40, item_y + 8, 14, "▶",
                                     color=(60, 200, 160))

# ============================================================
# 初始化 / 清理
# ============================================================
def init_app():
    global app_should_exit, is_recording, is_playing
    global rec_elapsed_ms, play_elapsed_ms, play_duration_ms
    global _touch_pressed, _debounce_until

    is_recording = False
    is_playing = False
    rec_elapsed_ms = 0
    play_elapsed_ms = 0
    play_duration_ms = 0
    _touch_pressed = False
    _debounce_until = 0
    app_should_exit = False

    init_amp()
    ensure_dir()

    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    MediaManager.init()

def deinit_app():
    if is_recording:
        rec_stop()
    if is_playing:
        play_do_stop()
    _audio_close()
    deinit_amp()
    try:
        Display.deinit()
    except:
        pass
    time.sleep_ms(60)
    try:
        MediaManager.deinit()
    except:
        pass

# ============================================================
# 主循环
# ============================================================
def main():
    global rec_file_list, app_should_exit

    init_app()
    tp = TOUCH(0)

    rec_file_list = scan_files()
    print("[录音机] 启动")
    print("  目录: " + AUDIO_DIR + ", 已有 " + str(len(rec_file_list)) + " 个录音")

    try:
        while True:
            os.exitpoint()

            points = tp.read(5)
            handle_touch(points)

            rec_update()
            play_update()

            if app_should_exit:
                print("[录音机] 退出")
                break

            img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
            draw_ui(img)
            Display.show_image(img)

            time.sleep_ms(30)

    except KeyboardInterrupt:
        print("[录音机] 用户停止")
    except BaseException as e:
        print("[录音机] 异常: " + str(e))
        import sys
        sys.print_exception(e)
    finally:
        deinit_app()

if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()
