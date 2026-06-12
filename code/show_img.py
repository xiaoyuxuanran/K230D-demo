import os, time, image
from media.display import *
from media.media import *

DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480

def show_image():
    print("LCD 显示 img_top.jpg")

    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    MediaManager.init()

    try:
        # 加载 JPG，用 to_rgb565() 解压并转换格式
        img_src = image.Image("/data/img_top.jpg")
        print(f"图片尺寸: {img_src.width()}x{img_src.height()}")

        img = img_src.to_rgb565()

        # 显示到屏幕
        Display.show_image(img)

        print("图片已显示，按 Ctrl+C 退出...")
        while True:
            time.sleep(1)
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
    show_image()
