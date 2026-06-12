# 触摸屏音乐播放器（集成WAV音频播放） - 立创·庐山派-K230-CanMV
# 功能：WAV音频播放/暂停、进度拖拽/快进快退、音量调节、切歌、音乐目录显示
# 动画：旋转黑胶唱片、频谱光环、均衡器跳动、浮动音符粒子

import time, os, gc, sys, urandom, math, image
from media.display import *
from media.media import *
from media.pyaudio import *
import media.wave as wave
from machine import TOUCH
from machine import Pin
from machine import FPIOA

# ============================================================
# 音频硬件初始化（使能功放芯片）
# ============================================================
fpioa = None
HT_CTRL = None

# ============================================================
# 显示初始化
# ============================================================
DISPLAY_MODE = "LCD"
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480

img = None
tp = None


def init_player_hardware():
    """播放器界面启动时再初始化硬件，便于从 touch.py 切入切出。"""
    global DISPLAY_WIDTH, DISPLAY_HEIGHT, img, tp, fpioa, HT_CTRL

    fpioa = FPIOA()
    fpioa.set_function(10, FPIOA.GPIO10)
    HT_CTRL = Pin(10, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    HT_CTRL.high()  # 拉高使能音频功放

    if DISPLAY_MODE == "VIRT":
        DISPLAY_WIDTH = ALIGN_UP(1920, 16)
        DISPLAY_HEIGHT = 1080
        Display.init(Display.VIRT, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, fps=60)
    elif DISPLAY_MODE == "LCD":
        DISPLAY_WIDTH = 800
        DISPLAY_HEIGHT = 480
        Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    elif DISPLAY_MODE == "HDMI":
        DISPLAY_WIDTH = 1920
        DISPLAY_HEIGHT = 1080
        Display.init(Display.LT9611, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)

    MediaManager.init()
    img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
    tp = TOUCH(0)

# ============================================================
# 音乐文件扫描
# ============================================================
MUSIC_DIR = "/data"

def scan_music_files():
    """扫描音乐目录，返回.wav文件列表"""
    files = []
    try:
        for f in os.listdir(MUSIC_DIR):
            if f.lower().endswith('.wav'):
                files.append(f)
        files.sort()
    except OSError:
        pass
    return files

def filename_to_title(filename):
    """将文件名转为显示标题"""
    name = filename.rsplit('.', 1)[0]  # 去掉扩展名
    name = name.replace('_', ' ').replace('-', ' ')  # 替换分隔符
    # 去除首尾空格
    name = name.strip()
    return name if name else filename

music_files = scan_music_files()
music_count = len(music_files)

# ============================================================
# 颜色定义 —— 精致深色风格
# ============================================================
C_BG_TOP      = (18, 38, 70)
C_BG_BOT      = (12, 130, 120)
C_PANEL       = (21, 35, 65)
C_PANEL_ITEM  = (28, 48, 82)
C_PANEL_ACTIVE = (34, 214, 184)
C_PANEL_SOFT  = (33, 54, 88)
C_TEXT        = (244, 250, 255)
C_SUBTEXT     = (156, 183, 205)
C_MUTED       = (92, 118, 145)
C_ACCENT      = (255, 111, 96)
C_ACCENT2     = (38, 224, 190)
C_PROGRESS_BG = (45, 70, 100)
C_PROGRESS_FG = (38, 224, 190)
C_WHITE       = (255, 255, 255)
C_VINYL_BASE  = (15, 18, 28)
C_GROOVE      = (48, 56, 70)
C_LABEL       = (255, 104, 88)
C_LABEL_INNER = (255, 168, 93)
C_HUB         = (20, 28, 38)
C_HUB_TOP     = (96, 110, 125)
C_SHADOW      = (7, 18, 32)
C_BTN_PREV    = (60, 82, 145)
C_BTN_NEXT    = (60, 82, 145)
C_BTN_PLAY    = (255, 111, 96)
C_BTN_PAUSE   = (38, 190, 168)

# ============================================================
# 布局参数
# ============================================================
# 左侧歌曲列表面板
LIST_X      = 18
LIST_Y      = 22
LIST_W      = 190
LIST_H      = 436
LIST_ITEM_H = 44
LIST_MAX_VISIBLE = 10

# 主内容区域起始X
CONTENT_X   = 232
CONTENT_W   = 542
CONTENT_CX  = CONTENT_X + CONTENT_W // 2  # ~485

# 唱片
RECORD_CX = 430
RECORD_CY = 214
RECORD_R  = 96
LABEL_R   = 32
HUB_R     = 7

# 均衡器
EQ_Y       = 332
EQ_BAR_W   = 10
EQ_GAP     = 6
EQ_COUNT   = 20
EQ_MAX_H   = 34
EQ_START_X = CONTENT_X + 24

# 音量（竖向滑杆）
VOL_X      = 724
VOL_Y      = 156
VOL_W      = 8
VOL_H      = 148

# 进度条
PROGRESS_Y = 362
PROGRESS_X = CONTENT_X + 24
PROGRESS_W = CONTENT_W - 132
PROGRESS_H = 8

# 按钮（加大间距，杜绝重叠）
BTN_Y      = 428
BTN_R      = 25
BTN_PLAY_X = CONTENT_CX
BTN_PREV_X = CONTENT_CX - 96
BTN_NEXT_X = CONTENT_CX + 96

# 主题按钮
THEME_X = 662
THEME_Y = 78
THEME_W = 86
THEME_H = 30

# 退出按钮
EXIT_X = 662
EXIT_Y = 32
EXIT_W = 86
EXIT_H = 30

# 顶部信息
TITLE_Y  = 28
ARTIST_Y = 68

PARTICLE_COUNT = 8

# ============================================================
# 全局状态
# ============================================================
is_playing = True
is_dark_theme = True
player_should_exit = False
rotation_angle = 0.0
progress = 0.0
volume = 70
song_index = 0
list_scroll_offset = 0   # 歌曲列表滚动偏移

# 均衡器状态
eq_heights = [0.0] * EQ_COUNT
eq_targets = [0.0] * EQ_COUNT
eq_phase   = [0.0] * EQ_COUNT

# 粒子
particles = []
for _ in range(PARTICLE_COUNT):
    particles.append({
        'x': urandom.getrandbits(10) % DISPLAY_WIDTH,
        'y': urandom.getrandbits(9) % DISPLAY_HEIGHT,
        'vx': (urandom.getrandbits(8) - 128) / 80.0,
        'vy': -(urandom.getrandbits(7) / 40.0 + 0.3),
        'life': urandom.getrandbits(8) / 255.0,
        'note': ["♪", "♫", "♬", "♩"][urandom.getrandbits(2) % 4],
    })

# 触摸消抖
touch_was_active = False
debounce_until = 0
BTN_DEBOUNCE_MS = 380

# 时间
last_time = time.ticks_ms()
last_eq_update = time.ticks_ms()

# ============================================================
# 音频状态
# ============================================================
audio_wf = None
audio_p = None
audio_stream = None
audio_filepath = ""
audio_chunk_size = 0
audio_total_frames = 0
audio_current_frame = 0
audio_framerate = 0
audio_channels = 0
audio_sampwidth = 0

# ============================================================
# 音频函数
# ============================================================

def _wav_total_frames(filepath, sampwidth, channels):
    """通过文件大小估算WAV总帧数（MicroPython wave模块无get_nframes）"""
    try:
        file_size = os.stat(filepath)[6]  # st_size
        # 标准WAV头44字节，但可能有额外chunk，按数据区估算
        # 跳过前44字节头部，剩余字节 / 每帧字节数
        data_size = file_size - 44
        if data_size > 0:
            return data_size // (sampwidth * channels)
    except:
        pass
    return 0


def audio_open(filename):
    """打开WAV文件并初始化音频输出流"""
    global audio_wf, audio_p, audio_stream
    global audio_chunk_size, audio_total_frames, audio_current_frame
    global audio_framerate, audio_channels, audio_sampwidth
    global audio_filepath

    audio_close()

    audio_filepath = MUSIC_DIR + "/" + filename
    audio_wf = wave.open(audio_filepath, 'rb')
    audio_framerate = audio_wf.get_framerate()
    audio_channels = audio_wf.get_channels()
    audio_sampwidth = audio_wf.get_sampwidth()
    audio_chunk_size = int(audio_framerate / 25)
    audio_current_frame = 0

    # 通过文件大小计算总帧数
    audio_total_frames = _wav_total_frames(
        audio_filepath, audio_sampwidth, audio_channels
    )

    audio_p = PyAudio()

    audio_stream = audio_p.open(
        format=audio_p.get_format_from_width(audio_sampwidth),
        channels=audio_channels,
        rate=audio_framerate,
        output=True,
        frames_per_buffer=audio_chunk_size
    )

    # 设置硬件音量
    audio_stream.volume(vol=volume)

    # 预填充音频缓冲区（确保DMA有数据开始播放）
    for _ in range(4):
        pre_data = audio_wf.read_frames(audio_chunk_size)
        if pre_data:
            audio_stream.write(pre_data)
            audio_current_frame = min(
                audio_current_frame + audio_chunk_size,
                audio_total_frames
            )


def audio_play_chunk():
    """播放多个音频块，保持缓冲区充满，返回 (还有数据, 当前帧位置)"""
    global audio_current_frame

    if not audio_wf or not audio_stream:
        return (False, 0)

    # 每帧写入多个chunk，防止显示渲染导致缓冲区欠载
    chunks_per_frame = 3
    has_data = False
    for _ in range(chunks_per_frame):
        data = audio_wf.read_frames(audio_chunk_size)
        if data:
            audio_stream.write(data)
            audio_current_frame = min(
                audio_current_frame + audio_chunk_size,
                audio_total_frames
            )
            has_data = True
        else:
            break

    if has_data:
        return (True, audio_current_frame)
    return (False, audio_total_frames)


def audio_seek(ratio):
    """跳转到指定比例位置 (0.0 ~ 1.0)。
    MicroPython wave模块无setpos，通过关闭重开+跳过帧实现。"""
    global audio_current_frame, audio_wf

    if not audio_wf or audio_total_frames <= 0:
        return

    target = int(audio_total_frames * ratio)
    if target >= audio_total_frames:
        target = audio_total_frames - audio_chunk_size
    if target < 0:
        target = 0

    # 关闭当前文件
    audio_wf.close()

    # 重新打开并跳过目标帧数
    audio_wf = wave.open(audio_filepath, 'rb')
    skipped = 0
    skip_chunk = audio_chunk_size
    while skipped < target:
        to_skip = min(skip_chunk, target - skipped)
        discarded = audio_wf.read_frames(to_skip)
        if not discarded:
            break
        skipped += to_skip

    audio_current_frame = target


def audio_close():
    """关闭所有音频资源"""
    global audio_wf, audio_p, audio_stream

    try:
        if audio_stream:
            audio_stream.stop_stream()
            audio_stream.close()
    except:
        pass
    try:
        if audio_p:
            audio_p.terminate()
    except:
        pass
    try:
        if audio_wf:
            audio_wf.close()
    except:
        pass

    audio_wf = None
    audio_p = None
    audio_stream = None

# ============================================================
# 辅助函数
# ============================================================

def hsv_to_rgb(h, s=1.0, v=1.0):
    if s == 0.0:
        return (int(v*255), int(v*255), int(v*255))
    h = h % 1.0
    i = int(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:   r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    elif i == 5: r, g, b = v, p, q
    return (int(r*255), int(g*255), int(b*255))


def is_inside_circle(px, py, cx, cy, r):
    return (px - cx) * (px - cx) + (py - cy) * (py - cy) <= r * r


def is_inside_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx + rw and ry <= py <= ry + rh


def draw_text_centered(x, y, w, text, size, color):
    """在指定宽度内居中绘制文字"""
    text_w = len(text) * size
    offset = (w - text_w) // 2
    if offset < 0:
        offset = 0
    img.draw_string_advanced(x + offset, y, size, text, color=color)


def draw_text_clipped(x, y, max_w, text, size, color):
    """绘制文字，超出宽度则截断加.."""
    chars_to_fit = max_w // size
    if len(text) > chars_to_fit:
        text = text[:chars_to_fit - 2] + ".."
    img.draw_string_advanced(x, y, size, text, color=color)


def lighten(color, amount):
    return (
        min(color[0] + amount, 255),
        min(color[1] + amount, 255),
        min(color[2] + amount, 255),
    )


def darken(color, amount):
    return (
        max(color[0] - amount, 0),
        max(color[1] - amount, 0),
        max(color[2] - amount, 0),
    )


def draw_round_rect(x, y, w, h, r, color, fill=True, thickness=1):
    """用矩形和圆形拼出圆角矩形，兼容 CanMV 基础绘图接口。"""
    if fill:
        img.draw_rectangle(x + r, y, w - 2 * r, h, color=color, fill=True)
        img.draw_rectangle(x, y + r, w, h - 2 * r, color=color, fill=True)
        img.draw_circle(x + r, y + r, r, color=color, thickness=1, fill=True)
        img.draw_circle(x + w - r, y + r, r, color=color, thickness=1, fill=True)
        img.draw_circle(x + r, y + h - r, r, color=color, thickness=1, fill=True)
        img.draw_circle(x + w - r, y + h - r, r, color=color, thickness=1, fill=True)
    else:
        img.draw_line(x + r, y, x + w - r, y, color=color, thickness=thickness)
        img.draw_line(x + r, y + h, x + w - r, y + h, color=color, thickness=thickness)
        img.draw_line(x, y + r, x, y + h - r, color=color, thickness=thickness)
        img.draw_line(x + w, y + r, x + w, y + h - r, color=color, thickness=thickness)


def draw_pill(x, y, w, h, color):
    if w >= h:
        r = h // 2
        img.draw_rectangle(x + r, y, w - 2 * r, h, color=color, fill=True)
        img.draw_circle(x + r, y + r, r, color=color, thickness=1, fill=True)
        img.draw_circle(x + w - r, y + r, r, color=color, thickness=1, fill=True)
    else:
        r = w // 2
        img.draw_rectangle(x, y + r, w, h - 2 * r, color=color, fill=True)
        img.draw_circle(x + r, y + r, r, color=color, thickness=1, fill=True)
        img.draw_circle(x + r, y + h - r, r, color=color, thickness=1, fill=True)


def apply_theme(dark=True):
    """切换黑色/白色主题使用的颜色。"""
    global C_BG_TOP, C_BG_BOT, C_PANEL, C_PANEL_ITEM, C_PANEL_ACTIVE
    global C_PANEL_SOFT, C_TEXT, C_SUBTEXT, C_MUTED, C_ACCENT, C_ACCENT2
    global C_PROGRESS_BG, C_PROGRESS_FG, C_VINYL_BASE, C_GROOVE
    global C_LABEL, C_LABEL_INNER, C_HUB, C_HUB_TOP, C_SHADOW
    global C_BTN_PREV, C_BTN_NEXT, C_BTN_PLAY, C_BTN_PAUSE

    if dark:
        C_BG_TOP      = (18, 38, 70)
        C_BG_BOT      = (12, 130, 120)
        C_PANEL       = (21, 35, 65)
        C_PANEL_ITEM  = (28, 48, 82)
        C_PANEL_ACTIVE = (34, 214, 184)
        C_PANEL_SOFT  = (33, 54, 88)
        C_TEXT        = (244, 250, 255)
        C_SUBTEXT     = (156, 183, 205)
        C_MUTED       = (92, 118, 145)
        C_ACCENT      = (255, 111, 96)
        C_ACCENT2     = (38, 224, 190)
        C_PROGRESS_BG = (45, 70, 100)
        C_PROGRESS_FG = (38, 224, 190)
        C_VINYL_BASE  = (15, 18, 28)
        C_GROOVE      = (48, 56, 70)
        C_LABEL       = (255, 104, 88)
        C_LABEL_INNER = (255, 168, 93)
        C_HUB         = (20, 28, 38)
        C_HUB_TOP     = (96, 110, 125)
        C_SHADOW      = (7, 18, 32)
        C_BTN_PREV    = (60, 82, 145)
        C_BTN_NEXT    = (60, 82, 145)
        C_BTN_PLAY    = (255, 111, 96)
        C_BTN_PAUSE   = (38, 190, 168)
    else:
        C_BG_TOP      = (238, 242, 248)
        C_BG_BOT      = (213, 235, 238)
        C_PANEL       = (250, 252, 255)
        C_PANEL_ITEM  = (235, 241, 248)
        C_PANEL_ACTIVE = (33, 181, 160)
        C_PANEL_SOFT  = (226, 235, 245)
        C_TEXT        = (26, 38, 55)
        C_SUBTEXT     = (88, 108, 130)
        C_MUTED       = (132, 150, 168)
        C_ACCENT      = (240, 92, 80)
        C_ACCENT2     = (0, 170, 150)
        C_PROGRESS_BG = (206, 218, 231)
        C_PROGRESS_FG = (0, 170, 150)
        C_VINYL_BASE  = (28, 31, 40)
        C_GROOVE      = (70, 76, 90)
        C_LABEL       = (240, 92, 80)
        C_LABEL_INNER = (255, 188, 96)
        C_HUB         = (70, 82, 95)
        C_HUB_TOP     = (150, 162, 176)
        C_SHADOW      = (174, 188, 205)
        C_BTN_PREV    = (91, 118, 190)
        C_BTN_NEXT    = (91, 118, 190)
        C_BTN_PLAY    = (240, 92, 80)
        C_BTN_PAUSE   = (0, 170, 150)


def draw_theme_button():
    label = "白色" if is_dark_theme else "黑色"
    bg = (242, 247, 252) if is_dark_theme else (26, 38, 55)
    fg = (26, 38, 55) if is_dark_theme else (246, 250, 255)
    knob_x = THEME_X + 58 if is_dark_theme else THEME_X + 19
    draw_pill(THEME_X, THEME_Y, THEME_W, THEME_H, bg)
    img.draw_circle(knob_x, THEME_Y + THEME_H // 2, 11, color=C_ACCENT2, thickness=1, fill=True)
    img.draw_string_advanced(THEME_X + 12, THEME_Y + 8, 12, label, color=fg)


def draw_exit_button():
    draw_pill(EXIT_X, EXIT_Y, EXIT_W, EXIT_H, C_ACCENT)
    img.draw_string_advanced(EXIT_X + 20, EXIT_Y + 7, 14, "退出", color=C_WHITE)

# ============================================================
# 绘制函数
# ============================================================

def draw_background():
    """蓝绿渐变背景 + 柔和装饰层"""
    img.clear()
    for i in range(DISPLAY_HEIGHT):
        ratio = i / DISPLAY_HEIGHT
        r = int(C_BG_TOP[0] + (C_BG_BOT[0] - C_BG_TOP[0]) * ratio)
        g = int(C_BG_TOP[1] + (C_BG_BOT[1] - C_BG_TOP[1]) * ratio)
        b = int(C_BG_TOP[2] + (C_BG_BOT[2] - C_BG_TOP[2]) * ratio)
        img.draw_line(0, i, DISPLAY_WIDTH, i, color=(r, g, b))

    # 大面积柔和色块，避免纯色背景显得生硬。
    if is_dark_theme:
        decor1, decor2, decor3, decor4 = (33, 78, 130), (41, 94, 143), (16, 158, 130), (9, 106, 116)
        main_panel, main_border = (16, 32, 58), (70, 110, 145)
    else:
        decor1, decor2, decor3, decor4 = (221, 232, 246), (231, 241, 250), (200, 234, 229), (194, 226, 230)
        main_panel, main_border = (248, 251, 255), (196, 212, 228)

    img.draw_circle(694, 56, 122, color=decor1, thickness=1, fill=True)
    img.draw_circle(704, 64, 84, color=decor2, thickness=1, fill=True)
    img.draw_circle(116, 432, 86, color=decor3, thickness=1, fill=True)
    img.draw_circle(370, 545, 160, color=decor4, thickness=1, fill=True)

    # 顶层半透明感用深色卡片统一收束。
    draw_round_rect(CONTENT_X, 22, CONTENT_W, 436, 20, main_panel, fill=True)
    draw_round_rect(CONTENT_X, 22, CONTENT_W, 436, 20, main_border, fill=False, thickness=1)


def draw_song_list_panel():
    """左侧歌曲列表面板"""
    list_shadow = (8, 24, 43) if is_dark_theme else (188, 204, 220)
    list_border = (68, 94, 125) if is_dark_theme else (198, 214, 230)
    count_bg = (37, 63, 95) if is_dark_theme else (226, 238, 247)
    item_bg = (24, 42, 70) if is_dark_theme else (238, 245, 251)
    active_bg = (33, 67, 91) if is_dark_theme else (219, 242, 239)
    draw_round_rect(LIST_X + 3, LIST_Y + 4, LIST_W, LIST_H, 18, list_shadow, fill=True)
    draw_round_rect(LIST_X, LIST_Y, LIST_W, LIST_H, 18, C_PANEL, fill=True)
    draw_round_rect(LIST_X, LIST_Y, LIST_W, LIST_H, 18, list_border, fill=False, thickness=1)

    # 标题
    img.draw_string_advanced(LIST_X + 16, LIST_Y + 14, 20, "音乐列表", color=C_TEXT)
    dir_label = MUSIC_DIR
    img.draw_string_advanced(LIST_X + 18, LIST_Y + 42, 12, dir_label, color=C_SUBTEXT)
    draw_pill(LIST_X + LIST_W - 52, LIST_Y + 18, 34, 18, count_bg)
    img.draw_string_advanced(LIST_X + LIST_W - 45, LIST_Y + 20, 11, str(music_count), color=C_ACCENT2)

    if music_count == 0:
        img.draw_string_advanced(LIST_X + 22, LIST_Y + 92, 16, "无音乐文件", color=C_TEXT)
        img.draw_string_advanced(LIST_X + 22, LIST_Y + 118, 13, "请放入 /data/", color=C_SUBTEXT)
        img.draw_string_advanced(LIST_X + 22, LIST_Y + 138, 13, "中的 .wav 文件", color=C_SUBTEXT)
        return

    # 列表可见范围
    list_top = LIST_Y + 70
    list_bottom = LIST_Y + LIST_H - 16
    visible_count = (list_bottom - list_top) // LIST_ITEM_H

    # 自动滚动使当前歌曲可见
    global list_scroll_offset
    if song_index < list_scroll_offset:
        list_scroll_offset = song_index
    elif song_index >= list_scroll_offset + visible_count:
        list_scroll_offset = song_index - visible_count + 1
    if list_scroll_offset < 0:
        list_scroll_offset = 0
    max_offset = max(0, music_count - visible_count)
    if list_scroll_offset > max_offset:
        list_scroll_offset = max_offset

    # 绘制列表项
    for i in range(visible_count):
        fi = list_scroll_offset + i
        if fi >= music_count:
            break

        item_y = list_top + i * LIST_ITEM_H
        is_current = (fi == song_index)

        # 选中高亮
        if is_current:
            draw_round_rect(LIST_X + 10, item_y + 3, LIST_W - 20, LIST_ITEM_H - 6,
                            10, active_bg, fill=True)
            img.draw_rectangle(LIST_X + 10, item_y + 12, 4, LIST_ITEM_H - 24,
                               color=C_ACCENT2, fill=True)
        else:
            draw_round_rect(LIST_X + 12, item_y + 4, LIST_W - 24, LIST_ITEM_H - 8,
                            9, item_bg, fill=True)

        # 序号 + 文件名
        num_text = f"{fi+1:02d}"
        img.draw_string_advanced(LIST_X + 22, item_y + 10, 14, num_text,
                                 color=C_ACCENT2 if is_current else C_MUTED)

        title = filename_to_title(music_files[fi])
        draw_text_clipped(LIST_X + 54, item_y + 9, LIST_W - 72, title, 14,
                          C_TEXT if is_current else C_SUBTEXT)

    # 滚动条指示
    if music_count > visible_count:
        bar_h = int((visible_count / music_count) * (visible_count * LIST_ITEM_H))
        bar_y = list_top + int((list_scroll_offset / music_count) * (visible_count * LIST_ITEM_H))
        draw_pill(LIST_X + LIST_W - 8, bar_y, 4, max(18, bar_h), (62, 97, 128))


def draw_top_info():
    """顶部歌曲信息"""
    if music_count == 0:
        draw_text_centered(CONTENT_X, TITLE_Y + 20, CONTENT_W, "请放入 WAV 音乐文件到 /data/ 目录", 16, C_SUBTEXT)
        return

    filename = music_files[song_index]
    title = filename_to_title(filename)
    img.draw_string_advanced(CONTENT_X + 24, TITLE_Y, 13, "NOW PLAYING", color=C_ACCENT2)
    draw_text_clipped(CONTENT_X + 24, TITLE_Y + 24, CONTENT_W - 170, title, 32, C_TEXT)

    # 文件信息
    if audio_framerate > 0:
        khz = audio_framerate / 1000.0
        ch = "立体声" if audio_channels >= 2 else "单声道"
        bits = audio_sampwidth * 8
        info = f"{khz:.1f}kHz | {ch} | {bits}bit | WAV"
    else:
        info = filename
    img.draw_string_advanced(CONTENT_X + 24, ARTIST_Y + 18, 15, info, color=C_SUBTEXT)

    # 右侧状态标签
    if is_playing:
        tag_text = "播放中"
        tag_color = C_ACCENT
    else:
        tag_text = "已暂停"
        tag_color = C_ACCENT2

    tag_w = 94
    tag_h = 30
    tag_x = CONTENT_X + CONTENT_W - tag_w - 24
    tag_y = TITLE_Y + 5
    draw_pill(tag_x, tag_y, tag_w, tag_h, tag_color)
    draw_text_centered(tag_x, tag_y + 6, tag_w, tag_text, 15, C_WHITE)

    # 歌曲序号
    idx_text = f"{song_index + 1} / {music_count}"
    img.draw_string_advanced(tag_x + 28, tag_y + 42, 15, idx_text, color=C_SUBTEXT)


def draw_rotating_vinyl(cx, cy, r, angle):
    """旋转黑胶唱片"""
    # 阴影
    img.draw_circle(cx + 5, cy + 8, r + 5, color=C_SHADOW, thickness=1, fill=True)
    img.draw_circle(cx + 2, cy + 4, r + 3, color=(11, 25, 43), thickness=1, fill=True)
    # 主体
    img.draw_circle(cx, cy, r, color=C_VINYL_BASE, thickness=2, fill=True)
    img.draw_circle(cx, cy, r, color=(88, 104, 124), thickness=1, fill=False)

    # 纹路
    for gr in [r-8, r-16, r-24, r-33, r-42, r-51, r-60, r-69, r-78]:
        img.draw_circle(cx, cy, gr, color=C_GROOVE, thickness=1, fill=False)

    # 光泽
    img.draw_circle(cx - 26, cy - 30, r // 3, color=(33, 43, 58), thickness=1, fill=False)
    for i in range(5):
        sy = cy - r + 22 + i * 6
        sw = int((r - 40) * (0.22 + i * 0.11))
        if sw > 3:
            img.draw_line(cx - sw, sy, cx + sw, sy, color=(58 + i * 6, 68 + i * 6, 84 + i * 6))

    # 标签
    img.draw_circle(cx, cy, LABEL_R, color=C_LABEL, thickness=2, fill=True)
    img.draw_circle(cx, cy, LABEL_R - 8, color=C_LABEL_INNER, thickness=1, fill=True)
    img.draw_circle(cx, cy, LABEL_R, color=(255, 201, 130), thickness=1, fill=False)

    # 旋转十字线
    for i in range(4):
        a = angle + i * math.pi / 2
        inner = HUB_R + 3
        outer = LABEL_R - 5
        img.draw_line(
            int(cx + inner * math.cos(a)), int(cy + inner * math.sin(a)),
            int(cx + outer * math.cos(a)), int(cy + outer * math.sin(a)),
            color=(220, 200, 200)
        )

    # 标签文字
    img.draw_string_advanced(cx - 20, cy - 11, 14, "MUSIC", color=(255, 250, 245))
    img.draw_string_advanced(cx - 15, cy + 7, 10, "33RPM", color=(255, 230, 205))

    # 轴心
    img.draw_circle(cx, cy, HUB_R, color=C_HUB, thickness=1, fill=True)
    img.draw_circle(cx - 1, cy - 1, HUB_R - 2, color=C_HUB_TOP, thickness=1, fill=True)

    # 旋转标记点
    dot_x = int(cx + (r - 10) * math.cos(angle))
    dot_y = int(cy + (r - 10) * math.sin(angle))
    img.draw_circle(dot_x, dot_y, 5, color=(250, 250, 255), thickness=2, fill=True)
    img.draw_circle(dot_x, dot_y, 9, color=(88, 134, 158), thickness=1, fill=False)

    # 指示线
    lx = int(cx + (r - 5) * math.cos(angle))
    ly = int(cy + (r - 5) * math.sin(angle))
    img.draw_line(cx, cy, lx, ly, color=(110, 138, 155))


def draw_spectrum_ring(cx, cy, r, angle):
    """唱片外圈频谱光环"""
    points = 48
    for i in range(points):
        a = 2 * math.pi * i / points
        amp = eq_heights[i % EQ_COUNT] * 15 + 3
        x1 = int(cx + r * math.cos(a))
        y1 = int(cy + r * math.sin(a))
        x2 = int(cx + (r + amp) * math.cos(a))
        y2 = int(cy + (r + amp) * math.sin(a))
        hue = (i / points + angle / (2 * math.pi)) % 1.0
        img.draw_line(x1, y1, x2, y2, color=hsv_to_rgb(hue, 0.58, 0.95), thickness=2)


def draw_equalizer(x, y, w, count, gap, max_h):
    """均衡器柱状图"""
    img.draw_string_advanced(x, y - 22, 13, "SPECTRUM", color=C_MUTED)
    for i in range(count):
        bar_h = int(eq_heights[i] * max_h * (volume / 100.0))
        bx = x + i * (w + gap)
        by = y + max_h - bar_h

        if bar_h > 0:
            if i < count // 3:
                col = C_ACCENT2
            elif i < count * 2 // 3:
                col = (70, 165, 245)
            else:
                col = C_ACCENT
            draw_pill(bx, by, w, max(bar_h, w), col)
            hl_h = min(3, bar_h)
            img.draw_rectangle(bx, by, w, hl_h,
                               color=lighten(col, 70),
                               fill=True)
        else:
            draw_pill(bx, y + max_h - 3, w, 4, (50, 74, 102))


def draw_volume_control(x, y, w, h, vol):
    """竖向音量控制"""
    panel_bg = (22, 44, 72) if is_dark_theme else (238, 246, 252)
    panel_border = (56, 88, 116) if is_dark_theme else (198, 214, 230)
    draw_round_rect(x - 31, y - 38, 70, h + 82, 16, panel_bg, fill=True)
    draw_round_rect(x - 31, y - 38, 70, h + 82, 16, panel_border, fill=False, thickness=1)
    img.draw_string_advanced(x - 18, y - 27, 13, "音量", color=C_SUBTEXT)

    track_x = x
    track_y = y
    draw_pill(track_x, track_y, w, h, C_PROGRESS_BG)

    fill_h = int(h * vol / 100.0)
    if fill_h > 0:
        ratio = vol / 100.0
        fr = int(38 + 217 * ratio)
        fg = int(224 - 96 * ratio)
        fb = int(190 - 82 * ratio)
        fill_color = (min(fr, 255), min(fg, 255), min(fb, 255))
        draw_pill(track_x, track_y + h - fill_h, w, max(fill_h, w), fill_color)

    knob_x = track_x + w // 2
    knob_y = track_y + h - fill_h
    img.draw_circle(knob_x, knob_y, 10, color=C_WHITE, thickness=2, fill=True)
    img.draw_circle(knob_x, knob_y, 10, color=(84, 116, 145), thickness=1, fill=False)
    img.draw_circle(knob_x, knob_y, 3, color=C_ACCENT2, thickness=1, fill=True)

    vol_text = f"{vol}%"
    img.draw_string_advanced(x - 18, y + h + 14, 15, vol_text, color=C_TEXT)
    img.draw_string_advanced(x - 3, y - 12, 11, "+", color=C_MUTED)
    img.draw_string_advanced(x - 3, y + h + 2, 11, "-", color=C_MUTED)


def draw_progress_bar(x, y, w, h, prog):
    """播放进度条"""
    # 轨道
    img.draw_string_advanced(x, y - 26, 13, "PLAYBACK", color=C_MUTED)
    draw_pill(x, y, w, h, C_PROGRESS_BG)

    fill_w = int(w * prog)
    if fill_w > 0:
        draw_pill(x, y, max(fill_w, h), h, C_PROGRESS_FG)

    knob_x = x + fill_w
    knob_y = y + h // 2
    img.draw_circle(knob_x, knob_y, 11, color=(6, 18, 30), thickness=1, fill=True)
    img.draw_circle(knob_x, knob_y, 9, color=C_WHITE, thickness=2, fill=True)
    img.draw_circle(knob_x, knob_y, 4, color=C_PROGRESS_FG, thickness=1, fill=True)

    # 时间
    cur_sec = int(prog * audio_total_frames / audio_framerate) if audio_framerate > 0 else 0
    total_sec = int(audio_total_frames / audio_framerate) if audio_framerate > 0 else 0
    time_cur = f"{cur_sec//60}:{cur_sec%60:02d}"
    time_tot = f"{total_sec//60}:{total_sec%60:02d}"
    img.draw_string_advanced(x, y + 15, 15, time_cur, color=C_TEXT)
    img.draw_string_advanced(x + w - 48, y + 15, 15, time_tot, color=C_SUBTEXT)


def draw_control_buttons():
    """三个控制按钮"""
    control_bg = (22, 43, 70) if is_dark_theme else (238, 246, 252)
    control_border = (56, 89, 118) if is_dark_theme else (198, 214, 230)
    draw_round_rect(CONTENT_X + 116, BTN_Y - 42, CONTENT_W - 232, 76, 24,
                    control_bg, fill=True)
    draw_round_rect(CONTENT_X + 116, BTN_Y - 42, CONTENT_W - 232, 76, 24,
                    control_border, fill=False, thickness=1)
    draw_icon_button(BTN_PREV_X, BTN_Y, BTN_R, "prev", C_BTN_PREV)
    icon = "pause" if is_playing else "play"
    btn_color = C_BTN_PAUSE if is_playing else C_BTN_PLAY
    draw_icon_button(BTN_PLAY_X, BTN_Y, BTN_R + 9, icon, btn_color)
    draw_icon_button(BTN_NEXT_X, BTN_Y, BTN_R, "next", C_BTN_NEXT)


def draw_icon_button(cx, cy, r, icon_type, color):
    """圆形图标按钮"""
    # 阴影
    img.draw_circle(cx, cy + 4, r + 2, color=(8, 20, 34), thickness=1, fill=True)
    # 主体
    img.draw_circle(cx, cy, r, color=color, thickness=2, fill=True)
    img.draw_circle(cx, cy, r, color=lighten(color, 38), thickness=1, fill=False)
    img.draw_circle(cx - r // 3, cy - r // 3, max(3, r // 5), color=lighten(color, 64), thickness=1, fill=True)

    # 图标
    if icon_type == "play":
        h = int(r * 0.46)
        x1 = cx - int(h * 0.2)
        x2 = cx + int(h * 0.5)
        y1, y2 = cy - h, cy + h
        img.draw_line(x1, y1, x2, cy, color=C_WHITE, thickness=4)
        img.draw_line(x1, y2, x2, cy, color=C_WHITE, thickness=4)
        img.draw_line(x1, y1, x1, y2, color=C_WHITE, thickness=4)
    elif icon_type == "pause":
        bw, bh, gap = int(r * 0.16), int(r * 0.56), int(r * 0.14)
        img.draw_rectangle(cx - gap - bw, cy - bh//2, bw, bh, color=C_WHITE, fill=True)
        img.draw_rectangle(cx + gap, cy - bh//2, bw, bh, color=C_WHITE, fill=True)
    elif icon_type == "prev":
        h = int(r * 0.42)
        x1, x2 = cx - int(h*0.2), cx - int(h*0.5)
        y1, y2 = cy - h, cy + h
        img.draw_line(x1, y1, x2, cy, color=C_WHITE, thickness=3)
        img.draw_line(x1, y2, x2, cy, color=C_WHITE, thickness=3)
        img.draw_line(x1, y1, x1, y2, color=C_WHITE, thickness=3)
        x3 = cx + int(h*0.18)
        img.draw_line(x3, y1, x1, cy, color=C_WHITE, thickness=3)
        img.draw_line(x3, y2, x1, cy, color=C_WHITE, thickness=3)
        img.draw_line(x3, y1, x3, y2, color=C_WHITE, thickness=3)
    elif icon_type == "next":
        h = int(r * 0.42)
        x1, x2 = cx + int(h*0.2), cx + int(h*0.5)
        y1, y2 = cy - h, cy + h
        img.draw_line(x1, y1, x2, cy, color=C_WHITE, thickness=3)
        img.draw_line(x1, y2, x2, cy, color=C_WHITE, thickness=3)
        img.draw_line(x1, y1, x1, y2, color=C_WHITE, thickness=3)
        x3 = cx - int(h*0.18)
        img.draw_line(x3, y1, x1, cy, color=C_WHITE, thickness=3)
        img.draw_line(x3, y2, x1, cy, color=C_WHITE, thickness=3)
        img.draw_line(x3, y1, x3, y2, color=C_WHITE, thickness=3)


def draw_floating_particles():
    """漂浮音符"""
    for p in particles:
        alpha = p['life']
        size = int(16 + 10 * alpha)
        r = 255
        g = int(120 + 135 * alpha)
        b = int(80 + 175 * alpha)
        img.draw_string_advanced(int(p['x']), int(p['y']), size, p['note'], color=(r, g, b))


# ============================================================
# 触摸处理（带消抖）
# ============================================================

def handle_touch(points):
    global is_playing, song_index, progress, volume, rotation_angle, is_dark_theme, player_should_exit
    global touch_was_active, debounce_until

    now = time.ticks_ms()

    if not points:
        touch_was_active = False
        return

    if time.ticks_diff(debounce_until, now) > 0:
        touch_was_active = True
        return

    pt = points[0]
    x, y = pt.x, pt.y

    is_touch_down = not touch_was_active
    touch_was_active = True

    # ---- 退出按钮：停止播放器并返回 touch.py 首页 ----
    if is_touch_down and is_inside_rect(x, y, EXIT_X - 4, EXIT_Y - 4, EXIT_W + 8, EXIT_H + 8):
        player_should_exit = True
        debounce_until = time.ticks_add(now, BTN_DEBOUNCE_MS)
        return

    # ---- 主题按钮：仅按下瞬间触发 ----
    if is_touch_down and is_inside_rect(x, y, THEME_X - 4, THEME_Y - 4, THEME_W + 8, THEME_H + 8):
        is_dark_theme = not is_dark_theme
        apply_theme(is_dark_theme)
        debounce_until = time.ticks_add(now, BTN_DEBOUNCE_MS)
        return

    # ---- 连续操作：进度条拖动 ----
    if is_inside_rect(x, y, PROGRESS_X - 15, PROGRESS_Y - 15, PROGRESS_W + 30, PROGRESS_H + 30):
        new_prog = max(0.0, min(1.0, (x - PROGRESS_X) / PROGRESS_W))
        progress = new_prog
        audio_seek(new_prog)
        return

    # ---- 连续操作：竖向音量拖动，上方为大音量 ----
    if is_inside_rect(x, y, VOL_X - 24, VOL_Y - 14, VOL_W + 48, VOL_H + 28):
        set_volume(int((VOL_Y + VOL_H - y) / VOL_H * 100))
        return

    # ---- 离散操作：仅按下瞬间触发 ----
    if not is_touch_down:
        return

    # 播放/暂停
    if is_inside_circle(x, y, BTN_PLAY_X, BTN_Y, BTN_R + 12):
        is_playing = not is_playing
        debounce_until = time.ticks_add(now, BTN_DEBOUNCE_MS)
        return

    # 上一首（单曲则重置进度）
    if is_inside_circle(x, y, BTN_PREV_X, BTN_Y, BTN_R + 3):
        if music_count <= 1:
            progress = 0.0
            rotation_angle = 0.0
            audio_seek(0.0)
        else:
            song_index = (song_index - 1) % music_count
            progress = 0.0
            rotation_angle = 0.0
            switch_song()
        debounce_until = time.ticks_add(now, BTN_DEBOUNCE_MS)
        return

    # 下一首（单曲则重置进度）
    if is_inside_circle(x, y, BTN_NEXT_X, BTN_Y, BTN_R + 3):
        if music_count <= 1:
            progress = 0.0
            rotation_angle = 0.0
            audio_seek(0.0)
        else:
            song_index = (song_index + 1) % music_count
            progress = 0.0
            rotation_angle = 0.0
            switch_song()
        debounce_until = time.ticks_add(now, BTN_DEBOUNCE_MS)
        return

    # 点击唱片区域
    if is_inside_circle(x, y, RECORD_CX, RECORD_CY, RECORD_R + 50):
        is_playing = not is_playing
        debounce_until = time.ticks_add(now, BTN_DEBOUNCE_MS)
        return

    # 点击歌曲列表项
    if is_inside_rect(x, y, LIST_X, LIST_Y + 70, LIST_W, LIST_H - 86):
        if music_count > 0:
            item_idx = list_scroll_offset + (y - (LIST_Y + 70)) // LIST_ITEM_H
            if 0 <= item_idx < music_count and item_idx != song_index:
                song_index = item_idx
                progress = 0.0
                rotation_angle = 0.0
                switch_song()
                debounce_until = time.ticks_add(now, BTN_DEBOUNCE_MS)
        return


def switch_song():
    """切换到当前 song_index 指向的歌曲"""
    global volume
    if music_count == 0:
        return
    audio_open(music_files[song_index])
    # 重新应用当前音量到硬件
    if audio_stream:
        try:
            audio_stream.volume(vol=volume)
        except:
            pass


def set_volume(vol):
    """设置音量并同步到硬件"""
    global volume
    volume = max(0, min(100, vol))
    if audio_stream:
        try:
            audio_stream.volume(vol=volume)
        except:
            pass


# ============================================================
# 状态更新
# ============================================================

def update_state(dt):
    global rotation_angle, progress, song_index, last_eq_update

    # ---- 音频播放 ----
    if is_playing and audio_stream and audio_wf:
        has_data, cur_frame = audio_play_chunk()
        if audio_total_frames > 0:
            progress = cur_frame / audio_total_frames

        if not has_data:
            # 播放完毕，自动下一首
            if music_count > 1:
                song_index = (song_index + 1) % music_count
            progress = 0.0
            rotation_angle = 0.0
            switch_song()
    else:
        # 暂停时从进度反算当前帧位置
        pass

    # ---- 动画 ----
    if is_playing and audio_stream:
        rotation_angle += dt * 2.2
        if rotation_angle > 2 * math.pi:
            rotation_angle -= 2 * math.pi

        # 均衡器
        now = time.ticks_ms()
        if time.ticks_diff(now, last_eq_update) > 80:
            last_eq_update = now
            vol_factor = volume / 100.0
            for i in range(EQ_COUNT):
                eq_phase[i] += 0.3 + urandom.getrandbits(6) / 255.0 * 0.5
                base = 0.2 + 0.8 * abs(math.sin(eq_phase[i]))
                noise = urandom.getrandbits(7) / 255.0 * 0.4 * vol_factor
                eq_targets[i] = min(1.0, base * 0.6 * vol_factor + 0.05 + noise)
    else:
        for i in range(EQ_COUNT):
            eq_targets[i] = max(0.02, eq_targets[i] * 0.90)

    for i in range(EQ_COUNT):
        eq_heights[i] += (eq_targets[i] - eq_heights[i]) * 0.25

    # 粒子
    for p in particles:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['life'] -= 0.003
        if is_playing:
            p['life'] -= 0.003

        if p['life'] <= 0 or p['y'] < -20 or p['x'] < -20 or p['x'] > DISPLAY_WIDTH + 20:
            p['x'] = urandom.getrandbits(10) % DISPLAY_WIDTH
            p['y'] = DISPLAY_HEIGHT + 10
            p['vx'] = (urandom.getrandbits(8) - 128) / 80.0
            p['vy'] = -(urandom.getrandbits(7) / 50.0 + 0.25)
            p['life'] = 0.5 + urandom.getrandbits(7) / 255.0 * 0.5
            p['note'] = ["♪", "♫", "♬", "♩"][urandom.getrandbits(2) % 4]


# ============================================================
# 均衡器颜色表
# ============================================================
eq_colors = [hsv_to_rgb(i / EQ_COUNT, 0.95, 0.95) for i in range(EQ_COUNT)]


# ============================================================
# 主循环
# ============================================================

def main():
    global last_time, is_playing, music_files, music_count, player_should_exit
    global touch_was_active, debounce_until, list_scroll_offset, progress, rotation_angle

    init_player_hardware()
    apply_theme(is_dark_theme)
    music_files = scan_music_files()
    music_count = len(music_files)
    player_should_exit = False
    touch_was_active = False
    debounce_until = 0
    list_scroll_offset = 0
    progress = 0.0
    rotation_angle = 0.0
    last_time = time.ticks_ms()

    print("=" * 50)
    print("  ♪ 触摸屏 WAV 音乐播放器")
    print("  黑胶唱片 | 频谱动画 | 均衡器 | 音量控制")
    print("=" * 50)
    print(f"音乐目录: {MUSIC_DIR}")
    print(f"找到 {music_count} 首 WAV 文件")
    if music_count > 0:
        for i, f in enumerate(music_files):
            marker = "→" if i == 0 else " "
            print(f"  {marker} [{i+1}] {f}")
    else:
        print("  (无音乐文件，仅演示UI)")
    print("=" * 50)
    print("操作：")
    print("  左侧列表 → 点击选歌")
    print("  唱片区域 → 播放/暂停")
    print("  底部按钮 → 上一首/暂停播放/下一首")
    print("  进度条   → 拖拽快进快退")
    print("  音量条   → 拖拽或点击±调节")
    print("=" * 50)

    # 初始化第一首歌
    if music_count > 0:
        switch_song()

    try:
        while True:
            os.exitpoint()

            # 帧时间
            now = time.ticks_ms()
            dt = time.ticks_diff(now, last_time) / 1000.0
            last_time = now
            if dt > 0.1:
                dt = 0.033
            if dt <= 0:
                dt = 0.033

            # 更新
            update_state(dt)

            # 触摸
            points = tp.read(5)
            handle_touch(points)
            if player_should_exit:
                print("退出音乐播放器，返回主界面")
                break

            # 绘制
            draw_background()
            draw_song_list_panel()
            draw_top_info()
            draw_exit_button()
            draw_theme_button()
            draw_spectrum_ring(RECORD_CX, RECORD_CY, RECORD_R + 14, rotation_angle)
            draw_rotating_vinyl(RECORD_CX, RECORD_CY, RECORD_R, rotation_angle)
            draw_equalizer(EQ_START_X, EQ_Y, EQ_BAR_W, EQ_COUNT, EQ_GAP, EQ_MAX_H)
            draw_volume_control(VOL_X, VOL_Y, VOL_W, VOL_H, volume)
            draw_progress_bar(PROGRESS_X, PROGRESS_Y, PROGRESS_W, PROGRESS_H, progress)
            draw_control_buttons()
            draw_floating_particles()

            Display.show_image(img)

            time.sleep_ms(28)

    except KeyboardInterrupt:
        print("用户停止播放器")
    except BaseException as e:
        print(f"异常: {e}")
    finally:
        audio_close()
        try:
            if HT_CTRL:
                HT_CTRL.low()
        except:
            pass
        Display.deinit()
        os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
        time.sleep_ms(100)
        MediaManager.deinit()


if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()
