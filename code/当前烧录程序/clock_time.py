# NTP 时间同步 + 主界面时间显示 - 立创·庐山派-K230-CanMV
# 联网后自动同步，格式 HH:MM

import time, image
from media.display import *

# ============================================================
# 全局
# ============================================================
_synced = False
_last_hour = -1
_last_minute = -1

# ============================================================
# NTP 时间同步（基于 clock/urllib/ntptime.py）
# ============================================================
def sync_time():
    global _synced
    try:
        import ntptime
        ntptime.settime()
        _synced = True
        print("[时间] NTP 同步成功")
        return True
    except Exception as e:
        print("[时间] NTP 同步失败: " + str(e))
        return False

def is_synced():
    return _synced

# ============================================================
# 时间获取
# ============================================================
def get_time_str():
    """返回当前时间字符串 'HH:MM'"""
    try:
        tm = time.localtime()
        return "%02d:%02d" % (tm[3], tm[4])
    except:
        return "--:--"

# ============================================================
# 主屏幕右上角时间+WiFi组合绘制
# ============================================================
def draw_time_wifi_overlay(wifi_icon_drawer, x, y):
    """在 OSD1 层绘制时间和 WiFi 图标组合"""
    # 时间在左（宽度 60），WiFi 在右（宽度 36），总宽 ~100
    img = image.Image(100, 32, image.ARGB8888)
    img.clear()

    # 时间文字
    time_str = get_time_str()
    img.draw_string_advanced(4, 6, 18, time_str, color=(255, 255, 255))

    # WiFi 图标（由 mywificon.draw_icon 绘制）
    wifi_icon_drawer(img, 68, 5)

    Display.show_image(img, x=x, y=y, layer=Display.LAYER_OSD1)
