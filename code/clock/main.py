'''
实验名称：天气时钟
实验平台：01Studio CanMV K230
日期:2024-8-27验证发布
教程：wiki.01studio.cc
作者:半只半解
版本:v1.0
'''

import os, time, gc, sys, network, json, re
from clock.urllib import urequest ,ntptime
from media.display import *
from media.media import *
from machine import Pin

# 初始化 Wi-Fi 指示灯
WIFI_LED_PIN = 52
LED = Pin(WIFI_LED_PIN, Pin.OUT)

# 选择显示方式
Display.init(Display.ST7701)    # 使用 LCD 屏幕显示

# 初始化媒体管理器
MediaManager.init()

# 创建图像对象用于绘制
canvas = image.Image(800, 480, image.RGB565)
canvas.clear()  # 清空图像

# WiFi账号密码
SSID =''
CODE =''

time.sleep(5) #等待WiFi模块初始化

def WIFI_Connect(max_retries=5):
    """
    连接到指定的 Wi-Fi 网络，并在屏幕上显示连接状态。

    """
    # 初始化 Wi-Fi 接口
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    start_time = time.time()  # 记录时间做超时判断
    retries = max_retries  # 重试次数

    if not wlan.isconnected():
        print('连接到网络...')
        canvas.clear()  # 清除屏幕并显示 "正在连接到 WiFi..." 的信息
        canvas.draw_string_advanced(0, 0, 40, "正在连接到 WiFi...", color=(255, 255, 255))
        Display.show_image(canvas)
        wlan.connect(SSID, CODE)  # WiFi连接

        while not wlan.isconnected():  # 添加重试逻辑
            LED.value(1)
            time.sleep_ms(300)
            LED.value(0)
            time.sleep_ms(300)

            if time.time() - start_time > 15:  # 超时判断,15秒没连接成功判定为超时
                print('WIFI 连接超时 !')
                wlan.active(False)
                return False

    if wlan.isconnected():
        LED.value(1)  # LED点亮
        canvas.clear()# 清除上次残留

        # 显示连接成功的信息
        canvas.draw_string_advanced(0, 0, 40, "WiFi 连接成功", color=(255, 255, 255))
        canvas.draw_string_advanced(0, 50, 40, "WiFi IP: " + wlan.ifconfig()[0], color=(255, 255, 255))
        canvas.draw_string_advanced(0, 430, 45, "Python   攻城", color=(255, 137, 54))
        Display.show_image(canvas)
        print('网络信息:', wlan.ifconfig()) # 打印网络信息

        # 立即获取天气信息和同步时间
        weather_get()
        sync_ntp()
        return True

    else:
        canvas.clear() # 清除上次残留
        canvas.draw_string_advanced(0, 100, 40, "连接失败!", color=(255, 255, 255))
        Display.show_image(canvas)

        for _ in range(3):  # LED 闪烁三次提示连接失败
            LED.value(1)
            time.sleep_ms(300)
            LED.value(0)
            time.sleep_ms(300)

        print('连接失败!!!', wlan.ifconfig()) # 打印错误信信息并把LED重置为熄灭状态
        # LED 重置为熄灭状态
        LED.value(0)

        return False

    """"
    同步NTP服务器时间

    """

def sync_ntp():
    ntp_servers = ['202.120.2.101', 'ntp.ntsc.ac.cn']  # 第二个NTP服务器作为备选
    for server in ntp_servers:
        ntptime.host = server
        try:
            ntptime.settime()
            print(f"成功从 {server} 同步时间")
            break
        except Exception as e:
            print(f"从 {server} 同步ntp时间错误: {repr(e)}")
            continue
    else:
        print("所有NTP服务器均无法同步时间，请检查网络连接或NTP服务器地址。")

    """"
    处理日期和时间

    """

def zero_str(str_num):
    num = int(str_num)
    return "0" + str(num) if num > 0 and num < 10 else str(num)


    """
    天气爬取
    """

