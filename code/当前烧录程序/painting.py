# 画板功能 - 立创·庐山派-K230-CanMV
# 触摸绘画、随机颜色、清除画布、保存、退出（四角大按钮）

import os, time, urandom, image
from media.display import *
from media.media import *
from machine import TOUCH
from machine import PWM
from machine import FPIOA

# ============================================================
# 参数
# ============================================================
DISPLAY_WIDTH  = 800
DISPLAY_HEIGHT = 480
SAVE_DIR       = "/data/code/picture"
BUZZER_PIN     = 61

# 四角大按钮（分散布局，放大触摸区域）
COLOR_BTN = (10,   8,   150, 44)   # 左上：随机颜色
EXIT_BTN  = (630,  8,   160, 44)   # 右上：退出
CLEAR_BTN = (10,   430, 130, 44)   # 左下：清除
SAVE_BTN  = (650,  430, 140, 44)   # 右下：保存

# ============================================================
# 蜂鸣器
# ============================================================
_beep_pwm = None
_fpioa_done = False

def beep_init():
    global _beep_pwm, _fpioa_done
    if _beep_pwm is not None:
        return
    if not _fpioa_done:
        fpioa = FPIOA()
        fpioa.set_function(BUZZER_PIN, FPIOA.PWM1)
        _fpioa_done = True
    _beep_pwm = PWM(1)
    _beep_pwm.freq(4000)

def beep():
    if _beep_pwm is None:
        return
    try:
        _beep_pwm.duty_u16(32768)
        time.sleep_ms(80)
        _beep_pwm.duty_u16(0)
    except:
        pass

def beep_deinit():
    global _beep_pwm
    if _beep_pwm:
        try:
            _beep_pwm.duty_u16(0)
            _beep_pwm.deinit()
        except:
            pass
        _beep_pwm = None

# ============================================================
# 保存
# ============================================================
def ensure_dir():
    try:
        os.stat(SAVE_DIR)
    except:
        os.mkdir(SAVE_DIR)

def get_next_name():
    try:
        files = [f for f in os.listdir(SAVE_DIR)
                 if f.startswith("painting_") and f.endswith(".jpg")]
        nums = []
        for f in files:
            try:
                nums.append(int(f[9:14]))
            except:
                pass
        n = max(nums) + 1 if nums else 1
    except:
        n = 1
    return SAVE_DIR + "/painting_" + ("%05d" % n) + ".jpg"

def save_canvas(img):
    ensure_dir()
    filename = get_next_name()
    try:
        data = img.compress(quality=95)
        with open(filename, "wb") as f:
            f.write(data)
        beep()
        print("[画板] 已保存: " + filename)
    except Exception as e:
        print("[画板] 保存失败: " + str(e))

# ============================================================
# 全局
# ============================================================
tp = None
app_should_exit = False
current_color = (0, 255, 0)
brush_size = 10
last_point = None
_debounce_until = 0

# ============================================================
# 触摸（不用 yield，直接返回动作列表，避免 MicroPython 生成器问题）
# ============================================================
def in_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx + rw and ry <= py <= ry + rh

