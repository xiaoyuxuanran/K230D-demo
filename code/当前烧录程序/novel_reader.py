# 小说阅读器 - 立创·庐山派-K230-CanMV
# TXT读取、上下翻页、进度记忆

import os, time, image
from media.display import *
from media.media import *
from machine import TOUCH

# ============================================================
# 参数
# ============================================================
DISPLAY_WIDTH  = 800
DISPLAY_HEIGHT = 480
DOC_DIR        = "/data/code/doc"
PROGRESS_FILE  = DOC_DIR + "/doc_read.txt"

FONT_SIZE   = 18
LINE_HEIGHT = 22
MARGIN_L    = 50   # 左侧翻页触摸区
MARGIN_R    = 50   # 右侧翻页触摸区
TOP_BAR_H   = 44
BOT_BAR_H   = 30

# 文本区域
TEXT_X   = MARGIN_L
TEXT_Y   = TOP_BAR_H + 6
TEXT_W   = DISPLAY_WIDTH - MARGIN_L - MARGIN_R
TEXT_H   = DISPLAY_HEIGHT - TOP_BAR_H - BOT_BAR_H - 12
CHARS_PER_LINE = TEXT_W // FONT_SIZE
LINES_PER_PAGE = TEXT_H // LINE_HEIGHT

# 网格布局（仿主页面图标风格）
GRID_COLS = 2
GRID_ROWS = 3
TILE_W = 360
TILE_H = 120
TILE_GAP = 15
GRID_X = (DISPLAY_WIDTH - (TILE_W * GRID_COLS + TILE_GAP * (GRID_COLS - 1))) // 2
GRID_Y = 60
PER_PAGE = GRID_COLS * GRID_ROWS

# ============================================================
# 进度读写
# ============================================================
def ensure_dir():
    try:
        os.stat(DOC_DIR)
    except:
        os.mkdir(DOC_DIR)