# 定义一个长度为5的字符列表
weather = ['']*5
is_first_run = True  # 添加一个标志来标记是否为首次运行

def weather_get(max_retries=5):
    print("尝试获取天气数据...")
    global weather
    retries = max_retries
    # 保存当前的天气信息
    previous_weather = weather.copy()
    while retries > 0:
        try:
            myURL = urequest.urlopen("https://www.weather.com.cn/weather1d/101280601.shtml")
            text = myURL.read(40000).decode('utf-8')  # 获取前38000个数据以节省内存
            # 在网页内容中找出 var observe24h_data 相关内容
            match = re.search('var observe24h_data = ' + '(.*?)' + ';', text)
            if match:
                text2 = json.loads(match.group(1))
                # 获取城市、温度、湿度、风向、风力级数
                weather[0] = text2['od']['od1']          # 城市
                weather[1] = text2['od']['od2'][0]['od22']  # 温度
                weather[2] = text2['od']['od2'][0]['od27']  # 相对湿度
                weather[3] = text2['od']['od2'][0]['od24']  # 实时风向
                weather[4] = text2['od']['od2'][0]['od28']  # 空气质量
                return  # 成功获取数据后退出函数
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            retries -= 1  # 减少重试次数
            if retries > 0:
                print(f"尝试重新获取天气数据，剩余{retries}次...")
                time.sleep(5)  # 等待一段时间再重试
                # 如果获取失败，恢复之前的天气信息
    weather = previous_weather.copy()
    print("获取天气数据失败！")


    """"
    开始连接wifi

    """

try:
    wifi_connected = WIFI_Connect()
except Exception as e:
    print(f"连接WIFI失败: {e}")
    wifi_connected = False

# 如果连接失败，显示连接失败的信息
if not wifi_connected:
    print('WiFi连接失败.')
    canvas.clear()  # 清屏,黑色
    canvas.draw_string_advanced(0, 100, 40, "连接失败,复位重新连接!", color=(255, 255, 255))
    Display.show_image(canvas)  # 显示
    while True:
        pass  # 阻塞在此，不再继续执行
