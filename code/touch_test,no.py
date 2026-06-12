import os
import time
import image
from machine import TOUCH
from media.display import *
from media.media import *


DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480
IMAGE_PATH = "/data/img_top.jpg"

# 如果实测触摸坐标方向不对，可以只改下面三个开关。
SWAP_XY = False
INVERT_X = False
INVERT_Y = False

# 每个区域按 800x480 图片坐标划分，包含图标和下方文字。
ICON_AREAS = (
    ("相机图标", 42, 90, 160, 240),
    ("音乐播放器图标", 193, 90, 311, 240),
    ("WiFi配网图标", 344, 90, 462, 240),
    ("蓝牙调试助手图标", 495, 90, 612, 240),
    ("天气预报图标", 645, 90, 763, 240),
    ("小说阅读器图标", 42, 267, 160, 417),
    ("录音机图标", 193, 267, 311, 417),
    ("画板图标", 344, 267, 462, 417),
    ("云平台监控图标", 495, 267, 612, 417),
    ("系统设置图标", 645, 267, 763, 417),
)


def normalize_touch(x, y):
    """把触摸坐标转换到 800x480 图片坐标。"""
    if SWAP_XY:
        x, y = y, x
    if INVERT_X:
        x = DISPLAY_WIDTH - 1 - x
    if INVERT_Y:
        y = DISPLAY_HEIGHT - 1 - y
    return x, y


def get_icon_name(x, y):
    for name, x1, y1, x2, y2 in ICON_AREAS:
        if x1 <= x <= x2 and y1 <= y <= y2:
            return name
    return None


def show_image():
    print("LCD 显示 img_top.jpg")
    img_src = image.Image(IMAGE_PATH)
    print(f"图片尺寸: {img_src.width()}x{img_src.height()}")
    Display.show_image(img_src.to_rgb565())


def main():
    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    MediaManager.init()
    tp = TOUCH(0)

    pressed = False

    try:
        show_image()
        print("触摸检测已启动，点击图标会打印对应名称，按 Ctrl+C 退出...")

        while True:
            points = tp.read(5)

            if points != ():
                if not pressed:
                    point = points[0]
                    x, y = normalize_touch(point.x, point.y)
                    icon_name = get_icon_name(x, y)

                    if icon_name:
                        print(f"点击了{icon_name}")
                    else:
                        print(f"点击了空白区域: X = {x}, Y = {y}")

                    pressed = True
            else:
                pressed = False

            time.sleep(0.01)
            os.exitpoint()

    except KeyboardInterrupt as e:
        print("用户终止：", e)
    except BaseException as e:
        print(f"异常：{e}")
    finally:
        Display.deinit()
        MediaManager.deinit()


if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()
