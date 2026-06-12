# 系统设置 - 立创·庐山派-K230-CanMV
# 调整待机超时时间（10~60秒）

import os, time, image
from media.display import *
from media.media import *
from machine import TOUCH
import stby

# ============================================================
# 参数
# ============================================================
DISPLAY_WIDTH  = 800
DISPLAY_HEIGHT = 480

# 按钮
EXIT_BTN  = (680, 12, 110, 40)
MINUS_BTN = (160, 180, 80, 50)
PLUS_BTN  = (560, 180, 80, 50)

# ============================================================
# 触摸
# ============================================================
def in_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx + rw and ry <= py <= ry + rh

# ============================================================
# 绘制
# ============================================================
def draw_ui(img, timeout):
    img.clear()
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, color=(18, 20, 32), fill=True)

    # 标题栏
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, 50, color=(28, 31, 46), fill=True)
    img.draw_string_advanced(20, 12, 20, "系统设置", color=(255, 255, 255))

    # 退出
    eb = EXIT_BTN
    img.draw_rectangle(*eb, color=(220, 60, 50), fill=True)
    img.draw_string_advanced(eb[0] + 24, eb[1] + 10, 18, "退出", color=(255, 255, 255))

    # ── 待机时间设置 ──
    img.draw_string_advanced(200, 100, 20, "待机超时时间", color=(200, 210, 230))

    # 减号按钮
    mb = MINUS_BTN
    img.draw_rectangle(*mb, color=(60, 64, 80), fill=True)
    img.draw_rectangle(*mb, color=(100, 105, 125), thickness=1, fill=False)
    img.draw_string_advanced(mb[0] + 28, mb[1] + 12, 24, "−", color=(255, 255, 255))

    # 数值
    val_str = str(timeout) + " 秒"
    img.draw_rectangle(260, 180, 280, 50, color=(35, 38, 52), fill=True)
    img.draw_rectangle(260, 180, 280, 50, color=(80, 85, 105), thickness=1, fill=False)
    img.draw_string_advanced(340, 192, 20, val_str, color=(50, 220, 140))

    # 加号按钮
    pb = PLUS_BTN
    img.draw_rectangle(*pb, color=(60, 64, 80), fill=True)
    img.draw_rectangle(*pb, color=(100, 105, 125), thickness=1, fill=False)
    img.draw_string_advanced(pb[0] + 24, pb[1] + 12, 24, "+", color=(255, 255, 255))

    # 范围提示
    img.draw_string_advanced(260, 250, 16, "范围: 10 ~ 60 秒", color=(120, 125, 140))
    img.draw_string_advanced(240, 280, 14, "主界面无操作超时后进入待机", color=(100, 105, 120))

# ============================================================
# 主循环
# ============================================================
def main():
    timeout = stby.STANDBY_TIMEOUT
    pressed = False
    debounce = 0

    print("[设置] 启动, 当前超时 " + str(timeout) + "s")

    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    MediaManager.init()
    tp = TOUCH(0)

    try:
        while True:
            os.exitpoint()
            now = time.ticks_ms()

            points = tp.read(5)
            app_exit = False

            if points:
                if not pressed:
                    pt = points[0]
                    x, y = pt.x, pt.y
                    if time.ticks_diff(now, debounce) < 0:
                        pressed = True
                        continue

                    # 退出
                    if in_rect(x, y, *EXIT_BTN):
                        stby.STANDBY_TIMEOUT = timeout
                        app_exit = True
                        debounce = time.ticks_add(now, 400)

                    # 减
                    elif in_rect(x, y, *MINUS_BTN) and timeout > 10:
                        timeout -= 5
                        debounce = time.ticks_add(now, 300)

                    # 加
                    elif in_rect(x, y, *PLUS_BTN) and timeout < 60:
                        timeout += 5
                        debounce = time.ticks_add(now, 300)

                    debounce = time.ticks_add(now, 200)
                    pressed = True
            else:
                pressed = False

            if app_exit:
                print("[设置] 超时设为 " + str(stby.STANDBY_TIMEOUT) + "s")
                break

            img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
            draw_ui(img, timeout)
            Display.show_image(img)
            time.sleep_ms(50)

    except KeyboardInterrupt:
        print("[设置] 用户停止")
    except BaseException as e:
        print("[设置] 异常: " + str(e))
    finally:
        Display.deinit()
        time.sleep_ms(60)
        MediaManager.deinit()

if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()