def load_progress():
    """读取进度文件，返回 {filename: page_num}"""
    prog = {}
    try:
        with open(PROGRESS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    fn, pg = line.split('=', 1)
                    prog[fn.strip()] = int(pg.strip())
    except:
        pass
    return prog

def save_progress(filename, page, total):
    """保存单个文件进度"""
    prog = load_progress()
    prog[filename] = page
    try:
        with open(PROGRESS_FILE, 'w') as f:
            for fn, pg in prog.items():
                f.write(fn + "=" + str(pg) + "\n")
    except:
        pass

# ============================================================
# 文本分页
# ============================================================
def split_pages(text):
    """将文本按屏幕尺寸分页，返回页面列表"""
    pages = []
    lines = []
    # 按换行符拆分，每行按字符宽度截断
    for paragraph in text.split('\n'):
        para = paragraph.rstrip()
        if not para:
            lines.append('')
            continue
        # 长行截断
        while len(para) > 0:
            lines.append(para[:CHARS_PER_LINE])
            para = para[CHARS_PER_LINE:]

    # 按每页行数分页
    for i in range(0, len(lines), LINES_PER_PAGE):
        page = lines[i:i + LINES_PER_PAGE]
        pages.append(page)
    return pages

def read_file_text(filepath):
    """读取文件文本，尝试 UTF-8 和 GBK"""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
    except:
        return ""

    # 跳过 BOM
    if data[:3] == b'\xef\xbb\xbf':
        data = data[3:]
    elif data[:2] == b'\xff\xfe':
        data = data[2:]

    # 尝试 UTF-8
    try:
        return data.decode('utf-8')
    except:
        pass
    # 尝试 GBK
    try:
        return data.decode('gbk')
    except:
        pass
    # 回退
    return data.decode('utf-8', 'ignore')

# ============================================================
# 触摸
# ============================================================
def in_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx + rw and ry <= py <= ry + rh

# ============================================================
# 绘制 — 小说列表
# ============================================================
def scan_novels():
    files = []
    try:
        for f in os.listdir(DOC_DIR):
            if f.lower().endswith('.txt') and f != "doc_read.txt":
                files.append(f)
        files.sort()
    except:
        pass
    return files

def draw_novel_grid(img, novels, page):
    img.clear()
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, color=(248, 245, 240), fill=True)

    # 标题栏
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, TOP_BAR_H, color=(230, 225, 215), fill=True)
    img.draw_string_advanced(20, 10, 20, "小说阅读器", color=(50, 45, 35))

    # 退出
    img.draw_rectangle(660, 4, 130, 38, color=(220, 80, 60), fill=True)
    img.draw_string_advanced(680, 11, 18, "退出", color=(255, 255, 255))

    if not novels:
        img.draw_string_advanced(240, 180, 20, "暂无小说文件", color=(160, 155, 140))
        img.draw_string_advanced(160, 220, 14,
                                 "请将 .txt 文件放入 " + DOC_DIR, color=(140, 135, 120))
        return

    prog = load_progress()
    start = page * PER_PAGE
    for i in range(PER_PAGE):
        idx = start + i
        if idx >= len(novels):
            break
        fn = novels[idx]
        col = i % GRID_COLS
        row = i // GRID_COLS
        tx = GRID_X + col * (TILE_W + TILE_GAP)
        ty = GRID_Y + row * (TILE_H + TILE_GAP)

        # 卡片
        img.draw_rectangle(tx, ty, TILE_W, TILE_H, color=(252, 250, 248), fill=True)
        img.draw_rectangle(tx, ty, TILE_W, TILE_H, color=(180, 175, 165), thickness=1, fill=False)

        # 图标区域（小装饰）
        icon_x = tx + 16
        icon_y = ty + 16
        img.draw_rectangle(icon_x, icon_y, 50, 50, color=(220, 215, 200), fill=True)
        img.draw_rectangle(icon_x, icon_y, 50, 50, color=(190, 185, 170), thickness=1, fill=False)
        # 模拟书本线条
        for li in range(4):
            ly = icon_y + 10 + li * 10
            img.draw_line(icon_x + 8, ly, icon_x + 42, ly, color=(160, 155, 140))

        # 书名
        name = fn.replace('.txt', '')
        short = name if len(name) <= 18 else name[:16] + ".."
        img.draw_string_advanced(tx + 80, ty + 18, 20, short, color=(50, 45, 35))

        # 进度
        if fn in prog:
            pstr = "进度: " + str(prog[fn]) + " 页"
            img.draw_string_advanced(tx + 80, ty + 50, 14, pstr, color=(80, 180, 120))
        else:
            img.draw_string_advanced(tx + 80, ty + 50, 14, "新书", color=(160, 155, 140))

        # 提示
        img.draw_string_advanced(tx + 80, ty + 80, 13, "点击阅读 >", color=(140, 160, 200))

    # 底部翻页
    total_pages = max(1, (len(novels) + PER_PAGE - 1) // PER_PAGE)
    pg_str = str(page + 1) + " / " + str(total_pages)
    img.draw_string_advanced(DISPLAY_WIDTH // 2 - 20, DISPLAY_HEIGHT - 30, 14, pg_str, color=(140, 135, 120))
    if page > 0:
        img.draw_rectangle(20, DISPLAY_HEIGHT - 40, 120, 34, color=(200, 195, 180), fill=True)
        img.draw_string_advanced(40, DISPLAY_HEIGHT - 34, 16, "▲ 上一页", color=(80, 75, 60))
    if page < total_pages - 1:
        img.draw_rectangle(660, DISPLAY_HEIGHT - 40, 120, 34, color=(200, 195, 180), fill=True)
        img.draw_string_advanced(680, DISPLAY_HEIGHT - 34, 16, "▼ 下一页", color=(80, 75, 60))

# ============================================================
# 绘制 — 阅读界面
# ============================================================
def draw_reading(img, filename, pages, cur_page):
    total = len(pages)
    img.clear()
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, color=(252, 250, 245), fill=True)

    # 顶部
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, TOP_BAR_H, color=(235, 230, 220), fill=True)
    short = filename.replace('.txt', '')
    if len(short) > 16:
        short = short[:14] + ".."
    title = short + "  " + str(cur_page + 1) + "/" + str(total)
    img.draw_string_advanced(20, 10, 16, title, color=(60, 55, 40))

    # 返回列表（大按钮）
    img.draw_rectangle(600, 4, 190, 38, color=(100, 140, 200), fill=True)
    img.draw_string_advanced(612, 10, 20, "← 返回列表", color=(255, 255, 255))

    # 文本内容
    if cur_page < total:
        for li, line in enumerate(pages[cur_page]):
            img.draw_string_advanced(TEXT_X, TEXT_Y + li * LINE_HEIGHT,
                                     FONT_SIZE, line, color=(50, 45, 30))

    # 底部进度
    bot_y = DISPLAY_HEIGHT - BOT_BAR_H
    img.draw_rectangle(0, bot_y, DISPLAY_WIDTH, BOT_BAR_H, color=(235, 230, 220), fill=True)
    if total > 1:
        pct = str((cur_page + 1) * 100 // total) + "%"
        img.draw_string_advanced(DISPLAY_WIDTH // 2 - 20, bot_y + 6, 14, pct, color=(140, 135, 120))

    # ── 左右大翻页按钮 ──
    # 左：上一页
    img.draw_rectangle(2, TOP_BAR_H + 20, 42, 240, color=(200, 195, 180), fill=True)
    img.draw_string_advanced(8, DISPLAY_HEIGHT // 2 - 18, 22, "◀", color=(100, 120, 180))
    # 右：下一页
    img.draw_rectangle(DISPLAY_WIDTH - 44, TOP_BAR_H + 20, 42, 240, color=(200, 195, 180), fill=True)
    img.draw_string_advanced(DISPLAY_WIDTH - 38, DISPLAY_HEIGHT // 2 - 18, 22, "▶", color=(100, 120, 180))

# ============================================================
# 主循环
# ============================================================
def main():
    ensure_dir()
    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    MediaManager.init()
    tp = TOUCH(0)

    prog = load_progress()
    novels = scan_novels()

    # 状态
    screen = 'grid'     # 'grid' | 'reading'
    cur_novel = ""
    pages = []
    cur_page = 0
    grid_page = 0
    last_page = -1      # 用于检测页面变化，仅在变化时重绘

    pressed = False
    debounce = 0

    print("[小说] 启动, " + str(len(novels)) + " 本小说")

    try:
        while True:
            os.exitpoint()
            now = time.ticks_ms()

            points = tp.read(5)
            page_changed = False

            if points:
                if not pressed:
                    pt = points[0]
                    x, y = pt.x, pt.y
                    if time.ticks_diff(now, debounce) < 0:
                        pressed = True
                        continue

                    if screen == 'grid':
                        # 退出
                        if in_rect(x, y, 650, 0, 150, 50):
                            print("[小说] 退出")
                            break

                        # 网格图标点击
                        start = grid_page * PER_PAGE
                        for i in range(PER_PAGE):
                            idx = start + i
                            if idx >= len(novels):
                                break
                            col = i % GRID_COLS
                            row = i // GRID_COLS
                            tx = GRID_X + col * (TILE_W + TILE_GAP)
                            ty = GRID_Y + row * (TILE_H + TILE_GAP)
                            if in_rect(x, y, tx - 4, ty - 4, TILE_W + 8, TILE_H + 8):
                                cur_novel = novels[idx]
                                # 显示加载中
                                load_img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
                                load_img.draw_rectangle(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT,
                                                        color=(252, 250, 245), fill=True)
                                load_img.draw_string_advanced(280, 220, 20, "正在加载...",
                                                              color=(120, 115, 100))
                                Display.show_image(load_img)

                                text = read_file_text(DOC_DIR + "/" + cur_novel)
                                pages = split_pages(text)
                                cur_page = prog.get(cur_novel, 0)
                                if cur_page >= len(pages):
                                    cur_page = 0
                                last_page = -1
                                screen = 'reading'
                                debounce = time.ticks_add(now, 500)
                                break

                        # 网格翻页
                        if in_rect(x, y, 10, DISPLAY_HEIGHT - 46, 140, 46) and grid_page > 0:
                            grid_page = max(0, grid_page - 1)
                            debounce = time.ticks_add(now, 300)
                        if in_rect(x, y, 650, DISPLAY_HEIGHT - 46, 140, 46) and (grid_page + 1) * PER_PAGE < len(novels):
                            grid_page += 1
                            debounce = time.ticks_add(now, 300)

                    elif screen == 'reading':
                        # 返回列表
                        if in_rect(x, y, 590, 0, 210, 50):
                            save_progress(cur_novel, cur_page, len(pages))
                            screen = 'grid'
                            last_page = -1
                            debounce = time.ticks_add(now, 400)
                            continue

                        # 上一页
                        if x < 55 and cur_page > 0:
                            cur_page -= 1
                            page_changed = True
                            debounce = time.ticks_add(now, 200)
                            continue

                        # 下一页（右侧+中间）
                        if cur_page < len(pages) - 1:
                            cur_page += 1
                            page_changed = True
                            debounce = time.ticks_add(now, 200)
                            continue

                    debounce = time.ticks_add(now, 150)
                    pressed = True
            else:
                pressed = False

            # 仅在页面变化或首次显示时重绘
            if screen == 'reading':
                if page_changed or last_page != cur_page:
                    img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
                    draw_reading(img, cur_novel, pages, cur_page)
                    Display.show_image(img)
                    last_page = cur_page
                time.sleep_ms(30)
            else:
                img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
                draw_novel_grid(img, novels, grid_page)
                Display.show_image(img)
                time.sleep_ms(80)

    except KeyboardInterrupt:
        print("[小说] 用户停止")
    except BaseException as e:
        print("[小说] 异常: " + str(e))
        import sys
        sys.print_exception(e)
    finally:
        if screen == 'reading' and cur_novel:
            save_progress(cur_novel, cur_page, len(pages))
        Display.deinit()
        time.sleep_ms(60)
        MediaManager.deinit()

if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()
