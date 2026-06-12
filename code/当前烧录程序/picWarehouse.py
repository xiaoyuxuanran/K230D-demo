# 相册功能 - 立创·庐山派-K230-CanMV
# 列表浏览 / 全屏查看 / 上一张下一张

import os, time, image
from media.display import *
from media.media import *
from machine import TOUCH

# ============================================================
# 参数
# ============================================================
DISPLAY_WIDTH  = 800
DISPLAY_HEIGHT = 480
PHOTO_DIR      = "/data/code/picture"

# 列表布局
LIST_X, LIST_Y, LIST_W = 20, 55, 660
ITEM_H = 64
ITEM_GAP = 4
VISIBLE_MAX = 5  # 一屏 5 个，底部留空间给翻页按钮

# 翻页按钮（底部独立区域）
PAGE_Y = 430
PREV_BTN = (20, PAGE_Y, 140, 40)
NEXT_BTN = (640, PAGE_Y, 140, 40)

# 退出按钮
EXIT_BTN = (660, 10, 126, 40)

# 全屏按钮
FS_EXIT_BTN  = (640, 4, 150, 44)
FS_PREV_BTN  = (6, DISPLAY_HEIGHT - 46, 160, 42)
FS_NEXT_BTN  = (634, DISPLAY_HEIGHT - 46, 160, 42)

# ============================================================
# 全局
# ============================================================
tp = None
app_should_exit = False
photo_files = []
total_photos = 0
fullscreen_idx = -1
list_scroll = 0

# ============================================================
# 文件扫描
# ============================================================
def scan_photos():
    global photo_files, total_photos
    photo_files = []
    try:
        for f in os.listdir(PHOTO_DIR):
            low = f.lower()
            if low.endswith('.jpg') or low.endswith('.jpeg') or low.endswith('.png'):
                photo_files.append(f)
        photo_files.sort()
    except:
        pass
    total_photos = len(photo_files)

# ============================================================
# 触摸
# ============================================================
_touch_pressed = False
_debounce_until = 0
_startup_lock = 0

def in_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx + rw and ry <= py <= ry + rh

def reset_touch_state():
    global _touch_pressed, _debounce_until
    _touch_pressed = False
    _debounce_until = 0

def handle_touch_gallery(points):
    global app_should_exit, fullscreen_idx, list_scroll
    global _touch_pressed, _debounce_until

    now = time.ticks_ms()
    if time.ticks_diff(now, _startup_lock) < 0:
        return
    if not points:
        _touch_pressed = False
        return
    if time.ticks_diff(now, _debounce_until) < 0:
        return

    pt = points[0]
    x, y = pt.x, pt.y
    is_down = not _touch_pressed
    _touch_pressed = True
    if not is_down:
        return

    # 退出（优先检测）
    if in_rect(x, y, *EXIT_BTN):
        app_should_exit = True
        _debounce_until = time.ticks_add(now, 400)
        return

    # 上一页
    if list_scroll > 0 and in_rect(x, y, *PREV_BTN):
        list_scroll = max(0, list_scroll - VISIBLE_MAX)
        _debounce_until = time.ticks_add(now, 400)
        return

    # 下一页
    if list_scroll + VISIBLE_MAX < total_photos and in_rect(x, y, *NEXT_BTN):
        list_scroll = min(total_photos - VISIBLE_MAX, list_scroll + VISIBLE_MAX)
        _debounce_until = time.ticks_add(now, 400)
        return

    # 列表项（最后检测，避免误吞翻页按钮）
    visible = min(VISIBLE_MAX, total_photos - list_scroll)
    for i in range(visible):
        idx = list_scroll + i
        if idx >= total_photos:
            break
        iy = LIST_Y + i * (ITEM_H + ITEM_GAP)
        if in_rect(x, y, LIST_X, iy, LIST_W, ITEM_H):
            fullscreen_idx = idx
            _debounce_until = time.ticks_add(now, 500)
            reset_touch_state()
            return

