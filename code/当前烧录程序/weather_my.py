# 天气功能 - 立创·庐山派-K230-CanMV
# 城市: 临清 (101121707)，数据源: weather.com.cn

import os, time, image, json, re, gc
from media.display import *
from media.media import *
from machine import TOUCH

# ============================================================
# 参数
# ============================================================
DISPLAY_WIDTH  = 800
DISPLAY_HEIGHT = 480
CITY_NAME      = "临清"
CITY_CODE      = "101121707"
WEATHER_URL    = "https://www.weather.com.cn/weather1d/" + CITY_CODE + ".shtml"

# ============================================================
# 全局
# ============================================================
weather = [''] * 5  # [城市, 温度, 湿度, 风向, 空气质量]
app_should_exit = False
last_update_time = ""
status_msg = "正在获取天气..."

# ============================================================
# 天气获取（基于 clock/main.py 的 weather_get）
# ============================================================
def fetch_weather():
    global weather, last_update_time, status_msg
    try:
        import urequest
    except:
        status_msg = "urequest 模块不可用"
        return False

    print("[天气] 获取 " + CITY_NAME + " 天气...")
    status_msg = "正在获取天气数据..."
    retries = 3

    while retries > 0:
        try:
            r = urequest.urlopen(WEATHER_URL)
            text = r.read(40000).decode('utf-8')
            r.close()

            match = re.search(r'var observe24h_data = (.*?);', text)
            if match:
                data = json.loads(match.group(1))
                weather[0] = CITY_NAME
                weather[1] = str(data['od']['od2'][0]['od22'])  # 温度
                weather[2] = str(data['od']['od2'][0]['od27'])  # 湿度
                weather[3] = str(data['od']['od2'][0]['od24'])  # 风向
                weather[4] = str(data['od']['od2'][0]['od28'])  # 空气质量

                tm = time.localtime()
                last_update_time = "%02d:%02d:%02d" % (tm[3], tm[4], tm[5])
                status_msg = ""
                print("[天气] 获取成功: " + weather[1] + "℃ " + weather[2] + "%")
                return True

        except Exception as e:
            retries -= 1
            print("[天气] 重试 " + str(retries) + ": " + str(e))
            time.sleep(2)

    status_msg = "获取天气失败，请检查网络"
    return False

# ============================================================
# 触摸
# ============================================================
def in_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx + rw and ry <= py <= ry + rh

