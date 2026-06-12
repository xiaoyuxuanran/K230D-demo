# K230D LVGL 触摸屏音乐播放器（WAV音频播放）
# 参照 lvgl_demo.py 的实际 API 模式编写

import os, sys, gc, time, math, urandom
import lvgl as lv
import uctypes
from media.display import *
from media.media import *
from media.pyaudio import *
import media.wave as wave
import image
from machine import TOUCH
from machine import Pin
from machine import FPIOA

# ============================================================
# 音频硬件初始化
# ============================================================
HT_CTRL = None

def init_amp():
    global HT_CTRL
    fpioa = FPIOA()
    fpioa.set_function(10, FPIOA.GPIO10)
    HT_CTRL = Pin(10, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    HT_CTRL.high()

# ============================================================
# 全局参数
# ============================================================
DISPLAY_WIDTH = ALIGN_UP(800, 16)
DISPLAY_HEIGHT = 480
MUSIC_DIR = "/data"

# ============================================================
# LVGL 初始化（参照 lvgl_demo.py 模式）
# ============================================================
disp_imgs = []

def lvgl_init():
    global disp_imgs
    print("  A) lv.init()...")
    lv.init()
    print("  B) lv.init() OK")

    print("  C) 创建 Image 缓冲区...")
    img0 = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.BGRA8888)
    img1 = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.BGRA8888)
    disp_imgs = [img0, img1]
    print("  D) Image 缓冲区 OK")

    print("  E) lv.disp_create...")
    disp_drv = lv.disp_create(DISPLAY_WIDTH, DISPLAY_HEIGHT)
    print("  F) 设置颜色格式...")
    disp_drv.set_color_format(lv.COLOR_FORMAT.ARGB8888)
    print("  G) 设置绘制缓冲区...")
    disp_drv.set_draw_buffers(
        img0.bytearray(), img1.bytearray(),
        img0.size(), lv.DISP_RENDER_MODE.FULL
    )
    print("  H) 设置 flush 回调...")
    disp_drv.set_flush_cb(lvgl_flush_cb)
    print("  I) LVGL 初始化完成")

def lvgl_flush_cb(disp_drv, area, color):
    if disp_drv.flush_is_last():
        ptr = uctypes.addressof(color.__dereference__())
        img_to_show = disp_imgs[0] if disp_imgs[0].virtaddr() == ptr else disp_imgs[1]
        Display.show_image(img_to_show, layer=Display.LAYER_OSD0)
    disp_drv.flush_ready()

# ============================================================
# 触摸初始化（参照 lvgl_demo.py TouchScreen 类）
# ============================================================
class TouchScreen:
    def __init__(self):
        # K230D LVGL 环境下 TOUCH(0) 与 lv.indev 存在冲突，
        # 参照 lvgl_demo.py 的做法，先不初始化触摸硬件。
        self.touch = None
        self.indev = lv.indev_create()
        self.indev.set_type(lv.INDEV_TYPE.POINTER)
        self.indev.set_read_cb(self._callback)

    def _callback(self, driver, data):
        if self.touch is None:
            data.state = lv.INDEV_STATE.RELEASED
            return
        try:
            tp = self.touch.read(1)
            if tp and len(tp) > 0:
                data.point.x = tp[0].x
                data.point.y = tp[0].y
                if tp[0].event in [2, 3]:
                    data.state = lv.INDEV_STATE.PRESSED
                else:
                    data.state = lv.INDEV_STATE.RELEASED
            else:
                data.state = lv.INDEV_STATE.RELEASED
        except:
            data.state = lv.INDEV_STATE.RELEASED

# ============================================================
# 颜色工具
# ============================================================
def color_hex(s):
    """ '#RRGGBB' → lvgl color """
    return lv.color_hex(int(s.lstrip('#'), 16))