def handle_touch_fullscreen(points):
    global fullscreen_idx
    global _touch_pressed, _debounce_until

    now = time.ticks_ms()
    if not points:
        _touch_pressed = False
        return
    if time.ticks_diff(now, _debounce_until) < 0:
        return

    pt = points[0]
    x, y = pt.x, pt.y
    is_down = not _touch_pressed
    _touch_pressed = True
    if not is_down:
        return

    # 退出全屏
    if in_rect(x, y, *FS_EXIT_BTN):
        fullscreen_idx = -1
        _debounce_until = time.ticks_add(now, 500)
        _startup_lock = time.ticks_add(now, 400)
        reset_touch_state()
        return

    # 上一张
    if total_photos > 0 and in_rect(x, y, *FS_PREV_BTN):
        fullscreen_idx = (fullscreen_idx - 1) % total_photos
        _debounce_until = time.ticks_add(now, 350)
        return

    # 下一张
    if total_photos > 0 and in_rect(x, y, *FS_NEXT_BTN):
        fullscreen_idx = (fullscreen_idx + 1) % total_photos
        _debounce_until = time.ticks_add(now, 350)
        return

# ============================================================
# 绘制 — 列表浏览
# ============================================================
def _draw_photo_icon(img, x, y, w, h):
    icon_margin = 4
    ix, iy = x + icon_margin, y + icon_margin
    iw, ih = w - icon_margin * 2, h - icon_margin * 2
    img.draw_rectangle(ix, iy, iw, ih, color=(55, 65, 90), fill=True)
    img.draw_rectangle(ix, iy, iw, ih, color=(90, 100, 130), thickness=1, fill=False)
    cx, cy = ix + iw // 2, iy + ih // 2
    sr = max(5, iw // 12)
    img.draw_circle(ix + iw - sr - 6, iy + sr + 4, sr, color=(255, 220, 140), thickness=2, fill=True)
    mx1, my1 = ix + iw // 4,  iy + ih - 5
    mx2, my2 = cx,            iy + ih // 3
    mx3, my3 = ix + iw * 3 // 4, iy + ih - 5
    img.draw_line(mx1, my1, mx2, my2, color=(80, 160, 100), thickness=2)
    img.draw_line(mx2, my2, mx3, my3, color=(80, 160, 100), thickness=2)
    img.draw_line(mx1, my1, mx3, my3, color=(60, 140, 80), thickness=2)

def draw_gallery(img):
    img.clear()
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, color=(18, 20, 32), fill=True)

    # 标题栏
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, 50, color=(28, 31, 46), fill=True)
    img.draw_string_advanced(20, 12, 20, "相册", color=(255, 255, 255))
    cnt_text = str(total_photos) + " 张照片"
    img.draw_string_advanced(110, 16, 14, cnt_text, color=(160, 165, 180))

    # 退出按钮
    eb = EXIT_BTN
    img.draw_rectangle(*eb, color=(220, 60, 50), fill=True)
    img.draw_string_advanced(eb[0] + 30, eb[1] + 10, 18, "退出", color=(255, 255, 255))

    if total_photos == 0:
        img.draw_string_advanced(250, 200, 20, "暂无照片", color=(140, 145, 160))
        img.draw_string_advanced(200, 240, 14, "请使用相机功能拍摄照片", color=(120, 125, 140))
        return

    # 照片列表（5 行，不超出翻页按钮区）
    visible = min(VISIBLE_MAX, total_photos - list_scroll)
    for i in range(visible):
        idx = list_scroll + i
        iy = LIST_Y + i * (ITEM_H + ITEM_GAP)
        bg = (36, 39, 55) if idx % 2 == 1 else (28, 31, 46)
        img.draw_rectangle(LIST_X, iy, LIST_W, ITEM_H, color=bg, fill=True)
        img.draw_rectangle(LIST_X, iy, LIST_W, ITEM_H, color=(50, 54, 72), thickness=1, fill=False)

        icon_w = 48
        _draw_photo_icon(img, LIST_X + 6, iy + 4, icon_w, ITEM_H - 8)
        num = "%02d" % (idx + 1)
        img.draw_string_advanced(LIST_X + 60, iy + 10, 18, num, color=(200, 205, 220))
        fname = photo_files[idx]
        short = fname if len(fname) <= 30 else fname[:28] + ".."
        img.draw_string_advanced(LIST_X + 94, iy + 22, 13, short, color=(160, 165, 180))
        img.draw_string_advanced(LIST_X + LIST_W - 68, iy + 22, 13, "查看 >", color=(100, 160, 210))

    # ── 底部翻页按钮（独立区域，不与列表重叠） ──
    page_str = str(list_scroll // VISIBLE_MAX + 1) + " / " + str(max(1, (total_photos + VISIBLE_MAX - 1) // VISIBLE_MAX))
    pw = len(page_str) * 12
    img.draw_string_advanced((800 - pw) // 2, PAGE_Y + 12, 14, page_str, color=(140, 145, 160))

    if list_scroll > 0:
        pb = PREV_BTN
        img.draw_rectangle(*pb, color=(45, 55, 75), fill=True)
        img.draw_rectangle(*pb, color=(80, 90, 110), thickness=1, fill=False)
        img.draw_string_advanced(pb[0] + 28, pb[1] + 10, 18, "▲ 上一页", color=(200, 210, 230))

    if list_scroll + VISIBLE_MAX < total_photos:
        nb = NEXT_BTN
        img.draw_rectangle(*nb, color=(45, 55, 75), fill=True)
        img.draw_rectangle(*nb, color=(80, 90, 110), thickness=1, fill=False)
        img.draw_string_advanced(nb[0] + 28, nb[1] + 10, 18, "▼ 下一页", color=(200, 210, 230))

# ============================================================
# 绘制 — 全屏查看
# ============================================================
def draw_fullscreen():
    filepath = PHOTO_DIR + "/" + photo_files[fullscreen_idx]

    # 底层照片
    try:
        photo = image.Image(filepath)
        Display.show_image(photo.to_rgb565(), layer=Display.LAYER_OSD0)
    except Exception as e:
        print("[相册] 加载失败: " + str(e))

    # 顶层 UI
    ui = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
    ui.clear()

    # 顶部条
    ui.draw_rectangle(0, 0, DISPLAY_WIDTH, 48, color=(0, 0, 0, 180), fill=True)
    short = photo_files[fullscreen_idx]
    if len(short) > 24:
        short = short[:22] + ".."
    ui.draw_string_advanced(10, 12, 16, short, color=(255, 255, 255))
    idx_str = str(fullscreen_idx + 1) + " / " + str(total_photos)
    ui.draw_string_advanced(330, 12, 16, idx_str, color=(200, 205, 220))

    # 退出全屏
    fb = FS_EXIT_BTN
    ui.draw_rectangle(*fb, color=(220, 60, 50), fill=True)
    ui.draw_string_advanced(fb[0] + 14, fb[1] + 10, 18, "退出全屏", color=(255, 255, 255))

    # 底部条
    ui.draw_rectangle(0, DISPLAY_HEIGHT - 50, DISPLAY_WIDTH, 50, color=(0, 0, 0, 180), fill=True)

    # 上一张按钮
    pb = FS_PREV_BTN
    ui.draw_rectangle(*pb, color=(50, 100, 180), fill=True)
    ui.draw_string_advanced(pb[0] + 14, pb[1] + 9, 20, "◀ 上一张", color=(255, 255, 255))

    # 下一张按钮
    nb = FS_NEXT_BTN
    ui.draw_rectangle(*nb, color=(50, 100, 180), fill=True)
    ui.draw_string_advanced(nb[0] + 14, nb[1] + 9, 20, "下一张 ▶", color=(255, 255, 255))

    Display.show_image(ui, layer=Display.LAYER_OSD1)

# ============================================================
# 主循环
# ============================================================
def main():
    global tp, app_should_exit, fullscreen_idx, list_scroll
    global _touch_pressed, _debounce_until, _startup_lock

    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    MediaManager.init()
    tp = TOUCH(0)

    scan_photos()
    app_should_exit = False
    fullscreen_idx = -1
    list_scroll = 0
    _touch_pressed = False
    _debounce_until = 0
    _startup_lock = time.ticks_add(time.ticks_ms(), 500)

    print("[相册] 启动, " + str(total_photos) + " 张照片")

    try:
        while True:
            os.exitpoint()

            points = tp.read(5)

            if fullscreen_idx >= 0:
                handle_touch_fullscreen(points)
            else:
                handle_touch_gallery(points)

            if app_should_exit:
                print("[相册] 退出")
                break

            if fullscreen_idx >= 0:
                draw_fullscreen()
            else:
                img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
                draw_gallery(img)
                Display.show_image(img)

            time.sleep_ms(40)

    except KeyboardInterrupt:
        print("[相册] 用户停止")
    except BaseException as e:
        print("[相册] 异常: " + str(e))
        import sys
        sys.print_exception(e)
    finally:
        Display.deinit()
        time.sleep_ms(60)
        MediaManager.deinit()

if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()