def handle_touch(points):
    global app_should_exit, current_color, last_point, _debounce_until

    now = time.ticks_ms()
    if not points:
        last_point = None
        return None

    if time.ticks_diff(_debounce_until, now) > 0:
        last_point = None
        return None

    actions = []

    for pt in points:
        x, y = pt.x, pt.y

        # 退出（右上）
        if in_rect(x, y, EXIT_BTN[0] - 10, EXIT_BTN[1] - 10,
                   EXIT_BTN[2] + 20, EXIT_BTN[3] + 20):
            app_should_exit = True
            _debounce_until = time.ticks_add(now, 400)
            return ('exit',)

        # 清除（左下）
        if in_rect(x, y, CLEAR_BTN[0] - 10, CLEAR_BTN[1] - 10,
                   CLEAR_BTN[2] + 20, CLEAR_BTN[3] + 20):
            _debounce_until = time.ticks_add(now, 300)
            return ('clear',)

        # 保存（右下）
        if in_rect(x, y, SAVE_BTN[0] - 10, SAVE_BTN[1] - 10,
                   SAVE_BTN[2] + 20, SAVE_BTN[3] + 20):
            _debounce_until = time.ticks_add(now, 500)
            return ('save',)

        # 随机颜色（左上）
        if in_rect(x, y, COLOR_BTN[0] - 10, COLOR_BTN[1] - 10,
                   COLOR_BTN[2] + 20, COLOR_BTN[3] + 20):
            current_color = (urandom.getrandbits(8), urandom.getrandbits(8), urandom.getrandbits(8))
            _debounce_until = time.ticks_add(now, 300)
            last_point = None
            print("[画板] 颜色: " + str(current_color))
            return None

        # 绘画（插值平滑）
        if last_point is not None:
            dx = x - last_point.x
            dy = y - last_point.y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist <= 30:
                steps = max(1, int(dist // 8))
                for i in range(1, steps + 1):
                    nx = int(last_point.x + i * dx / (steps + 1))
                    ny = int(last_point.y + i * dy / (steps + 1))
                    actions.append(('draw', nx, ny))
                actions.append(('draw', x, y))
            else:
                actions.append(('draw', x, y))
        else:
            actions.append(('draw', x, y))

        last_point = pt
        break  # 只处理第一个触摸点

    return ('draw', actions) if actions else None

# ============================================================
# UI 绘制
# ============================================================
def draw_buttons(img):
    # 左上：随机颜色
    cx, cy, cw, ch = COLOR_BTN
    img.draw_rectangle(cx, cy, cw, ch, color=(60, 60, 70), fill=True)
    img.draw_rectangle(cx, cy, cw, ch, color=(100, 105, 120), thickness=1, fill=False)
    img.draw_string_advanced(cx + 12, cy + 12, 16, "随机颜色", color=(255, 255, 255))
    img.draw_circle(cx + cw + 16, cy + ch // 2, 16, color=current_color, thickness=2, fill=True)

    # 右上：退出
    ex, ey, ew, eh = EXIT_BTN
    img.draw_rectangle(ex, ey, ew, eh, color=(220, 60, 50), fill=True)
    img.draw_string_advanced(ex + 40, ey + 12, 18, "退出", color=(255, 255, 255))

    # 左下：清除
    lx, ly, lw, lh = CLEAR_BTN
    img.draw_rectangle(lx, ly, lw, lh, color=(200, 50, 40), fill=True)
    img.draw_string_advanced(lx + 30, ly + 12, 18, "清除", color=(255, 255, 255))

    # 右下：保存
    sx, sy, sw, sh = SAVE_BTN
    img.draw_rectangle(sx, sy, sw, sh, color=(50, 160, 140), fill=True)
    img.draw_string_advanced(sx + 32, sy + 12, 18, "保存", color=(255, 255, 255))

    # 底部：画笔大小
    img.draw_string_advanced(320, DISPLAY_HEIGHT - 24, 13,
                             "画笔: " + str(brush_size), color=(160, 165, 180))

# ============================================================
# 主循环
# ============================================================
def main():
    global tp, app_should_exit, current_color, brush_size, last_point, _debounce_until

    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    MediaManager.init()
    tp = TOUCH(0)
    beep_init()

    canvas = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.RGB565)
    canvas.clear()

    app_should_exit = False
    current_color = (0, 255, 0)
    brush_size = 10
    last_point = None
    _debounce_until = 0

    print("[画板] 启动")
    print("  左上:随机颜色 | 右上:退出 | 左下:清除 | 右下:保存")

    try:
        while True:
            os.exitpoint()

            points = tp.read(5)
            result = handle_touch(points)

            if app_should_exit:
                print("[画板] 退出")
                break

            if result is not None:
                action_type = result[0]
                if action_type == 'clear':
                    canvas.clear()
                elif action_type == 'save':
                    save_canvas(canvas)
                elif action_type == 'draw':
                    for _, x, y in result[1]:
                        canvas.draw_circle(x, y, brush_size,
                                          color=current_color, thickness=2, fill=True)

            draw_buttons(canvas)
            Display.show_image(canvas)
            time.sleep_ms(8)

    except KeyboardInterrupt:
        print("[画板] 用户停止")
    except BaseException as e:
        print("[画板] 异常: " + str(e))
        import sys
        sys.print_exception(e)
    finally:
        beep_deinit()
        Display.deinit()
        time.sleep_ms(60)
        MediaManager.deinit()

if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()