# 深色 / 浅色主题色表
DARK = {
    'bg':       '#121e3a', 'bg2':      '#0a5e5a',
    'panel':    '#152341', 'panel2':   '#1c3052',
    'active':   '#22d6b8', 'text':     '#f4faff',
    'subtext':  '#9cb7cd', 'accent':   '#ff6f60',
    'accent2':  '#26e0be', 'progress': '#2d4664',
    'prog_fg':  '#26e0be', 'btn_prev': '#3c5291',
    'btn_next': '#3c5291', 'btn_play': '#ff6f60',
    'btn_pause':'#26bea8', 'white':    '#ffffff',
}

LIGHT = {
    'bg':       '#eef2f8', 'bg2':      '#d5ebee',
    'panel':    '#fafcff', 'panel2':   '#ebf1f8',
    'active':   '#21b5a0', 'text':     '#1a2637',
    'subtext':  '#586c82', 'accent':   '#f05c50',
    'accent2':  '#00aa96', 'progress': '#cedae7',
    'prog_fg':  '#00aa96', 'btn_prev': '#5b76be',
    'btn_next': '#5b76be', 'btn_play': '#f05c50',
    'btn_pause':'#00aa96', 'white':    '#ffffff',
}

THEME = dict(DARK)
IS_DARK = True

# ============================================================
# 音频状态 / 函数
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

def _wav_total_frames(filepath, sampwidth, channels):
    try:
        sz = os.stat(filepath)[6]
        data_sz = sz - 44
        return data_sz // (sampwidth * channels) if data_sz > 0 else 0
    except:
        return 0

def audio_open(filename):
    global audio_wf, audio_p, audio_stream, audio_chunk_size
    global audio_total_frames, audio_current_frame
    global audio_framerate, audio_channels, audio_sampwidth, audio_filepath

    audio_close()
    audio_filepath = MUSIC_DIR + "/" + filename
    audio_wf = wave.open(audio_filepath, 'rb')
    audio_framerate = audio_wf.get_framerate()
    audio_channels = audio_wf.get_channels()
    audio_sampwidth = audio_wf.get_sampwidth()
    audio_chunk_size = int(audio_framerate / 25)
    audio_current_frame = 0
    audio_total_frames = _wav_total_frames(audio_filepath, audio_sampwidth, audio_channels)

    audio_p = PyAudio()
    audio_stream = audio_p.open(
        format=audio_p.get_format_from_width(audio_sampwidth),
        channels=audio_channels,
        rate=audio_framerate,
        output=True,
        frames_per_buffer=audio_chunk_size,
    )
    audio_stream.volume(vol=volume)

    for _ in range(4):
        d = audio_wf.read_frames(audio_chunk_size)
        if d:
            audio_stream.write(d)
            audio_current_frame = min(audio_current_frame + audio_chunk_size, audio_total_frames)

def audio_play_chunk():
    global audio_current_frame
    if not audio_wf or not audio_stream:
        return False, 0
    has = False
    for _ in range(3):
        d = audio_wf.read_frames(audio_chunk_size)
        if d:
            audio_stream.write(d)
            audio_current_frame = min(audio_current_frame + audio_chunk_size, audio_total_frames)
            has = True
        else:
            break
    return has, audio_current_frame

def audio_seek(ratio):
    global audio_current_frame, audio_wf
    if not audio_wf or audio_total_frames <= 0:
        return
    target = int(audio_total_frames * ratio)
    if target >= audio_total_frames:
        target = audio_total_frames - audio_chunk_size
    if target < 0:
        target = 0
    audio_wf.close()
    audio_wf = wave.open(audio_filepath, 'rb')
    skipped = 0
    sc = audio_chunk_size
    while skipped < target:
        ts = min(sc, target - skipped)
        if not audio_wf.read_frames(ts):
            break
        skipped += ts
    audio_current_frame = target

def audio_close():
    global audio_wf, audio_p, audio_stream
    for obj in ['audio_stream', 'audio_p', 'audio_wf']:
        try:
            o = globals()[obj]
            if o:
                if obj == 'audio_stream':
                    o.stop_stream()
                    o.close()
                elif obj == 'audio_p':
                    o.terminate()
                elif obj == 'audio_wf':
                    o.close()
        except:
            pass
    audio_wf = audio_p = audio_stream = None

