# 待机界面 - 立创·庐山派-K230-CanMV
# 基于 clock 项目，显示天气+时间+动画，点击屏幕唤醒

import os, time, image, json, re, gc, network
from media.display import *
from media.media import *
from machine import TOUCH

# ============================================================
# 参数（与 weather_my 保持一致）
# ============================================================
DISPLAY_WIDTH  = 800
DISPLAY_HEIGHT = 480
CITY_NAME      = "临清"
CITY_CODE      = "101121707"
WEATHER_URL    = "https://www.weather.com.cn/weather1d/" + CITY_CODE + ".shtml"

# 待机超时默认值（秒）
STANDBY_TIMEOUT = 30

# 天气缓存
weather = [''] * 5
last_weather_fetch = 0

# 无动画

# ============================================================
# WiFi + NTP
# ============================================================
def ensure_wifi_time():
    import ntptime
    sta = network.WLAN(network.STA_IF)
    if not sta.active():
        sta.active(True)
    if not sta.isconnected():
        return False
    try:
        ntptime.settime()
        return True
    except:
        return False

# ============================================================
# 天气
# ============================================================
def fetch_weather():
    global weather, last_weather_fetch
    try:
        import urequest
    except:
        return False
    try:
        r = urequest.urlopen(WEATHER_URL)
        text = r.read(40000).decode('utf-8')
        r.close()
        match = re.search(r'var observe24h_data = (.*?);', text)
        if match:
            data = json.loads(match.group(1))
            weather[0] = CITY_NAME
            weather[1] = str(data['od']['od2'][0]['od22'])
            weather[2] = str(data['od']['od2'][0]['od27'])
            weather[3] = str(data['od']['od2'][0]['od24'])
            weather[4] = str(data['od']['od2'][0]['od28'])
            last_weather_fetch = time.time()
            return True
    except:
        pass
    return False

# 动画已移除

# ============================================================
# 绘制
# ============================================================
def zero_str(n):
    num = int(n)
    return "0" + str(num) if 0 < num < 10 else str(num)

def draw_standby(img):
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, color=(10, 12, 22), fill=True)
    tm = time.localtime()
    CX = DISPLAY_WIDTH // 2

    # ── 城市名（居中） ──
    city = weather[0] if weather[0] else CITY_NAME
    img.draw_string_advanced(CX - len(city) * 12, 20, 24, city, color=(255, 165, 0))

    # ── 空气质量（居中色块） ──
    try:
        aqi = int(weather[4]) if weather[4] else 0
    except:
        aqi = 0
    if aqi <= 0:
        aqc, aqt = (80, 80, 100), " --"
    elif aqi < 50:
        aqc, aqt = (0, 200, 80), "you"
    elif aqi < 100:
        aqc, aqt = (249, 218, 101), "liang"
    elif aqi < 150:
        aqc, aqt = (255, 165, 0), "qingdu"
    elif aqi < 200:
        aqc, aqt = (212, 106, 106), "zhongdu"
    elif aqi < 300:
        aqc, aqt = (220, 60, 60), "zhongdu"
    else:
        aqc, aqt = (139, 0, 0), "yanzhong"
    img.draw_rectangle(CX - 30, 52, 60, 24, color=aqc, fill=True)
    img.draw_string_advanced(CX - 22, 54, 14, aqt, color=(0, 0, 0))

    # ── 天气信息行（纯数字，避免中文/符号缺失） ──
    parts = []
    if weather[1]:
        parts.append(weather[1] + "C")
    if weather[2]:
        parts.append(weather[2] + "%")
    if weather[3]:
        parts.append(weather[3])
    line = "  |  ".join(parts) if parts else "No Data"
    img.draw_string_advanced(CX - len(line) * 5, 90, 18, line, color=(180, 190, 210))

    # ── 日期（居中） ──
    ds = str(tm[0]) + "-" + zero_str(tm[1]) + "-" + zero_str(tm[2])
    img.draw_string_advanced(CX - len(ds) * 15, 150, 50, ds, color=(144, 238, 144))

    # ── 时间（居中大字，HH:MM） ──
    ts = zero_str(tm[3]) + ":" + zero_str(tm[4])
    img.draw_string_advanced(CX - len(ts) * 30, 220, 90, ts, color=(199, 237, 204))

    # ── 底部提示 ──
    img.draw_string_advanced(CX - 70, DISPLAY_HEIGHT - 36, 16,
                             "Touch to wake", color=(70, 75, 90))

# ============================================================
# 主循环
# ============================================================
def main():
    global last_weather_fetch

    print("[待机] 启动")

    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    MediaManager.init()
    tp = TOUCH(0)

    ensure_wifi_time()
    fetch_weather()

    last_weather_fetch = time.time()
    pressed = False

    try:
        while True:
            os.exitpoint()
            now = time.time()

            # 每 1000 秒更新天气
            if now - last_weather_fetch > 1000:
                ensure_wifi_time()
                fetch_weather()
                last_weather_fetch = now

            # 触摸唤醒
            points = tp.read(5)
            if points:
                if not pressed:
                    print("[待机] 唤醒")
                    break
                pressed = True
            else:
                pressed = False

            # 绘制
            img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
            draw_standby(img)
            Display.show_image(img)

            time.sleep_ms(200)

            # 内存回收
            if gc.mem_free() < 500000:
                gc.collect()

    except KeyboardInterrupt:
        print("[待机] 用户停止")
    except BaseException as e:
        print("[待机] 异常: " + str(e))
        import sys
        sys.print_exception(e)
    finally:
        Display.deinit()
        time.sleep_ms(60)
        MediaManager.deinit()

if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()
