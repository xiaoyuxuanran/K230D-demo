import os
import time
import image
import music_player_copy
import takephoto
import audiowr
import picWarehouse
import painting
import mywificon
import weather_my
import clock_time
import stby
import sys_setting
import novel_reader
from machine import TOUCH
from media.display import *
from media.media import *


DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480
IMAGE_PATH = "/data/code/photo/img_top.jpg"

# 如果实测触摸坐标方向不对，可以只改下面三个开关。
SWAP_XY = False
INVERT_X = False
INVERT_Y = False

# 每个区域按 800x480 图片坐标划分，包含图标和下方文字。
ICON_AREAS = (
    ("相机图标", 42, 90, 160, 240),
    ("音乐播放器图标", 193, 90, 311, 240),
    ("WiFi配网图标", 344, 90, 462, 240),
    ("相册图标", 495, 90, 612, 240),
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


_shared_tp = None  # TOUCH 全局单例，避免重复创建

def init_home():
    global _shared_tp
    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    MediaManager.init()
    if _shared_tp is None:
        _shared_tp = TOUCH(0)
    return _shared_tp


def deinit_home():
    Display.deinit()
    time.sleep_ms(80)
    MediaManager.deinit()
    time.sleep_ms(50)


_time_synced = False

def update_status_bar():
    """右上角 OSD1：时间(HH:MM) + WiFi 图标"""
    clock_time.draw_time_wifi_overlay(mywificon.draw_icon, x=690, y=6)

def main():
    global _shared_tp, _time_synced
    tp = init_home()

    pressed = False
    last_status_update = 0
    last_activity = time.ticks_ms()  # 待机倒计时

    try:
        show_image()
        update_status_bar()
        print("触摸检测已启动，点击图标会打印对应名称，按 Ctrl+C 退出...")

        while True:
            points = tp.read(5)
            now = time.ticks_ms()

            # ── 待机检测 ──
            if time.ticks_diff(now, last_activity) > stby.STANDBY_TIMEOUT * 1000:
                print("[主页] " + str(stby.STANDBY_TIMEOUT) + "s 无操作，进入待机")
                deinit_home()
                stby.main()
                os.exitpoint(os.EXITPOINT_ENABLE)
                tp = init_home()
                show_image()
                update_status_bar()
                last_activity = time.ticks_ms()
                pressed = False
                continue

            if points != ():
                last_activity = now  # 刷新活动时间
                if not pressed:
                    point = points[0]
                    x, y = normalize_touch(point.x, point.y)
                    icon_name = get_icon_name(x, y)

                    if icon_name == "WiFi配网图标":
                        print("点击了WiFi配网图标，进入WiFi配网")
                        deinit_home()
                        try:
                            mywificon.main()
                        except BaseException as e:
                            print("WiFi异常: " + str(e))
                            import sys
                            sys.print_exception(e)
                        os.exitpoint(os.EXITPOINT_ENABLE)
                        tp = init_home()
                        show_image()
                        # WiFi 配网后尝试同步时间
                        if mywificon.is_connected() and not _time_synced:
                            if clock_time.sync_time():
                                _time_synced = True
                        update_status_bar()
                        print("已返回主界面")
                    elif icon_name == "相机图标":
                        print("点击了相机图标，进入相机")
                        deinit_home()
                        takephoto.main()
                        os.exitpoint(os.EXITPOINT_ENABLE)
                        tp = init_home()
                        show_image()
                        update_status_bar()
                        last_activity = time.ticks_ms()
                        print("已返回主界面")
                    elif icon_name == "音乐播放器图标":
                        print("点击了音乐播放器图标，进入音乐播放器")
                        deinit_home()
                        music_player_copy.main()
                        os.exitpoint(os.EXITPOINT_ENABLE)
                        tp = init_home()
                        show_image()
                        update_status_bar()
                        last_activity = time.ticks_ms()
                        print("已返回主界面")
                    elif icon_name == "小说阅读器图标":
                        print("点击了小说阅读器图标，进入阅读器")
                        deinit_home()
                        try:
                            novel_reader.main()
                        except BaseException as e:
                            print("阅读器异常: " + str(e))
                            import sys
                            sys.print_exception(e)
                        os.exitpoint(os.EXITPOINT_ENABLE)
                        tp = init_home()
                        show_image()
                        update_status_bar()
                        last_activity = time.ticks_ms()
                        print("已返回主界面")
                    elif icon_name == "画板图标":
                        print("点击了画板图标，进入画板")
                        deinit_home()
                        try:
                            painting.main()
                        except BaseException as e:
                            print("画板异常: " + str(e))
                            import sys
                            sys.print_exception(e)
                        os.exitpoint(os.EXITPOINT_ENABLE)
                        tp = init_home()
                        show_image()
                        update_status_bar()
                        last_activity = time.ticks_ms()
                        print("已返回主界面")
                    elif icon_name == "天气预报图标":
                        print("点击了天气预报图标，进入天气")
                        deinit_home()
                        try:
                            weather_my.main()
                        except BaseException as e:
                            print("天气异常: " + str(e))
                            import sys
                            sys.print_exception(e)
                        os.exitpoint(os.EXITPOINT_ENABLE)
                        tp = init_home()
                        show_image()
                        update_status_bar()
                        last_activity = time.ticks_ms()
                        print("已返回主界面")
                    elif icon_name == "系统设置图标":
                        print("点击了系统设置图标，进入设置")
                        deinit_home()
                        try:
                            sys_setting.main()
                        except BaseException as e:
                            print("设置异常: " + str(e))
                            import sys
                            sys.print_exception(e)
                        os.exitpoint(os.EXITPOINT_ENABLE)
                        tp = init_home()
                        show_image()
                        update_status_bar()
                        last_activity = time.ticks_ms()
                        print("已返回主界面")
                    elif icon_name == "相册图标":
                        print("点击了相册图标，进入相册")
                        deinit_home()
                        try:
                            picWarehouse.main()
                        except BaseException as e:
                            print("相册异常: " + str(e))
                            import sys
                            sys.print_exception(e)
                        os.exitpoint(os.EXITPOINT_ENABLE)
                        tp = init_home()
                        show_image()
                        update_status_bar()
                        last_activity = time.ticks_ms()
                        print("已返回主界面")
                    elif icon_name == "录音机图标":
                        print("点击了录音机图标，进入录音机")
                        deinit_home()
                        try:
                            audiowr.main()
                        except BaseException as e:
                            print(f"录音机异常: {e}")
                            import sys
                            sys.print_exception(e)
                        os.exitpoint(os.EXITPOINT_ENABLE)
                        tp = init_home()
                        show_image()
                        update_status_bar()
                        last_activity = time.ticks_ms()
                        print("已返回主界面")
                    elif icon_name:
                        print(f"点击了{icon_name}")
                    else:
                        print(f"点击了空白区域: X = {x}, Y = {y}")

                    pressed = True
            else:
                pressed = False

            # 每 15 秒刷新状态栏；WiFi 已连接且未同步时尝试 NTP 同步
            now = time.ticks_ms()
            if time.ticks_diff(now, last_status_update) > 15000:
                update_status_bar()
                last_status_update = now
                if mywificon.is_connected() and not _time_synced:
                    if clock_time.sync_time():
                        _time_synced = True

            time.sleep(0.01)
            os.exitpoint()

    except KeyboardInterrupt as e:
        print("用户终止：", e)
    except BaseException as e:
        print(f"异常：{e}")
    finally:
        deinit_home()


def touch_main():
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()