# ============================================================
# 播放状态
# ============================================================
is_playing = True
volume = 70
song_index = 0
progress = 0.0
player_should_exit = False
music_files = []
music_count = 0

def set_volume(vol):
    global volume
    volume = max(0, min(100, vol))
    if vol_slider:
        vol_slider.set_value(volume, lv.ANIM.OFF)
    if audio_stream:
        try:
            audio_stream.volume(vol=volume)
        except:
            pass

def switch_song():
    if music_count == 0:
        return
    audio_open(music_files[song_index])
    if audio_stream:
        try:
            audio_stream.volume(vol=volume)
        except:
            pass

def filename_to_title(fn):
    n = fn.rsplit('.', 1)[0]
    n = n.replace('_', ' ').replace('-', ' ')
    return n.strip() or fn

def clip_text(t, mx):
    return t if len(t) <= mx else t[:mx-2] + '..'

# ============================================================
# 均衡器状态
# ============================================================
EQ_COUNT = 16
eq_heights = [0.0] * EQ_COUNT
eq_targets = [0.0] * EQ_COUNT
eq_phase = [0.0] * EQ_COUNT
last_eq_update = 0
eq_bars = []

# ============================================================
# UI 组件引用
# ============================================================
vol_slider = None
progress_slider = None

# ============================================================
# 歌曲列表（左侧面板）
# ============================================================
SX, SY, SW, SH = 12, 16, 190, 448
ITEM_H = 44