# ============================================================
# 绘制
# ============================================================
def draw_ui(img):
    img.clear()
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, color=(18, 20, 32), fill=True)

    # 标题栏
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, 50, color=(28, 31, 46), fill=True)
    img.draw_string_advanced(20, 12, 20, "天气 - " + CITY_NAME, color=(255, 255, 255))

    # 退出按钮
    img.draw_rectangle(680, 10, 110, 36, color=(220, 60, 50), fill=True)
    img.draw_string_advanced(695, 16, 16, "退出", color=(255, 255, 255))

    # 刷新按钮
    img.draw_rectangle(560, 10, 110, 36, color=(50, 100, 180), fill=True)
    img.draw_string_advanced(580, 16, 16, "刷新", color=(255, 255, 255))

    # 状态消息
    if status_msg:
        img.draw_string_advanced(200, 200, 16, status_msg, color=(255, 160, 60))

    if not weather[1]:
        img.draw_string_advanced(240, 240, 14, "请确保 WiFi 已连接后点击刷新", color=(120, 125, 140))
        if last_update_time:
            img.draw_string_advanced(300, 270, 14, "上次更新: " + last_update_time, color=(100, 105, 120))
        return

    # ── 城市 + 空气质量 ──
    img.draw_string_advanced(40, 70, 24, weather[0], color=(255, 165, 0))

    # 空气质量色块
    try:
        aqi = int(weather[4])
    except:
        aqi = 0

    aqi_x, aqi_y = 160, 68
    if 0 <= aqi < 50:
        aqi_color, aqi_text = (0, 200, 80), " 优"
    elif aqi < 100:
        aqi_color, aqi_text = (249, 218, 101), " 良"
    elif aqi < 150:
        aqi_color, aqi_text = (255, 165, 0), " 轻度"
    elif aqi < 200:
        aqi_color, aqi_text = (212, 106, 106), " 中度"
    elif aqi < 300:
        aqi_color, aqi_text = (220, 60, 60), " 重度"
    else:
        aqi_color, aqi_text = (139, 0, 0), " 严重"

    img.draw_rectangle(aqi_x, aqi_y, 70, 28, color=aqi_color, fill=True)
    img.draw_string_advanced(aqi_x + 4, aqi_y + 4, 18, aqi_text, color=(0, 0, 0))

    # ── 温度（大字） ──
    img.draw_string_advanced(40, 120, 90, weather[1] + "°", color=(255, 200, 130))
    img.draw_string_advanced(200, 145, 28, "℃", color=(255, 160, 122))

    # ── 信息卡片 ──
    card_x, card_y = 40, 240
    card_w, card_h = 320, 200
    img.draw_rectangle(card_x, card_y, card_w, card_h, color=(28, 31, 46), fill=True)
    img.draw_rectangle(card_x, card_y, card_w, card_h, color=(60, 65, 80), thickness=1, fill=False)

    img.draw_string_advanced(card_x + 16, card_y + 16, 16, "━━ 详细信息 ━━", color=(160, 165, 180))

    info_items = [
        ("湿度", weather[2] + "%", (32, 178, 170)),
        ("风向", weather[3], (180, 180, 220)),
        ("空气质量", weather[4] + " (" + aqi_text.strip() + ")", aqi_color),
    ]
    for i, (label, value, vc) in enumerate(info_items):
        iy = card_y + 54 + i * 48
        img.draw_string_advanced(card_x + 20, iy, 16, label + ":", color=(140, 145, 160))
        img.draw_string_advanced(card_x + 100, iy, 18, value, color=vc)

    # 分隔线
    for i in range(1, 3):
        ly = card_y + 46 + i * 48
        img.draw_line(card_x + 16, ly, card_x + card_w - 16, ly, color=(45, 50, 65))

    # ── 右侧装饰 ──
    # 大温度计图标
    rx, ry = 420, 240
    img.draw_rectangle(rx, ry, 340, 200, color=(28, 31, 46), fill=True)
    img.draw_rectangle(rx, ry, 340, 200, color=(60, 65, 80), thickness=1, fill=False)
    img.draw_string_advanced(rx + 20, ry + 20, 16, "━━ 生活建议 ━━", color=(160, 165, 180))

    # 根据温度给建议
    try:
        temp = int(weather[1])
    except:
        temp = 20

    tips = []
    if temp < 10:
        tips = ["天气寒冷，注意保暖", "适合穿棉衣、羽绒服", "不宜长时间户外活动"]
    elif temp < 20:
        tips = ["天气凉爽，体感舒适", "适合穿薄外套或毛衣", "适宜户外运动"]
    elif temp < 28:
        tips = ["温度适宜，天气舒适", "适合穿短袖、衬衫", "注意防晒补水"]
    elif temp < 35:
        tips = ["天气较热，注意防暑", "适合穿轻薄夏装", "避免正午户外活动"]
    else:
        tips = ["高温预警，谨防中暑", "穿清凉夏装，多饮水", "尽量避免户外活动"]

    for i, tip in enumerate(tips):
        iy = ry + 56 + i * 44
        icon = ["🧥", "🌿", "☀️"][i] if i < 3 else ""
        img.draw_string_advanced(rx + 20, iy, 16, tip, color=(200, 210, 230))

    # ── 更新时间 ──
    if last_update_time:
        ut = "更新于 " + last_update_time
        img.draw_string_advanced(40, DISPLAY_HEIGHT - 28, 13, ut, color=(80, 85, 100))

# ============================================================
# 主循环
# ============================================================
def main():
    global app_should_exit, last_update_time, status_msg

    print("[天气] 启动 - " + CITY_NAME)

    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    MediaManager.init()
    tp = TOUCH(0)

    app_should_exit = False
    last_update_time = ""
    status_msg = "点击 [刷新] 获取天气"
    pressed = False
    debounce = 0

    try:
        while True:
            os.exitpoint()
            now = time.ticks_ms()

            points = tp.read(5)
            if points:
                if not pressed:
                    pt = points[0]
                    x, y = pt.x, pt.y
                    if time.ticks_diff(now, debounce) < 0:
                        pressed = True
                        continue

                    # 退出
                    if in_rect(x, y, 680, 10, 110, 36):
                        app_should_exit = True
                        debounce = time.ticks_add(now, 400)
                        pressed = True
                        continue

                    # 刷新
                    if in_rect(x, y, 560, 10, 110, 36):
                        fetch_weather()
                        debounce = time.ticks_add(now, 500)
                        pressed = True
                        continue

                    debounce = time.ticks_add(now, 200)
                    pressed = True
            else:
                pressed = False

            if app_should_exit:
                print("[天气] 退出")
                break

            img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
            draw_ui(img)
            Display.show_image(img)

            time.sleep_ms(50)

    except KeyboardInterrupt:
        print("[天气] 用户停止")
    except BaseException as e:
        print("[天气] 异常: " + str(e))
        import sys
        sys.print_exception(e)
    finally:
        Display.deinit()
        time.sleep_ms(60)
        MediaManager.deinit()

if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()
