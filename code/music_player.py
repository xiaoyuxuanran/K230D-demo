# 触摸屏音乐播放器（集成WAV音频播放） - 立创·庐山派-K230-CanMV
# 功能：WAV音频播放/暂停、进度拖拽/快进快退、音量调节、切歌、音乐目录显示
# 动画：旋转黑胶唱片、频谱光环、均衡器跳动、浮动音符粒子

import time, os, gc, sys, urandom, math
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
fpioa = FPIOA()
fpioa.set_function(10, FPIOA.GPIO10)
HT_CTRL = Pin(10, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
HT_CTRL.high()  # 拉高使能音频功放

# ============================================================
# 显示初始化
# ============================================================
DISPLAY_MODE = "LCD"
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480

if DISPLAY_MODE == "VIRT":
    DISPLAY_WIDTH = ALIGN_UP(1920, 16)
    DISPLAY_HEIGHT = 1080
    Display.init(Display.VIRT, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, fps=60)
elif DISPLAY_MODE == "LCD":
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
# 颜色定义 —— 明亮风格
# ============================================================
C_BG_TOP      = (215, 218, 235)
C_BG_BOT      = (235, 237, 248)
C_PANEL       = (240, 241, 250)
C_PANEL_ITEM  = (225, 227, 240)
C_PANEL_ACTIVE = (200, 210, 240)
C_TEXT        = (38, 38, 55)
C_SUBTEXT     = (130, 130, 150)
C_ACCENT      = (255, 90, 95)
C_ACCENT2     = (50, 185, 175)
C_PROGRESS_BG = (210, 212, 225)
C_PROGRESS_FG = (255, 90, 95)
C_WHITE       = (255, 255, 255)
C_VINYL_BASE  = (32, 30, 38)
C_GROOVE      = (58, 56, 65)
C_LABEL       = (235, 75, 75)
C_LABEL_INNER = (200, 50, 50)
C_HUB         = (70, 70, 70)
C_HUB_TOP     = (110, 110, 110)
C_SHADOW      = (160, 162, 180)
C_BTN_PREV    = (120, 125, 195)
C_BTN_NEXT    = (120, 125, 195)
C_BTN_PLAY    = (255, 90, 95)
C_BTN_PAUSE   = (50, 185, 175)

# ============================================================
# 布局参数
# ============================================================
# 左侧歌曲列表面板
LIST_X      = 5
LIST_Y      = 10
LIST_W      = 155
LIST_H      = 460
LIST_ITEM_H = 34
LIST_MAX_VISIBLE = 10

# 主内容区域起始X
CONTENT_X   = 175
CONTENT_W   = 620
CONTENT_CX  = CONTENT_X + CONTENT_W // 2  # ~485

# 唱片
RECORD_CX = CONTENT_CX
RECORD_CY = 180
RECORD_R  = 108
LABEL_R   = 35
HUB_R     = 6

# 均衡器
EQ_Y       = 300
EQ_BAR_W   = 14
EQ_GAP     = 5
EQ_COUNT   = 20
EQ_MAX_H   = 30
EQ_START_X = CONTENT_X + 5

# 音量
VOL_Y      = 344
VOL_X      = CONTENT_X + 5
VOL_W      = 180
VOL_H      = 6

# 进度条
PROGRESS_Y = 370
PROGRESS_X = CONTENT_X + 5
PROGRESS_W = CONTENT_W - 10
PROGRESS_H = 8

# 按钮（加大间距，杜绝重叠）
BTN_Y      = 422
BTN_R      = 22
BTN_PLAY_X = CONTENT_CX
BTN_PREV_X = CONTENT_CX - 135
BTN_NEXT_X = CONTENT_CX + 135

# 顶部信息
TITLE_Y  = 22
ARTIST_Y = 54

PARTICLE_COUNT = 8

# ============================================================
# 全局状态
# ============================================================
is_playing = True
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

# ============================================================
# 绘制函数
# ============================================================

def draw_background():
    """明亮渐变背景"""
    img.clear()
    for i in range(DISPLAY_HEIGHT):
        ratio = i / DISPLAY_HEIGHT
        r = int(C_BG_TOP[0] + (C_BG_BOT[0] - C_BG_TOP[0]) * ratio)
        g = int(C_BG_TOP[1] + (C_BG_BOT[1] - C_BG_TOP[1]) * ratio)
        b = int(C_BG_TOP[2] + (C_BG_BOT[2] - C_BG_TOP[2]) * ratio)
        img.draw_line(0, i, DISPLAY_WIDTH, i, color=(r, g, b))

    # 装饰圆
    img.draw_circle(730, 70, 120, color=(225, 228, 242), thickness=1, fill=True)
    img.draw_circle(730, 70, 85, color=(232, 234, 246), thickness=1, fill=True)
    img.draw_circle(100, 420, 70, color=(225, 228, 242), thickness=1, fill=True)


def draw_song_list_panel():
    """左侧歌曲列表面板"""
    # 面板背景
    img.draw_rectangle(LIST_X, LIST_Y, LIST_W, LIST_H, color=C_PANEL, fill=True)
    img.draw_rectangle(LIST_X, LIST_Y, LIST_W, LIST_H, color=(195, 197, 215), thickness=1, fill=False)

    # 标题
    img.draw_string_advanced(LIST_X + 8, LIST_Y + 5, 15, "♪ 音乐列表", color=C_TEXT)
    dir_label = MUSIC_DIR
    img.draw_string_advanced(LIST_X + 8, LIST_Y + 22, 11, dir_label, color=C_SUBTEXT)

    if music_count == 0:
        img.draw_string_advanced(LIST_X + 10, LIST_Y + 60, 14, "无音乐文件", color=C_SUBTEXT)
        img.draw_string_advanced(LIST_X + 10, LIST_Y + 78, 12, "请放入 /data/", color=C_SUBTEXT)
        img.draw_string_advanced(LIST_X + 10, LIST_Y + 93, 12, "中的 .wav 文件", color=C_SUBTEXT)
        return

    # 列表可见范围
    list_top = LIST_Y + 38
    list_bottom = LIST_Y + LIST_H - 10
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
            img.draw_rectangle(LIST_X + 3, item_y, LIST_W - 6, LIST_ITEM_H - 2,
                               color=C_PANEL_ACTIVE, fill=True)
            # 左侧指示条
            img.draw_rectangle(LIST_X + 3, item_y + 2, 3, LIST_ITEM_H - 6,
                               color=C_ACCENT, fill=True)

        # 序号 + 文件名
        num_text = f"{fi+1:02d}"
        img.draw_string_advanced(LIST_X + 10, item_y + 4, 13, num_text,
                                 color=C_ACCENT if is_current else C_SUBTEXT)

        title = filename_to_title(music_files[fi])
        draw_text_clipped(LIST_X + 32, item_y + 4, LIST_W - 42, title, 13,
                          C_TEXT if is_current else C_SUBTEXT)

    # 滚动条指示
    if music_count > visible_count:
        bar_h = int((visible_count / music_count) * (visible_count * LIST_ITEM_H))
        bar_y = list_top + int((list_scroll_offset / music_count) * (visible_count * LIST_ITEM_H))
        img.draw_rectangle(LIST_X + LIST_W - 5, bar_y, 3, bar_h, color=(180, 182, 200), fill=True)


def draw_top_info():
    """顶部歌曲信息"""
    if music_count == 0:
        draw_text_centered(CONTENT_X, TITLE_Y + 20, CONTENT_W, "请放入 WAV 音乐文件到 /data/ 目录", 16, C_SUBTEXT)
        return

    filename = music_files[song_index]
    title = filename_to_title(filename)
    draw_text_clipped(CONTENT_X, TITLE_Y, CONTENT_W - 110, title, 28, C_TEXT)

    # 文件信息
    if audio_framerate > 0:
        khz = audio_framerate / 1000.0
        ch = "立体声" if audio_channels >= 2 else "单声道"
        bits = audio_sampwidth * 8
        info = f"{khz:.1f}kHz | {ch} | {bits}bit | WAV"
    else:
        info = filename
    img.draw_string_advanced(CONTENT_X, ARTIST_Y, 16, info, color=C_SUBTEXT)

    # 右侧状态标签
    if is_playing:
        tag_text = "▶ 播放中"
        tag_color = C_ACCENT
    else:
        tag_text = "⏸ 已暂停"
        tag_color = C_ACCENT2

    tag_w = 100
    tag_h = 28
    tag_x = CONTENT_X + CONTENT_W - tag_w - 5
    tag_y = TITLE_Y
    img.draw_rectangle(tag_x, tag_y, tag_w, tag_h, color=tag_color, fill=True)
    draw_text_centered(tag_x, tag_y + 5, tag_w, tag_text, 16, C_WHITE)

    # 歌曲序号
    idx_text = f"{song_index + 1} / {music_count}"
    img.draw_string_advanced(tag_x, ARTIST_Y + 2, 14, idx_text, color=C_SUBTEXT)


def draw_rotating_vinyl(cx, cy, r, angle):
    """旋转黑胶唱片"""
    # 阴影
    img.draw_circle(cx + 3, cy + 4, r + 2, color=C_SHADOW, thickness=1, fill=True)
    # 主体
    img.draw_circle(cx, cy, r, color=C_VINYL_BASE, thickness=2, fill=True)
    img.draw_circle(cx, cy, r, color=(75, 73, 82), thickness=1, fill=False)

    # 纹路
    for gr in [r-8, r-18, r-28, r-38, r-48, r-57, r-65, r-72]:
        img.draw_circle(cx, cy, gr, color=C_GROOVE, thickness=1, fill=False)

    # 光泽
    for i in range(4):
        sy = cy - r + 20 + i * 4
        sw = int((r - 35) * (0.25 + i * 0.12))
        sr, sg, sb = 68 + i*8, 66 + i*8, 78 + i*8
        if sw > 3:
            img.draw_line(cx - sw, sy, cx + sw, sy, color=(sr, sg, sb))

    # 标签
    img.draw_circle(cx, cy, LABEL_R, color=C_LABEL, thickness=2, fill=True)
    img.draw_circle(cx, cy, LABEL_R, color=C_LABEL_INNER, thickness=2, fill=False)
    img.draw_circle(cx, cy, int(LABEL_R * 0.82), color=C_LABEL_INNER, thickness=1, fill=False)

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
    img.draw_string_advanced(cx - 20, cy - 12, 15, "MUSIC", color=(245, 245, 250))
    img.draw_string_advanced(cx - 16, cy + 6, 11, "33 RPM", color=(210, 210, 220))

    # 轴心
    img.draw_circle(cx, cy, HUB_R, color=C_HUB, thickness=1, fill=True)
    img.draw_circle(cx - 1, cy - 1, HUB_R - 2, color=C_HUB_TOP, thickness=1, fill=True)

    # 旋转标记点
    dot_x = int(cx + (r - 10) * math.cos(angle))
    dot_y = int(cy + (r - 10) * math.sin(angle))
    img.draw_circle(dot_x, dot_y, 5, color=(250, 250, 255), thickness=2, fill=True)
    img.draw_circle(dot_x, dot_y, 9, color=(130, 130, 165), thickness=1, fill=False)

    # 指示线
    lx = int(cx + (r - 5) * math.cos(angle))
    ly = int(cy + (r - 5) * math.sin(angle))
    img.draw_line(cx, cy, lx, ly, color=(150, 148, 165))


def draw_spectrum_ring(cx, cy, r, angle):
    """唱片外圈频谱光环"""
    points = 48
    for i in range(points):
        a = 2 * math.pi * i / points
        amp = eq_heights[i % EQ_COUNT] * 18 + 2
        x1 = int(cx + r * math.cos(a))
        y1 = int(cy + r * math.sin(a))
        x2 = int(cx + (r + amp) * math.cos(a))
        y2 = int(cy + (r + amp) * math.sin(a))
        hue = (i / points + angle / (2 * math.pi)) % 1.0
        img.draw_line(x1, y1, x2, y2, color=hsv_to_rgb(hue, 0.9, 0.95))


def draw_equalizer(x, y, w, count, gap, max_h):
    """均衡器柱状图"""
    for i in range(count):
        bar_h = int(eq_heights[i] * max_h * (volume / 100.0))
        bx = x + i * (w + gap)
        by = y + max_h - bar_h

        if bar_h > 0:
            col = eq_colors[i]
            img.draw_rectangle(bx, by, w, bar_h, color=col, fill=True)
            hl_h = min(3, bar_h)
            img.draw_rectangle(bx, by, w, hl_h,
                               color=(min(col[0]+90,255), min(col[1]+90,255), min(col[2]+90,255)),
                               fill=True)
        img.draw_rectangle(bx, y + max_h - 1, w, 1, color=(185, 187, 200), fill=True)


def draw_volume_control(x, y, w, h, vol):
    """音量控制"""
    img.draw_string_advanced(x - 2, y - 3, 18, "♫", color=C_ACCENT if vol > 0 else C_SUBTEXT)

    sx = x + 28
    # 轨道
    img.draw_rectangle(sx, y, w, h, color=(210, 212, 225), fill=True)
    img.draw_circle(sx, y + h // 2, h // 2, color=(210, 212, 225), thickness=1, fill=True)
    img.draw_circle(sx + w, y + h // 2, h // 2, color=(210, 212, 225), thickness=1, fill=True)

    fill_w = int(w * vol / 100.0)
    if fill_w > 0:
        ratio = vol / 100.0
        fr = int(50 + 205 * ratio)
        fg = int(185 - 95 * ratio)
        fb = int(175 - 80 * ratio)
        fill_color = (min(fr,255), min(fg,255), min(fb,255))
        img.draw_rectangle(sx, y, fill_w, h, color=fill_color, fill=True)
        if fill_w > h:
            img.draw_circle(sx + fill_w, y + h // 2, h // 2, color=fill_color, thickness=1, fill=True)

    knob_x = sx + fill_w
    knob_y = y + h // 2
    img.draw_circle(knob_x, knob_y, 8, color=C_WHITE, thickness=2, fill=True)
    img.draw_circle(knob_x, knob_y, 8, color=(180, 182, 200), thickness=1, fill=False)
    img.draw_circle(knob_x, knob_y, 3, color=C_ACCENT, thickness=1, fill=True)

    vol_text = f"{vol}%"
    img.draw_string_advanced(sx + w + 12, y - 2, 16, vol_text, color=C_TEXT)

    # 触摸提示
    img.draw_string_advanced(sx - 2, y - 13, 12, "-", color=C_SUBTEXT)
    img.draw_string_advanced(sx + w - 8, y - 13, 12, "+", color=C_SUBTEXT)


def draw_progress_bar(x, y, w, h, prog):
    """播放进度条"""
    # 轨道
    img.draw_rectangle(x, y, w, h, color=C_PROGRESS_BG, fill=True)
    img.draw_circle(x, y + h // 2, h // 2, color=C_PROGRESS_BG, thickness=1, fill=True)
    img.draw_circle(x + w, y + h // 2, h // 2, color=C_PROGRESS_BG, thickness=1, fill=True)

    fill_w = int(w * prog)
    if fill_w > 0:
        img.draw_rectangle(x, y, fill_w, h, color=C_PROGRESS_FG, fill=True)
        if fill_w > h:
            img.draw_circle(x + fill_w, y + h // 2, h // 2, color=C_PROGRESS_FG, thickness=1, fill=True)

    knob_x = x + fill_w
    knob_y = y + h // 2
    img.draw_circle(knob_x, knob_y, 10, color=C_WHITE, thickness=2, fill=True)
    img.draw_circle(knob_x, knob_y, 10, color=C_PROGRESS_FG, thickness=1, fill=False)
    img.draw_circle(knob_x, knob_y, 5, color=C_PROGRESS_FG, thickness=1, fill=True)

    # 时间
    cur_sec = int(prog * audio_total_frames / audio_framerate) if audio_framerate > 0 else 0
    total_sec = int(audio_total_frames / audio_framerate) if audio_framerate > 0 else 0
    time_cur = f"{cur_sec//60}:{cur_sec%60:02d}"
    time_tot = f"{total_sec//60}:{total_sec%60:02d}"
    img.draw_string_advanced(x, y - 18, 16, time_cur, color=C_TEXT)
    img.draw_string_advanced(x + w - 55, y - 18, 16, time_tot, color=C_SUBTEXT)


def draw_control_buttons():
    """三个控制按钮"""
    draw_icon_button(BTN_PREV_X, BTN_Y, BTN_R, "prev", C_BTN_PREV)
    icon = "pause" if is_playing else "play"
    btn_color = C_BTN_PAUSE if is_playing else C_BTN_PLAY
    draw_icon_button(BTN_PLAY_X, BTN_Y, BTN_R + 2, icon, btn_color)
    draw_icon_button(BTN_NEXT_X, BTN_Y, BTN_R, "next", C_BTN_NEXT)


def draw_icon_button(cx, cy, r, icon_type, color):
    """圆形图标按钮（3D风格）"""
    # 阴影
    img.draw_circle(cx, cy + 2, r + 1, color=(185, 187, 200), thickness=2, fill=True)
    # 主体
    img.draw_circle(cx, cy, r, color=color, thickness=2, fill=True)
    # 底部暗面
    dark = (max(color[0]-35,0), max(color[1]-35,0), max(color[2]-35,0))
    img.draw_circle(cx, cy + r // 3, r, color=dark, thickness=2, fill=True)
    # 上半亮面
    light = (min(color[0]+45,255), min(color[1]+45,255), min(color[2]+45,255))
    img.draw_circle(cx, cy - r // 4, r - 2, color=light, thickness=1, fill=False)
    # 顶部高光线
    hl_y = cy - r + 4
    hl_len = int(r * 1.0)
    hl_c = (min(color[0]+85,255), min(color[1]+85,255), min(color[2]+85,255))
    img.draw_line(cx - hl_len, hl_y, cx + hl_len, hl_y, color=hl_c)

    # 图标
    if icon_type == "play":
        h = int(r * 0.55)
        x1 = cx - int(h * 0.2)
        x2 = cx + int(h * 0.5)
        y1, y2 = cy - h, cy + h
        img.draw_line(x1, y1, x2, cy, color=C_WHITE, thickness=3)
        img.draw_line(x1, y2, x2, cy, color=C_WHITE, thickness=3)
        img.draw_line(x1, y1, x1, y2, color=C_WHITE, thickness=3)
    elif icon_type == "pause":
        bw, bh, gap = int(r * 0.16), int(r * 0.6), int(r * 0.14)
        img.draw_rectangle(cx - gap - bw, cy - bh//2, bw, bh, color=C_WHITE, fill=True)
        img.draw_rectangle(cx + gap, cy - bh//2, bw, bh, color=C_WHITE, fill=True)
    elif icon_type == "prev":
        h = int(r * 0.42)
        x1, x2 = cx - int(h*0.2), cx - int(h*0.5)
        y1, y2 = cy - h, cy + h
        img.draw_line(x1, y1, x2, cy, color=C_WHITE, thickness=2)
        img.draw_line(x1, y2, x2, cy, color=C_WHITE, thickness=2)
        img.draw_line(x1, y1, x1, y2, color=C_WHITE, thickness=2)
        x3 = cx + int(h*0.18)
        img.draw_line(x3, y1, x1, cy, color=C_WHITE, thickness=2)
        img.draw_line(x3, y2, x1, cy, color=C_WHITE, thickness=2)
        img.draw_line(x3, y1, x3, y2, color=C_WHITE, thickness=2)
    elif icon_type == "next":
        h = int(r * 0.42)
        x1, x2 = cx + int(h*0.2), cx + int(h*0.5)
        y1, y2 = cy - h, cy + h
        img.draw_line(x1, y1, x2, cy, color=C_WHITE, thickness=2)
        img.draw_line(x1, y2, x2, cy, color=C_WHITE, thickness=2)
        img.draw_line(x1, y1, x1, y2, color=C_WHITE, thickness=2)
        x3 = cx - int(h*0.18)
        img.draw_line(x3, y1, x1, cy, color=C_WHITE, thickness=2)
        img.draw_line(x3, y2, x1, cy, color=C_WHITE, thickness=2)
        img.draw_line(x3, y1, x3, y2, color=C_WHITE, thickness=2)


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
    global is_playing, song_index, progress, volume, rotation_angle
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

    # ---- 连续操作：进度条拖动 ----
    if is_inside_rect(x, y, PROGRESS_X - 15, PROGRESS_Y - 15, PROGRESS_W + 30, PROGRESS_H + 30):
        new_prog = max(0.0, min(1.0, (x - PROGRESS_X) / PROGRESS_W))
        progress = new_prog
        audio_seek(new_prog)
        return

    # ---- 连续操作：音量拖动 ----
    vol_sx = VOL_X + 28
    if is_inside_rect(x, y, vol_sx - 10, VOL_Y - 12, VOL_W + 20, VOL_H + 24):
        set_volume(int((x - vol_sx) / VOL_W * 100))
        return

    # ---- 离散操作：仅按下瞬间触发 ----
    if not is_touch_down:
        return

    # 音量 - 快速点击
    if is_inside_rect(x, y, VOL_X - 5, VOL_Y - 13, 30, VOL_H + 26):
        set_volume(volume - 10)
        debounce_until = time.ticks_add(now, BTN_DEBOUNCE_MS)
        return

    # 音量 + 快速点击
    if is_inside_rect(x, y, VOL_X + VOL_W + 10, VOL_Y - 13, 40, VOL_H + 26):
        set_volume(volume + 10)
        debounce_until = time.ticks_add(now, BTN_DEBOUNCE_MS)
        return

    # 播放/暂停
    if is_inside_circle(x, y, BTN_PLAY_X, BTN_Y, BTN_R + 6):
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
    if is_inside_rect(x, y, LIST_X, LIST_Y + 38, LIST_W, LIST_H - 48):
        if music_count > 0:
            item_idx = list_scroll_offset + (y - (LIST_Y + 38)) // LIST_ITEM_H
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
    global last_time, is_playing

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

            # 绘制
            draw_background()
            draw_song_list_panel()
            draw_top_info()
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
        Display.deinit()
        os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
        time.sleep_ms(100)
        MediaManager.deinit()


if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()