def build_song_list(parent):
    global song_list_obj
    # 面板
    panel = lv.obj(parent)
    panel.set_size(SW, SH)
    panel.set_pos(SX, SY)
    panel.set_style_bg_color(color_hex(THEME['panel']), 0)
    panel.set_style_border_width(1, 0)
    panel.set_style_border_color(color_hex(THEME['panel2']), 0)
    panel.set_style_radius(14, 0)
    panel.set_style_pad_all(12, 0)
    panel.set_flex_flow(lv.FLEX_FLOW.COLUMN)
    panel.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.START)

    # 标题行
    hdr = lv.obj(panel)
    hdr.set_size(SW - 24, 36)
    hdr.set_style_bg_opa(0, 0)
    hdr.set_style_border_width(0, 0)
    hdr.set_flex_flow(lv.FLEX_FLOW.ROW)
    hdr.set_flex_align(lv.FLEX_ALIGN.SPACE_BETWEEN, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

    hl = lv.label(hdr)
    hl.set_text("音乐列表")
    hl.set_style_text_color(color_hex(THEME['text']), 0)

    cnt_obj = lv.obj(hdr)
    cnt_obj.set_size(44, 22)
    cnt_obj.set_style_bg_color(color_hex(THEME['panel2']), 0)
    cnt_obj.set_style_radius(11, 0)
    cnt_obj.set_style_border_width(0, 0)
    cnt_lbl = lv.label(cnt_obj)
    cnt_lbl.set_text(str(music_count))
    cnt_lbl.center()
    cnt_lbl.set_style_text_color(color_hex(THEME['accent2']), 0)

    # 歌曲条目（可滚动容器）
    list_container = lv.obj(panel)
    list_container.set_size(SW - 24, SH - 70)
    list_container.set_style_bg_opa(0, 0)
    list_container.set_style_border_width(0, 0)
    list_container.set_style_pad_all(0, 0)
    list_container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
    list_container.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.START)
    list_container.set_scroll_dir(lv.DIR.VER)

    for i, fn in enumerate(music_files):
        btn = lv.btn(list_container)
        btn.set_size(SW - 30, ITEM_H)
        btn.set_style_radius(8, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_shadow_width(0, 0)
        btn.set_style_bg_color(color_hex(THEME['panel2']), 0)
        btn.set_style_bg_opa(76, 0)

        lbl = lv.label(btn)
        lbl.set_text(f"{i+1:02d}  {clip_text(filename_to_title(fn), 12)}")
        lbl.set_style_text_color(color_hex(THEME['subtext']), 0)
        lbl.center()
        # 用 user_data 存 index 便于回调
        btn.set_user_data(lbl)

        def make_cb(idx):
            def cb(e):
                global song_index, progress
                btn_obj = lv.btn.__cast__(e.get_target())
                lbl_obj = lv.label.__cast__(btn_obj.get_user_data())
                if idx < music_count:
                    song_index = idx
                    progress = 0.0
                    switch_song()
                    refresh_song_list_colors()
                    refresh_song_info()
            return cb
        btn.add_event(make_cb(i), lv.EVENT.CLICKED, None)

    song_list_obj = list_container
    refresh_song_list_colors()

def refresh_song_list_colors():
    if song_list_obj is None:
        return
    for j in range(song_list_obj.get_child_cnt()):
        try:
            btn = song_list_obj.get_child(j)
            if not hasattr(btn, 'get_user_data'):
                continue
            lbl = btn.get_user_data()
            if btn and lbl and isinstance(lbl, lv.label):
                pass  # fall through
        except:
            continue
        try:
            lbl = lv.label.__cast__(btn.get_user_data())
            if j == song_index:
                btn.set_style_bg_color(color_hex(THEME['active']), 0)
                btn.set_style_bg_opa(102, 0)
                lbl.set_style_text_color(color_hex(THEME['accent2']), 0)
            else:
                btn.set_style_bg_color(color_hex(THEME['panel2']), 0)
                btn.set_style_bg_opa(76, 0)
                lbl.set_style_text_color(color_hex(THEME['subtext']), 0)
        except:
            pass

# ============================================================
# 顶部歌曲信息
# ============================================================
IX = SX + SW + 20
IW = DISPLAY_WIDTH - IX - 20

song_title_label = None
song_info_label = None
tag_obj = None
tag_text_label = None
idx_label = None

def build_song_info(parent):
    global song_title_label, song_info_label, tag_obj, tag_text_label, idx_label

    np = lv.label(parent)
    np.set_text("NOW PLAYING")
    np.set_pos(IX, 24)
    np.set_style_text_color(color_hex(THEME['accent2']), 0)

    song_title_label = lv.label(parent)
    song_title_label.set_pos(IX, 48)
    song_title_label.set_style_text_color(color_hex(THEME['text']), 0)

    song_info_label = lv.label(parent)
    song_info_label.set_pos(IX, 78)
    song_info_label.set_style_text_color(color_hex(THEME['subtext']), 0)

    # 状态标签
    tag_obj = lv.obj(parent)
    tag_obj.set_size(90, 28)
    tag_obj.set_pos(DISPLAY_WIDTH - 120, 24)
    tag_obj.set_style_radius(14, 0)
    tag_obj.set_style_border_width(0, 0)
    tag_obj.set_style_bg_color(color_hex(THEME['accent']), 0)
    tag_text_label = lv.label(tag_obj)
    tag_text_label.set_text("播放中")
    tag_text_label.center()
    tag_text_label.set_style_text_color(color_hex('#ffffff'), 0)

    idx_label = lv.label(parent)
    idx_label.set_pos(DISPLAY_WIDTH - 120, 58)
    idx_label.set_style_text_color(color_hex(THEME['subtext']), 0)

    refresh_song_info()

def refresh_song_info():
    if music_count == 0:
        if song_title_label:
            song_title_label.set_text("请放入 WAV 文件")
        return
    fn = music_files[song_index]
    if song_title_label:
        song_title_label.set_text(clip_text(filename_to_title(fn), 18))
    if audio_framerate > 0:
        ch = "立体声" if audio_channels >= 2 else "单声道"
        bits = audio_sampwidth * 8
        info = f"{audio_framerate/1000:.1f}kHz  {ch}  {bits}bit  WAV"
    else:
        info = fn
    if song_info_label:
        song_info_label.set_text(info)
    if idx_label:
        idx_label.set_text(f"{song_index+1} / {music_count}")
    refresh_playing_tag()

def refresh_playing_tag():
    if tag_obj is None or tag_text_label is None:
        return
    if IS_DARK:
        bg = color_hex('#ff6f60') if is_playing else color_hex('#26e0be')
    else:
        bg = color_hex('#f05c50') if is_playing else color_hex('#00aa96')
    tag_obj.set_style_bg_color(bg, 0)
    tag_text_label.set_text("播放中" if is_playing else "已暂停")

# ============================================================
# 控制按钮
# ============================================================
BTN_Y = 430
BTN_PLAY_X = 490
BTN_PREV_X = BTN_PLAY_X - 110
BTN_NEXT_X = BTN_PLAY_X + 110

play_btn = None
play_btn_label = None

def build_controls(parent):
    global play_btn, play_btn_label

    # 背景面板
    bg = lv.obj(parent)
    bg.set_size(340, 56)
    bg.set_pos(BTN_PREV_X - 68, BTN_Y - 28)
    bg.set_style_bg_color(color_hex(THEME['panel']), 0)
    bg.set_style_border_width(1, 0)
    bg.set_style_border_color(color_hex(THEME['panel2']), 0)
    bg.set_style_radius(16, 0)

    def _round_btn(x, y, r, ck, txt):
        b = lv.btn(parent)
        b.set_size(r * 2, r * 2)
        b.set_pos(x - r, y - r)
        b.set_style_radius(r, 0)
        b.set_style_bg_color(color_hex(THEME[ck]), 0)
        b.set_style_border_width(0, 0)
        b.set_style_shadow_width(5, 0)
        b.set_style_shadow_ofs_y(3, 0)
        lb = lv.label(b)
        lb.set_text(txt)
        lb.center()
        lb.set_style_text_color(color_hex('#ffffff'), 0)
        return b, lb

    prev_btn, _ = _round_btn(BTN_PREV_X, BTN_Y, 24, 'btn_prev', lv.SYMBOL.PREV)
    play_btn, play_btn_label = _round_btn(
        BTN_PLAY_X, BTN_Y, 30,
        'btn_pause' if is_playing else 'btn_play',
        lv.SYMBOL.PAUSE if is_playing else lv.SYMBOL.PLAY,
    )
    next_btn, _ = _round_btn(BTN_NEXT_X, BTN_Y, 24, 'btn_next', lv.SYMBOL.NEXT)

    def on_prev(e):
        global song_index, progress
        if music_count <= 1:
            progress = 0.0
            audio_seek(0.0)
        else:
            song_index = (song_index - 1) % music_count
            progress = 0.0
            switch_song()
            refresh_song_list_colors()
            refresh_song_info()

    def on_play(e):
        global is_playing
        is_playing = not is_playing
        refresh_play_btn()

    def on_next(e):
        global song_index, progress
        if music_count <= 1:
            progress = 0.0
            audio_seek(0.0)
        else:
            song_index = (song_index + 1) % music_count
            progress = 0.0
            switch_song()
            refresh_song_list_colors()
            refresh_song_info()

    prev_btn.add_event(on_prev, lv.EVENT.CLICKED, None)
    play_btn.add_event(on_play, lv.EVENT.CLICKED, None)
    next_btn.add_event(on_next, lv.EVENT.CLICKED, None)

def refresh_play_btn():
    if play_btn is None or play_btn_label is None:
        return
    if is_playing:
        play_btn.set_style_bg_color(color_hex(THEME['btn_pause']), 0)
        play_btn_label.set_text(lv.SYMBOL.PAUSE)
    else:
        play_btn.set_style_bg_color(color_hex(THEME['btn_play']), 0)
        play_btn_label.set_text(lv.SYMBOL.PLAY)
    refresh_playing_tag()

# ============================================================
# 进度条
# ============================================================
PX, PY = IX + 10, 392
PW = IW - 120
t_cur = None
t_tot = None

def build_progress(parent):
    global progress_slider, t_cur, t_tot

    lb = lv.label(parent)
    lb.set_text("PLAYBACK")
    lb.set_pos(PX, PY - 22)
    lb.set_style_text_color(color_hex(THEME['subtext']), 0)

    progress_slider = lv.slider(parent)
    progress_slider.set_size(PW, 8)
    progress_slider.set_pos(PX, PY)
    progress_slider.set_range(0, 1000)
    progress_slider.set_value(0, lv.ANIM.OFF)
    progress_slider.set_style_bg_color(color_hex(THEME['progress']), 0)
    progress_slider.set_style_bg_color(color_hex(THEME['prog_fg']), lv.PART.INDICATOR)
    progress_slider.set_style_bg_color(color_hex(THEME['prog_fg']), lv.PART.KNOB)

    def pc(e):
        global progress
        r = progress_slider.get_value() / 1000.0
        progress = r
        audio_seek(r)
        _refresh_times()

    progress_slider.add_event(pc, lv.EVENT.VALUE_CHANGED, None)

    t_cur = lv.label(parent)
    t_cur.set_pos(PX, PY + 14)
    t_cur.set_style_text_color(color_hex(THEME['text']), 0)
    t_tot = lv.label(parent)
    t_tot.set_pos(PX + PW - 50, PY + 14)
    t_tot.set_style_text_color(color_hex(THEME['subtext']), 0)
    _refresh_times()

def _refresh_times():
    p = progress_slider.get_value() / 1000.0 if progress_slider else progress
    cs = int(p * audio_total_frames / audio_framerate) if audio_framerate > 0 else 0
    ts = int(audio_total_frames / audio_framerate) if audio_framerate > 0 else 0
    if t_cur:
        t_cur.set_text(f"{cs//60}:{cs%60:02d}")
    if t_tot:
        t_tot.set_text(f"{ts//60}:{ts%60:02d}")

# ============================================================
# 音量控制
# ============================================================
VX, VY, VW, VH = 716, 140, 50, 160

def build_volume(parent):
    global vol_slider

    pnl = lv.obj(parent)
    pnl.set_size(VW, VH)
    pnl.set_pos(VX, VY)
    pnl.set_style_bg_color(color_hex(THEME['panel']), 0)
    pnl.set_style_border_width(1, 0)
    pnl.set_style_border_color(color_hex(THEME['panel2']), 0)
    pnl.set_style_radius(12, 0)

    lb = lv.label(pnl)
    lb.set_text("音量")
    lb.align(lv.ALIGN.TOP_MID, 0, 8)
    lb.set_style_text_color(color_hex(THEME['subtext']), 0)

    vol_slider = lv.slider(pnl)
    vol_slider.set_size(VH - 36, 8)
    vol_slider.align(lv.ALIGN.CENTER, 0, 4)
    vol_slider.set_range(0, 100)
    vol_slider.set_value(volume, lv.ANIM.OFF)
    vol_slider.set_style_bg_color(color_hex(THEME['progress']), 0)
    vol_slider.set_style_bg_color(color_hex(THEME['prog_fg']), lv.PART.INDICATOR)
    vol_slider.set_style_bg_color(color_hex(THEME['accent2']), lv.PART.KNOB)

    def vc(e):
        set_volume(vol_slider.get_value())
    vol_slider.add_event(vc, lv.EVENT.VALUE_CHANGED, None)

# ============================================================
# 均衡器 (lv.bar)
# ============================================================
EQ_X, EQ_Y = IX + 10, 330
EQ_BW, EQ_GAP, EQ_MH = 12, 4, 36

def build_equalizer(parent):
    global eq_bars

    lb = lv.label(parent)
    lb.set_text("SPECTRUM")
    lb.set_pos(EQ_X, EQ_Y - 22)
    lb.set_style_text_color(color_hex(THEME['subtext']), 0)

    for i in range(EQ_COUNT):
        b = lv.bar(parent)
        b.set_size(EQ_BW, EQ_MH)
        b.set_pos(EQ_X + i * (EQ_BW + EQ_GAP), EQ_Y)
        b.set_range(0, 100)
        b.set_value(0, lv.ANIM.OFF)
        b.set_style_bg_color(color_hex(THEME['progress']), 0)
        b.set_style_radius(3, 0)
        b.set_style_radius(3, lv.PART.INDICATOR)
        if i < EQ_COUNT // 3:
            c = color_hex(THEME['accent2'])
        elif i < EQ_COUNT * 2 // 3:
            c = lv.color_hex(0x4695F5)
        else:
            c = color_hex(THEME['accent'])
        b.set_style_bg_color(c, lv.PART.INDICATOR)
        eq_bars.append(b)

# ============================================================
# 主题 / 退出按钮
# ============================================================
TX, TY, TW, TH = 660, 74, 90, 30
EX, EY, EW, EH = 660, 30, 90, 30

def build_top_btns(parent):
    # 退出
    eb = lv.btn(parent)
    eb.set_size(EW, EH)
    eb.set_pos(EX, EY)
    eb.set_style_radius(EH // 2, 0)
    eb.set_style_bg_color(color_hex(THEME['accent']), 0)
    eb.set_style_border_width(0, 0)
    el = lv.label(eb)
    el.set_text("退出")
    el.center()
    el.set_style_text_color(color_hex('#ffffff'), 0)

    def on_exit(e):
        global player_should_exit
        player_should_exit = True
    eb.add_event(on_exit, lv.EVENT.CLICKED, None)

    # 主题
    tb = lv.btn(parent)
    tb.set_size(TW, TH)
    tb.set_pos(TX, TY)
    tb.set_style_radius(TH // 2, 0)
    tb.set_style_bg_color(lv.color_hex(0x1A2637), 0)
    tb.set_style_border_width(0, 0)
    tl = lv.label(tb)
    tl.set_text("浅色")
    tl.center()
    tl.set_style_text_color(lv.color_hex(0xF6FAFF), 0)

    def on_theme(e):
        global IS_DARK, THEME
        IS_DARK = not IS_DARK
        THEME = dict(DARK if IS_DARK else LIGHT)
        tb.set_style_bg_color(lv.color_hex(0x1A2637) if IS_DARK else lv.color_hex(0xF2F7FC), 0)
        tl.set_text("浅色" if IS_DARK else "深色")
        tl.set_style_text_color(lv.color_hex(0xF6FAFF) if IS_DARK else lv.color_hex(0x1A2637), 0)
        lv.scr_act().set_style_bg_color(color_hex(THEME['bg']), 0)

    tb.add_event(on_theme, lv.EVENT.CLICKED, None)

# ============================================================
# 唱片装饰（静态 LVGL 对象模拟）
# ============================================================
def build_vinyl(parent):
    RCX, RCY, RR = 380, 204, 90

    # 背景圆（深色）
    bg = lv.obj(parent)
    bg.set_size(RR * 2 + 40, RR * 2 + 40)
    bg.set_pos(RCX - RR - 20, RCY - RR - 20)
    bg.set_style_bg_color(lv.color_hex(0x0F121C), 0)
    bg.set_style_radius(RR + 20, 0)
    bg.set_style_border_width(0, 0)
    bg.set_style_shadow_width(20, 0)
    bg.set_style_shadow_color(lv.color_hex(0x000000), 0)
    bg.set_style_shadow_ofs_x(4, 0)
    bg.set_style_shadow_ofs_y(6, 0)

    # 内圆（标签）
    lbl = lv.obj(parent)
    lbl.set_size(60, 60)
    lbl.set_pos(RCX - 30, RCY - 30)
    lbl.set_style_bg_color(color_hex(THEME['btn_play']), 0)
    lbl.set_style_radius(30, 0)
    lbl.set_style_border_width(0, 0)
    lt = lv.label(lbl)
    lt.set_text("MUSIC")
    lt.center()
    lt.set_style_text_color(lv.color_hex(0xFFFFFF), 0)

# ============================================================
# 构建全部 UI
# ============================================================
def build_ui():
    scr = lv.scr_act()
    scr.set_style_bg_color(color_hex(THEME['bg']), 0)

    build_song_list(scr)
    build_song_info(scr)
    build_vinyl(scr)
    build_equalizer(scr)
    build_progress(scr)
    build_volume(scr)
    build_controls(scr)
    build_top_btns(scr)

# ============================================================
# 状态更新
# ============================================================
def update_state():
    global progress, song_index, last_eq_update

    # 音频播放
    if is_playing and audio_stream and audio_wf:
        has, cf = audio_play_chunk()
        if audio_total_frames > 0:
            progress = cf / audio_total_frames
        if not has:
            if music_count > 1:
                song_index = (song_index + 1) % music_count
            progress = 0.0
            switch_song()
            refresh_song_list_colors()
            refresh_song_info()

    # 进度条
    if progress_slider:
        tv = int(progress * 1000)
        cv = progress_slider.get_value()
        if abs(cv - tv) > 5:
            progress_slider.set_value(tv, lv.ANIM.OFF)
    _refresh_times()

    # 均衡器
    if is_playing and audio_stream:
        _update_eq(volume / 100.0)

def _update_eq(vf):
    global last_eq_update
    now = time.ticks_ms()
    if time.ticks_diff(now, last_eq_update) > 80:
        last_eq_update = now
        for i in range(EQ_COUNT):
            eq_phase[i] += 0.3 + urandom.getrandbits(6) / 255.0 * 0.5
            base = 0.2 + 0.8 * abs(math.sin(eq_phase[i]))
            noise = urandom.getrandbits(7) / 255.0 * 0.4 * vf
            eq_targets[i] = min(1.0, base * 0.6 * vf + 0.05 + noise)
    else:
        for i in range(EQ_COUNT):
            eq_targets[i] = max(0.02, eq_targets[i] * 0.90)
    for i in range(EQ_COUNT):
        eq_heights[i] += (eq_targets[i] - eq_heights[i]) * 0.25
        if i < len(eq_bars):
            eq_bars[i].set_value(int(eq_heights[i] * 100), lv.ANIM.OFF)

# ============================================================
# 主函数
# ============================================================
def main():
    global music_files, music_count, song_index, progress
    global player_should_exit, is_playing

    print("=" * 50)
    print("  LVGL 触摸屏 WAV 音乐播放器 (K230D)")
    print("=" * 50)

    print("[1/6] 功放初始化...")
    try:
        init_amp()
    except Exception as e:
        print(f"  功放跳过: {e}")

    print("[2/6] 显示屏初始化...")
    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)

    # 文件扫描必须在 LVGL 之前！LVGL 分配大缓冲区后 os.listdir 会卡死
    print("[3/6] 扫描音乐文件...")
    music_files = []
    try:
        files = os.listdir(MUSIC_DIR)
        for f in files:
            if f.lower().endswith('.wav'):
                music_files.append(f)
        music_files.sort()
    except Exception as e:
        print(f"  扫描异常: {e}")
    music_count = len(music_files)

    print("[4/6] LVGL 初始化...")
    try:
        lvgl_init()
    except Exception as e:
        sys.print_exception(e)
        raise

    print("[5/6] 触摸屏初始化...")
    try:
        tp = TouchScreen()
    except Exception as e:
        print(f"  触摸跳过: {e}")
        tp = None
    song_index = 0
    progress = 0.0
    player_should_exit = False

    print(f"  目录: {MUSIC_DIR}, 找到 {music_count} 首 WAV 文件")
    for i, f in enumerate(music_files):
        print(f"  {'→' if i == 0 else ' '} [{i+1}] {f}")

    print("[6/6] 构建 LVGL UI...")
    build_ui()
    print("  UI 构建完成")

    if music_count > 0:
        switch_song()

    try:
        while True:
            os.exitpoint()
            update_state()
            time.sleep_ms(max(lv.task_handler(), 10))
            if player_should_exit:
                print("退出音乐播放器")
                break
    except KeyboardInterrupt:
        print("用户停止")
    except BaseException as e:
        sys.print_exception(e)
    finally:
        audio_close()
        try:
            if HT_CTRL:
                HT_CTRL.low()
        except:
            pass
        lv.deinit()
        Display.deinit()
        gc.collect()

if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()