else:

    # 创建一个包含所有图片路径的列表
    kof_paths = [f"/sdcard/clock/ui/kof/{i}.png" for i in range(1, 18)]  # 从1到17
    star_paths = [f"/sdcard/clock/ui/star/{i}.png" for i in range(1, 25)]  # 从1到24
    logo_paths = [f"/sdcard/clock/ui/logo/{i}.png" for i in range(1, 31)]  # 从1到31

    # 预处理所有图像并转换为RGB565格式
    star_rgb565 = [image.Image(path).to_rgb565() for path in star_paths]
    kof_rgb565 = [image.Image(path).to_rgb565() for path in kof_paths]
    logo_rgb565 = [image.Image(path).to_rgb565() for path in logo_paths]

    # 用于显示图片
    star_index = 0
    kof_index = 0
    logo_index = 0

    # 获取空气质量字符串
    aqi_str = weather[4]

    # 初始绘制,首次绘制.
    if is_first_run:
        # 清除上次残留
        canvas.draw_rectangle(0, 0, 480, 100, color = (0, 0, 0), thickness = 2, fill = True)
        canvas.draw_string_advanced(20, 0, 40, f" {weather[0]} ", color = (255, 165, 0))

        # 绘制温度湿度信息
        canvas.draw_string_advanced(0, 50, 40, f"温度: {weather[1]}℃", color=(255,160,122))
        canvas.draw_string_advanced(250, 50, 40, f"湿度: {weather[2]}%", color=(32,178,170))

        # 清楚上次残留,并绘制风向信息
        canvas.draw_rectangle(0, 380, 340, 50, color = (0, 0, 0), thickness = 2, fill = True)
        canvas.draw_string_advanced(0, 380, 40, f"实时风向: {weather[3]}", color=(255, 255, 255))

        # 空气质量
        try:
            aqi = int(aqi_str)
        except ValueError:
            aqi = 0  # 设置默认值

        if 0 <= aqi < 50:  # 优
            canvas.draw_rectangle(275, 0, 70, 50, color=(0, 255, 0), thickness=2, fill=True)
            canvas.draw_string_advanced(280, 0, 40, f" 优!", color=(0, 0, 0))
        elif 50 <= aqi < 100:  # 良
            canvas.draw_rectangle(275, 0, 70, 50, color=(249, 218, 101), thickness=2, fill=True)
            canvas.draw_string_advanced(280, 0, 40, f" 良", color=(0, 0, 0))
        elif 100 <= aqi < 150:  # 轻度
            canvas.draw_rectangle(275, 0, 105, 50, color=(255, 165, 0), thickness=2, fill=True)
            canvas.draw_string_advanced(280, 0, 40, f" 轻度", color=(0, 0, 0))
        elif 150 <= aqi < 200:  # 中度
            canvas.draw_rectangle(275, 0, 105, 50, color=(212, 106, 106), thickness=2, fill=True)
            canvas.draw_string_advanced(280, 0, 40, f" 中度", color=(0, 0, 0))
        elif 200 <= aqi < 300:  # 重度
            canvas.draw_rectangle(275, 0, 105, 50, color=(220, 20, 60), thickness=2, fill=True)
            canvas.draw_string_advanced(280, 0, 40, f" 重度", color=(0, 0, 0))
        elif 300 <= aqi < 500:  # 严重
            canvas.draw_rectangle(275, 0, 105, 50, color=(139, 0, 0), thickness=2, fill=True)
            canvas.draw_string_advanced(280, 0, 40, f" 严重", color=(0, 0, 0))

        is_first_run = False  # 设置标志为False，下次循环不绘制这些信息

    # 主循环
    last_weather_update = time.time()  # 记录最后一次更新天气的时间

    try:
        while True:
            os.exitpoint() #检测IDE中断

            current_time = time.time()  # 当前时间
            localtime_now = time.localtime()  # 每次循环开始时定义 localtime_now

            if current_time - last_weather_update > 1000:  # 每隔1000秒更新一次天气信息
                last_weather_update = current_time
                weather_get()  # 获取天气
                sync_ntp()  # 同步时间
                aqi_str = weather[4]  # 更新空气质量字符串

                # 在同步时间之后获取本地时间并格式化
                time_str = '%s-%s-%s %s:%s:%s' % (
                    localtime_now[0],   # 年
                    zero_str(localtime_now[1]), # 月
                    zero_str(localtime_now[2]), # 日
                    zero_str(localtime_now[3]), # 小时
                    zero_str(localtime_now[4]), # 分钟
                    zero_str(localtime_now[5])  # 秒
                )
                print("当前日期和时间:",time_str)

                 # 清除上次残留, # 日期:年月日
                canvas.draw_rectangle(0, 120, 430, 100, color = (0, 0, 0), thickness = 2, fill = True)
                canvas.draw_string_advanced(0, 120, 80, f" {localtime_now[0]}-{zero_str(localtime_now[1])}-{zero_str(localtime_now[2])}", color=(144,238,144))

                # 清除上次残留, # 城市信息
                canvas.draw_rectangle(0, 0, 480, 100, color = (0, 0, 0), thickness = 2, fill = True)
                canvas.draw_string_advanced(20, 0, 40, f" {weather[0]} ", color = (255, 165, 0))

                # 绘制温度湿度信息
                canvas.draw_string_advanced(0, 50, 40, f"温度: {weather[1]}℃", color=(255,160,122))
                canvas.draw_string_advanced(250, 50, 40, f"湿度: {weather[2]}%", color=(32,178,170))

                # 清楚上次残留,并绘制风向信息
                canvas.draw_rectangle(0, 380, 340, 50, color = (0, 0, 0), thickness = 2, fill = True)
                canvas.draw_string_advanced(0, 380, 40, f"实时风向: {weather[3]}", color=(255, 255, 255))
                # 空气质量
                try:
                    aqi = int(aqi_str)
                except ValueError:
                    aqi = 0  # 设置默认值

                if 0 <= aqi < 50:  # 优
                    canvas.draw_rectangle(275, 0, 70, 50, color=(0, 255, 0), thickness=2, fill=True)
                    canvas.draw_string_advanced(280, 0, 40, f" 优!", color=(0, 0, 0))
                elif 50 <= aqi < 100:  # 良
                    canvas.draw_rectangle(275, 0, 70, 50, color=(249, 218, 101), thickness=2, fill=True)
                    canvas.draw_string_advanced(280, 0, 40, f" 良", color=(0, 0, 0))
                elif 100 <= aqi < 150:  # 轻度
                    canvas.draw_rectangle(275, 0, 105, 50, color=(255, 165, 0), thickness=2, fill=True)
                    canvas.draw_string_advanced(280, 0, 40, f" 轻度", color=(0, 0, 0))
                elif 150 <= aqi < 200:  # 中度
                    canvas.draw_rectangle(275, 0, 105, 50, color=(212, 106, 106), thickness=2, fill=True)
                    canvas.draw_string_advanced(280, 0, 40, f" 中度", color=(0, 0, 0))
                elif 200 <= aqi < 300:  # 重度
                    canvas.draw_rectangle(275, 0, 105, 50, color=(220, 20, 60), thickness=2, fill=True)
                    canvas.draw_string_advanced(280, 0, 40, f" 重度", color=(0, 0, 0))
                elif 300 <= aqi < 500:  # 严重
                    canvas.draw_rectangle(275, 0, 105, 50, color=(139, 0, 0), thickness=2, fill=True)
                    canvas.draw_string_advanced(280, 0, 40, f" 严重", color=(0, 0, 0))

            ###########
            #主循环绘制#
            ###########
            # 清除上次残留, # 日期:年月日
            canvas.draw_rectangle(0, 120, 430, 100, color = (0, 0, 0), thickness = 2, fill = True)
            canvas.draw_string_advanced(0, 120, 80, f" {localtime_now[0]}-{zero_str(localtime_now[1])}-{zero_str(localtime_now[2])}", color=(144,238,144))
            # 清除上次残留，# 时间 :小时分钟秒
            canvas.draw_rectangle(0, 230, 430, 100, color = (0, 0, 0), thickness = 2, fill = True)
            canvas.draw_string_advanced(0, 230, 80, f" {zero_str(localtime_now[3])}:{zero_str(localtime_now[4])}:{zero_str(localtime_now[5])}", color=(199, 237, 204))
            # 图片绘制
            canvas.draw_image(logo_rgb565[logo_index], 350, 350, alpha=256, scale=1.0)
            canvas.draw_image(star_rgb565[star_index], 480, 0, alpha=256, scale=1.0)
            canvas.draw_image(kof_rgb565[kof_index], 480, 240, alpha=256, scale=1.0)
            Display.show_image(canvas)  # 显示图片

            time.sleep_ms(20)   # 消除图片过快鬼畜

            # 查询内存,可有可无K230随便造这些小功能
            DRAM = gc.mem_free()
            if DRAM < 1000000:  # 内存不足
                gc.collect()  # 回收内存

            # 更新索引，使用模运算实现循环
            star_index = (star_index + 1) % len(star_rgb565)
            kof_index = (kof_index + 1) % len(kof_rgb565)
            logo_index = (logo_index + 1) % len(logo_rgb565)

    except KeyboardInterrupt:
        print("用户停止程序")
    except Exception as e:
        print(f"发生异常: {e}")
    finally:
        # 释放显示资源
        Display.deinit()
        MediaManager.deinit()
        os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
