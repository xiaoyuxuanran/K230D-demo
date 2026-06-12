# V 1.1 版本测试

# 摄像头

## 默认摄像头 CSI2 ✅

- 代码
  
    ```python
    # 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
    # 开发板官网：www.lckfb.com
    # 技术支持常驻论坛，任何技术问题欢迎随时交流学习
    # 立创论坛：www.jlc-bbs.com/lckfb
    # 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
    # 不靠卖板赚钱，以培养中国工程师为己任
    
    import time, os, sys
    
    from media.sensor import *
    from media.display import *
    from media.media import *
    
    sensor_id = 2
    sensor = None
    
    try:
        # 构造一个具有默认配置的摄像头对象
        sensor = Sensor(id=sensor_id)
        # 重置摄像头sensor
        sensor.reset()
    
        # 无需进行镜像翻转
        # 设置水平镜像
        # sensor.set_hmirror(False)
        # 设置垂直翻转
        # sensor.set_vflip(False)
    
        # 设置通道0的输出尺寸为1920x1080
        sensor.set_framesize(Sensor.FHD, chn=CAM_CHN_ID_0)
        # 设置通道0的输出像素格式为RGB888
        sensor.set_pixformat(Sensor.RGB888, chn=CAM_CHN_ID_0)
    
        # 使用IDE的帧缓冲区作为显示输出
        Display.init(Display.VIRT, width=1920, height=1080, to_ide=True)
        # 初始化媒体管理器
        MediaManager.init()
        # 启动传感器
        sensor.run()
    
        while True:
            os.exitpoint()
    
            # 捕获通道0的图像
            img = sensor.snapshot(chn=CAM_CHN_ID_0)
            # 显示捕获的图像
            Display.show_image(img)
    
    except KeyboardInterrupt as e:
        print("用户停止: ", e)
    except BaseException as e:
        print(f"异常: {e}")
    finally:
        # 停止传感器运行
        if isinstance(sensor, Sensor):
            sensor.stop()
        # 反初始化显示模块
        Display.deinit()
        os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
        time.sleep_ms(100)
        # 释放媒体缓冲区
        MediaManager.deinit()
    ```
    

## CSI1 ✅

- 代码
  
    ```python
    # 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
    # 开发板官网：www.lckfb.com
    # 技术支持常驻论坛，任何技术问题欢迎随时交流学习
    # 立创论坛：www.jlc-bbs.com/lckfb
    # 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
    # 不靠卖板赚钱，以培养中国工程师为己任
    
    import time, os, sys
    
    from media.sensor import *
    from media.display import *
    from media.media import *
    
    sensor_id = 1
    sensor = None
    
    try:
        # 构造一个具有默认配置的摄像头对象
        sensor = Sensor(id=sensor_id)
        # 重置摄像头sensor
        sensor.reset()
    
        # 无需进行镜像翻转
        # 设置水平镜像
        # sensor.set_hmirror(False)
        # 设置垂直翻转
        # sensor.set_vflip(False)
    
        # 设置通道0的输出尺寸为1920x1080
        sensor.set_framesize(Sensor.FHD, chn=CAM_CHN_ID_0)
        # 设置通道0的输出像素格式为RGB888
        sensor.set_pixformat(Sensor.RGB888, chn=CAM_CHN_ID_0)
    
        # 使用IDE的帧缓冲区作为显示输出
        Display.init(Display.VIRT, width=1920, height=1080, to_ide=True)
        # 初始化媒体管理器
        MediaManager.init()
        # 启动传感器
        sensor.run()
    
        while True:
            os.exitpoint()
    
            # 捕获通道0的图像
            img = sensor.snapshot(chn=CAM_CHN_ID_0)
            # 显示捕获的图像
            Display.show_image(img)
    
    except KeyboardInterrupt as e:
        print("用户停止: ", e)
    except BaseException as e:
        print(f"异常: {e}")
    finally:
        # 停止传感器运行
        if isinstance(sensor, Sensor):
            sensor.stop()
        # 反初始化显示模块
        Display.deinit()
        os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
        time.sleep_ms(100)
        # 释放媒体缓冲区
        MediaManager.deinit()
    ```
    

## CSI0 ✅

- 代码
  
    ```python
    # 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
    # 开发板官网：www.lckfb.com
    # 技术支持常驻论坛，任何技术问题欢迎随时交流学习
    # 立创论坛：www.jlc-bbs.com/lckfb
    # 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
    # 不靠卖板赚钱，以培养中国工程师为己任
    
    import time, os, sys
    
    from media.sensor import *
    from media.display import *
    from media.media import *
    
    sensor_id = 0
    sensor = None
    
    try:
        # 构造一个具有默认配置的摄像头对象
        sensor = Sensor(id=sensor_id)
        # 重置摄像头sensor
        sensor.reset()
    
        # 无需进行镜像翻转
        # 设置水平镜像
        # sensor.set_hmirror(False)
        # 设置垂直翻转
        # sensor.set_vflip(False)
    
        # 设置通道0的输出尺寸为1920x1080
        sensor.set_framesize(Sensor.FHD, chn=CAM_CHN_ID_0)
        # 设置通道0的输出像素格式为RGB888
        sensor.set_pixformat(Sensor.RGB888, chn=CAM_CHN_ID_0)
    
        # 使用IDE的帧缓冲区作为显示输出
        Display.init(Display.VIRT, width=1920, height=1080, to_ide=True)
        # 初始化媒体管理器
        MediaManager.init()
        # 启动传感器
        sensor.run()
    
        while True:
            os.exitpoint()
    
            # 捕获通道0的图像
            img = sensor.snapshot(chn=CAM_CHN_ID_0)
            # 显示捕获的图像
            Display.show_image(img)
    
    except KeyboardInterrupt as e:
        print("用户停止: ", e)
    except BaseException as e:
        print(f"异常: {e}")
    finally:
        # 停止传感器运行
        if isinstance(sensor, Sensor):
            sensor.stop()
        # 反初始化显示模块
        Display.deinit()
        os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
        time.sleep_ms(100)
        # 释放媒体缓冲区
        MediaManager.deinit()
    ```
    

# 风扇✅

没有问题，可以正常调速

- 代码
  
    ```python
    import time
    from machine import PWM, FPIOA
    
    # 1. 配置引脚复用 (根据你的代码，将引脚60复用为PWM通道0输出)
    pwm_io = FPIOA()
    pwm_io.set_function(60, FPIOA.PWM0)
    
    # 2. 初始化PWM参数
    pwm = PWM(0)
    
    # 设置频率为2000Hz (2kHz)，这个频率通常很适合直流无刷风扇
    pwm.freq(20000)
    
    # 初始状态：确保风扇处于停止状态 (0% 占空比)
    pwm.duty_u16(0)
    time.sleep(1)
    
    print("开始测试：风扇转速将从 0% 逐渐提升至 100%...")
    
    try:
        # 3. 使用 for 循环逐步增加转速
        # 范围从 0 到 65535，每次增加 1024 (步长可自行修改，步长越小过渡越平滑)
        for duty in range(0, 65536, 1024):
            # 确保数值不会溢出超过 65535
            safe_duty = min(duty, 65535)
            
            # 写入占空比控制转速
            pwm.duty_u16(safe_duty)
            
            # 计算百分比并打印，方便观察终端输出
            percent = (safe_duty / 65535) * 100
            print(f"当前占空比值: {safe_duty:5d}  |  转速比例: {percent:5.1f}%")
            
            # 短暂延时 0.1 秒，给电机提速的时间，也让视觉/听觉上有渐进的效果
            time.sleep(0.1)
    
        # 循环结束后，确保风扇达到绝对最高转速
        pwm.duty_u16(65535)
        print("已达到最高转速 (100%)，保持全速运行 5 秒...")
        time.sleep(5)
    
    except KeyboardInterrupt:
        # 如果你在终端按下了 Ctrl+C 中断程序，会捕获到这个异常
        print("\n程序被手动中断！")
    
    finally:
        # 4. 安全退出：无论程序是正常结束还是被中断，都将占空比设为0，关闭风扇
        print("测试结束，关闭风扇。")
        pwm.duty_u16(0)
        
        # 如果你的硬件固件支持，可以使用 pwm.deinit() 来释放 PWM 资源
        # pwm.deinit()
    ```
    

# 麦克风和功放喇叭✅

- 代码
  
    ```python
    # audio input and output example
    #
    # Note: You will need an SD card to run this example.
    #
    # You can play wav files or capture audio to save as wav
    
    import os
    from media.media import *   #导入media模块，用于初始化vb buffer
    from media.pyaudio import * #导入pyaudio模块，用于采集和播放音频
    import media.wave as wave   #导入wav模块，用于保存和加载wav音频文件
    
    from machine import Pin
    from machine import FPIOA
    import machine
    
    #from mpp.ai import ai_config_mic
    
    # 创建FPIOA对象，用于初始化引脚功能配置
    fpioa = FPIOA()
    
    # 设置引脚功能，将指定的引脚配置为普通GPIO功能,
    fpioa.set_function(10,FPIOA.GPIO10)
    
    HT_CTRL = Pin(10, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    
    HT_CTRL.high()
    
    def exit_check():
        try:
            os.exitpoint()
        except KeyboardInterrupt as e:
            print("user stop: ", e)
            return True
        return False
    
    def record_audio(filename, duration):
        CHUNK = 44100//25  #设置音频chunk值
        FORMAT = paInt16       #设置采样精度,支持16bit(paInt16)/24bit(paInt24)/32bit(paInt32)
        CHANNELS = 2           #设置声道数,支持单声道(1)/立体声(2)
        RATE = 44100           #设置采样率
    
        try:
            p = PyAudio()
    
            #创建音频输入流
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
    
            stream.volume(70, LEFT)
            stream.volume(85, RIGHT)
            print("volume :",stream.volume())
    
            #启用音频3A功能：自动噪声抑制(ANS)
            stream.enable_audio3a(AUDIO_3A_ENABLE_ANS)
    
            frames = []
            #采集音频数据并存入列表
            for i in range(0, int(RATE / CHUNK * duration)):
                data = stream.read()
                frames.append(data)
                if exit_check():
                    break
            #将列表中的数据保存到wav文件中
            wf = wave.open(filename, 'wb') #创建wav 文件
            wf.set_channels(CHANNELS) #设置wav 声道数
            wf.set_sampwidth(p.get_sample_size(FORMAT))  #设置wav 采样精度
            wf.set_framerate(RATE)  #设置wav 采样率
            wf.write_frames(b''.join(frames)) #存储wav音频数据
            wf.close() #关闭wav文件
        except BaseException as e:
                import sys
                sys.print_exception(e)
        finally:
            stream.stop_stream() #停止采集音频数据
            stream.close()#关闭音频输入流
            p.terminate()#释放音频对象
    
    def play_audio(filename):
        try:
            wf = wave.open(filename, 'rb')#打开wav文件
            CHUNK = int(wf.get_framerate()/25)#设置音频chunk值
    
            p = PyAudio()
    
            #创建音频输出流，设置的音频参数均为wave中获取到的参数
            stream = p.open(format=p.get_format_from_width(wf.get_sampwidth()),
                        channels=wf.get_channels(),
                        rate=wf.get_framerate(),
                        output=True,frames_per_buffer=CHUNK)
    
            #设置音频输出流的音量
            stream.volume(vol=100)
    
            data = wf.read_frames(CHUNK)#从wav文件中读取数一帧数据
    
            while data:
                stream.write(data)  #将帧数据写入到音频输出流中
                data = wf.read_frames(CHUNK) #从wav文件中读取数一帧数据
                if exit_check():
                    break
        except BaseException as e:
                import sys
                sys.print_exception(e)
        finally:
            stream.stop_stream() #停止音频输出流
            stream.close()#关闭音频输出流
            p.terminate()#释放音频对象
            wf.close()#关闭wav文件
    
    def loop_audio(duration):
        CHUNK = 44100//25#设置音频chunck
        FORMAT = paInt16 #设置音频采样精度,支持16bit(paInt16)/24bit(paInt24)/32bit(paInt32)
        CHANNELS = 2 #设置音频声道数，支持单声道(1)/立体声(2)
        RATE = 44100 #设置音频采样率
    
        try:
            p = PyAudio()
    
            #创建音频输入流
            input_stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
    
            #设置音频输入流的音量
            input_stream.volume(70, LEFT)
            input_stream.volume(85, RIGHT)
            print("input volume :",input_stream.volume())
    
            #启用音频3A功能：自动噪声抑制(ANS)
            input_stream.enable_audio3a(AUDIO_3A_ENABLE_ANS)
    
            #创建音频输出流
            output_stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            output=True,frames_per_buffer=CHUNK)
    
            #设置音频输出流的音量
            output_stream.volume(vol=85)
    
            #从音频输入流中获取数据写入到音频输出流中
            for i in range(0, int(RATE / CHUNK * duration)):
                output_stream.write(input_stream.read())
                if exit_check():
                    break
        except BaseException as e:
                import sys
                sys.print_exception(e)
        finally:
            input_stream.stop_stream()#停止音频输入流
            output_stream.stop_stream()#停止音频输出流
            input_stream.close() #关闭音频输入流
            output_stream.close() #关闭音频输出流
            p.terminate() #释放音频对象
    
    def audio_recorder(filename, duration):
        CHUNK = 44100//25      #设置音频chunk值
        FORMAT = paInt16       #设置采样精度,支持16bit(paInt16)/24bit(paInt24)/32bit(paInt32)
        CHANNELS = 2           #设置声道数,支持单声道(1)/立体声(2)
        RATE = 44100           #设置采样率
    
    #    ai_config_mic()
    
        p = PyAudio()
    
    #    ai_config_mic()
    
        try:
            #创建音频输入流
            input_stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
    
            input_stream.volume(60, LEFT)
            input_stream.volume(60, RIGHT)
            print("input volume :",input_stream.volume())
    
            #启用音频3A功能：自动噪声抑制(ANS)
            input_stream.enable_audio3a(AUDIO_3A_ENABLE_ANS)
            print("enable audio 3a:ans")
    
            print("start record...")
            frames = []
            #采集音频数据并存入列表
            for i in range(0, int(RATE / CHUNK * duration)):
                data = input_stream.read()
                frames.append(data)
                if exit_check():
                    break
            print("stop record...")
            #将列表中的数据保存到wav文件中
            wf = wave.open(filename, 'wb') #创建wav 文件
            wf.set_channels(CHANNELS) #设置wav 声道数
            wf.set_sampwidth(p.get_sample_size(FORMAT))  #设置wav 采样精度
            wf.set_framerate(RATE)  #设置wav 采样率
            wf.write_frames(b''.join(frames)) #存储wav音频数据
            wf.close() #关闭wav文件
        except BaseException as e:
                import sys
                sys.print_exception(e)
        finally:
            input_stream.stop_stream() #停止采集音频数据
            input_stream.close()#关闭音频输入流
    
        try:
            wf = wave.open(filename, 'rb')#打开wav文件
            CHUNK = int(wf.get_framerate()/25)#设置音频chunk值
    
            #创建音频输出流，设置的音频参数均为wave中获取到的参数
            output_stream = p.open(format=p.get_format_from_width(wf.get_sampwidth()),
                        channels=wf.get_channels(),
                        rate=wf.get_framerate(),
                        output=True,frames_per_buffer=CHUNK)
    
            #设置音频输出流的音量
            output_stream.volume(vol=100)
            print("output volume :",output_stream.volume())
    
            print("start play...")
            data = wf.read_frames(CHUNK)#从wav文件中读取数一帧数据
    
            while data:
                output_stream.write(data)  #将帧数据写入到音频输出流中
                data = wf.read_frames(CHUNK) #从wav文件中读取数一帧数据
                if exit_check():
                    break
            print("stop play...")
        except BaseException as e:
                import sys
                sys.print_exception(e)
        finally:
            output_stream.stop_stream() #停止音频输出流
            output_stream.close()#关闭音频输出流
    
        p.terminate() #释放音频对象
    
    if __name__ == "__main__":
        os.exitpoint(os.EXITPOINT_ENABLE)
        print("audio sample start")
    
    #    ai_config_mic()
        print("MIC BIAS set to ~1.8V, PGA Gain set to 0dB")
    
        HT_CTRL.high()
    
        # record_audio('/sdcard/examples/test1.wav', 30)  #录制wav文件
        # play_audio('/sdcard/examples/test.wav') #播放wav文件
        # loop_audio(150) #采集音频并输出
        audio_recorder('/data/test.wav', 15) #录制15秒音频并播放
        print("audio sample done")
    
    ```
    

# RGB灯✅

- 代码【基础点灯】
  
    ```python
    # 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
    # 开发板官网：www.lckfb.com
    # 技术支持常驻论坛，任何技术问题欢迎随时交流学习
    # 立创论坛：www.jlc-bbs.com/lckfb
    # 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
    # 不靠卖板赚钱，以培养中国工程师为己任
    
    from machine import Pin
    from machine import FPIOA
    import time
    
    # 创建FPIOA对象，用于初始化引脚功能配置
    fpioa = FPIOA()
    
    # 设置引脚功能，将指定的引脚配置为普通GPIO功能,
    fpioa.set_function(65,FPIOA.GPIO65)
    fpioa.set_function(66,FPIOA.GPIO66)
    fpioa.set_function(71,FPIOA.GPIO71)
    
    # 实例化Pin62, Pin20, Pin63为输出，分别控制红、绿、蓝灯
    LED_R = Pin(65, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    LED_G = Pin(66, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    LED_B = Pin(71, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    
    # 板载RGB灯是共阳结构，设置引脚为高电平时关闭灯，低电平时点亮灯
    # 初始化时先关闭所有LED灯
    LED_R.low()  # 关闭红灯
    LED_G.low()  # 关闭绿灯
    LED_B.low()  # 关闭蓝灯
    
    # 基础点灯试验：选择一个LED灯并让其闪烁
    # 默认选择红色LED灯，后续可以通过变量改变需要控制的灯
    LED = LED_R  # 当前控制的LED为红色LED
    
    while True:
        LED.low()   # 点亮当前选择的LED
        time.sleep(0.5)  # 等待0.5秒
        LED.high()  # 熄灭当前选择的LED
        time.sleep(0.5)  # 等待0.5秒from machine import Pin
    ```
    
- 代码【多色点灯】
  
    ```python
    # 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
    # 开发板官网：www.lckfb.com
    # 技术支持常驻论坛，任何技术问题欢迎随时交流学习
    # 立创论坛：www.jlc-bbs.com/lckfb
    # 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
    # 不靠卖板赚钱，以培养中国工程师为己任
    
    from machine import Pin
    from machine import FPIOA
    import time
    
    # 创建FPIOA对象，用于初始化引脚功能配置
    fpioa = FPIOA()
    
    # 设置引脚功能，将指定的引脚配置为普通GPIO功能,
    fpioa.set_function(65,FPIOA.GPIO65)
    fpioa.set_function(66,FPIOA.GPIO66)
    fpioa.set_function(71,FPIOA.GPIO71)
    
    # 实例化Pin62, Pin20, Pin63为输出，分别控制红、绿、蓝灯
    LED_R = Pin(65, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    LED_G = Pin(66, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    LED_B = Pin(71, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    
    # 初始化时先关闭所有LED灯
    LED_R.low()  # 关闭红灯
    LED_G.low()  # 关闭绿灯
    LED_B.low()  # 关闭蓝灯
    
    def set_color(r, g, b):
        """设置RGB灯的颜色，使用Pin.high()和Pin.low()控制"""
        if r == 0:
            LED_R.high()  # 红灯亮
        else:
            LED_R.low()  # 红灯灭
    
        if g == 0:
            LED_G.high()  # 绿灯亮
        else:
            LED_G.low()  # 绿灯灭
    
        if b == 0:
            LED_B.high()  # 蓝灯亮
        else:
            LED_B.low()  # 蓝灯灭
    
    def blink_color(r, g, b, delay):
        """设置颜色并让灯亮一段时间后熄灭"""
        set_color(r, g, b)  # 设置颜色
        time.sleep(delay)   # 保持该颜色一段时间
        set_color(1, 1, 1)  # 熄灭所有灯（共阳：1为熄灭）
        time.sleep(delay)   # 熄灭后等待一段时间
    
    while True:
        # 红色
        blink_color(0, 1, 1, 0.5)
        # 绿色
        blink_color(1, 0, 1, 0.5)
        # 蓝色
        blink_color(1, 1, 0, 0.5)
        # 黄色（红+绿）
        blink_color(0, 0, 1, 0.5)
        # 紫色（红+蓝）
        blink_color(0, 1, 0, 0.5)
        # 青色（绿+蓝）
        blink_color(1, 0, 0, 0.5)
        # 白色（红+绿+蓝）
        blink_color(0, 0, 0, 0.5)
    ```
    

# 板载按键✅

复位没问题，

用户按键：

- 代码【按键控制灯】
  
    ```python
    # 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
    # 开发板官网：www.lckfb.com
    # 技术支持常驻论坛，任何技术问题欢迎随时交流学习
    # 立创论坛：www.jlc-bbs.com/lckfb
    # 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
    # 不靠卖板赚钱，以培养中国工程师为己任
    
    from machine import Pin
    from machine import FPIOA
    import time
    
    # 创建FPIOA对象，用于初始化引脚功能配置
    fpioa = FPIOA()
    
    # 设置引脚功能，将指定的引脚配置为普通GPIO功能,
    fpioa.set_function(65,FPIOA.GPIO65)
    fpioa.set_function(66,FPIOA.GPIO66)
    fpioa.set_function(71,FPIOA.GPIO71)
    fpioa.set_function(64,FPIOA.GPIO64)
    
    # 实例化Pin62, Pin20, Pin63为输出，分别控制红、绿、蓝灯
    LED_R = Pin(65, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    LED_G = Pin(66, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    LED_B = Pin(71, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    
    # 按键引脚为53，按下时高电平，设置为输入模式
    button = Pin(64, Pin.IN, Pin.PULL_DOWN)  # 使用下拉电阻
    
    # 初始选择控制红灯
    LED = LED_R  # 默认控制红灯
    
    # 初始化时关闭所有LED灯
    LED_R.low()
    LED_G.low()
    LED_B.low()
    
    # 消抖时间设置为20毫秒
    debounce_delay = 20  # 毫秒
    last_press_time = 0  # 上次按键按下的时间，单位为毫秒
    
    # 记录LED当前状态，True表示亮，False表示灭
    led_on = False
    
    # 记录按键状态，用于检测按下和松开的状态变化
    button_last_state = 0  # 上次按键状态
    
    # 主循环
    while True:
        button_state = button.value()  # 获取当前按键状态
        current_time = time.ticks_ms()  # 获取当前时间（单位：毫秒）
    
        # 检测按键从未按下(0)到按下(1)的变化（上升沿）
        if button_state == 1 and button_last_state == 0:
            # 检查按键是否在消抖时间外
            if current_time - last_press_time > debounce_delay:
                # 切换LED的状态
                if led_on:
                    LED.low()  # 熄灭LED
                else:
                    LED.high()   # 点亮LED
    
                led_on = not led_on  # 反转LED状态
                last_press_time = current_time  # 更新按键按下时间
    
        # 更新上次按键状态
        button_last_state = button_state
    
        # 简单延时，防止主循环过于频繁
        time.sleep_ms(10)
    ```
    

# 蜂鸣器✅

- 代码【简单鸣叫一声】
  
    ```python
    # 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
    # 开发板官网：www.lckfb.com
    # 技术支持常驻论坛，任何技术问题欢迎随时交流学习
    # 立创论坛：www.jlc-bbs.com/lckfb
    # 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
    # 不靠卖板赚钱，以培养中国工程师为己任
    import time
    from machine import PWM, FPIOA
    
    # 配置蜂鸣器IO口功能
    beep_io = FPIOA()
    beep_io.set_function(61, FPIOA.PWM1)
    
    # 初始化蜂鸣器PWM通道
    beep_pwm = PWM(1)  # 默认频率4kHz,占空比50%
    
    # 调整通道0频率为4000Hz
    beep_pwm.freq(4000)
    
    # 调整通道0的占空比为 50% (32768 / 65535)
    beep_pwm.duty_u16(32768)
    
    # 使能PWM通道输出
    beep_pwm.duty_u16(32768)
    # 延时50ms
    time.sleep_ms(50)
    # 关闭PWM输出 防止蜂鸣器吵闹
    beep_pwm.duty_u16(0)
    # 叫完了就释放PWM
    beep_pwm.deinit()
    ```
    

# WIFI 模块✅

- 代码【链接wifi】
  
    ```python
    # 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
    # 开发板官网：www.lckfb.com
    # 技术支持常驻论坛，任何技术问题欢迎随时交流学习
    # 立创论坛：www.jlc-bbs.com/lckfb
    # 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
    # 不靠卖板赚钱，以培养中国工程师为己任
    
    import network
    import time
    
    SSID = "yzhm"        # 路由器名称
    PASSWORD = "123456781" # 路由器密码
    
    def sta_test():
        # 初始化STA模式（客户端模式）
        sta = network.WLAN(network.STA_IF)
    
        # 激活WiFi模块（相当于打开手机WIFI开关）
        if not sta.active():  # 判断是否已激活
            sta.active(True)
        print("WiFi模块激活状态:", sta.active())
    
        # 查看初始连接状态
        print("初始连接状态:", sta.status())
    
        # 扫描当前环境中的WIFI
        wifi_list = sta.scan()  # 扫描周围WiFi
        # 打印每个Wi-Fi信息
        for wifi in wifi_list:
            # 访问 rt_wlan_info 对象的属性
            ssid = wifi.ssid       # ssid 属性
            rssi = wifi.rssi       # rssi 属性
            print(f"SSID: {ssid}, 信号强度: {rssi}dBm")
    
        # 尝试连接路由器
        print(f"正在连接 {SSID}...")
        sta.connect(SSID, PASSWORD)
    
        # 等待连接结果（最多尝试5次）
        max_wait = 5
        while max_wait > 0:
            if sta.isconnected():  # 检查是否连接成功
                break
            max_wait -= 1
            time.sleep(1)  # 失败了就线休息一秒再说
            sta.connect(SSID, PASSWORD)
            print("剩余等待次数：", max_wait, "次")
    
        # 如果获取不到IP地址就一直在这等待
        while sta.ifconfig()[0] == '0.0.0.0':
            pass
    
        if sta.isconnected():
            print("\n连接成功！")
            # 重新获取并打印网络配置
            ip_info = sta.ifconfig()
            print(f"IP地址: {ip_info[0]}")
            print(f"子网掩码: {ip_info[1]}")
            print(f"网关: {ip_info[2]}")
            print(f"DNS服务器: {ip_info[3]}")
        else:
            print("连接失败，请检查密码或信号强度")
    
    sta_test()
    
    while True:
        # 持续死循环，等待用户打断并退出该循环
        time.sleep(0.5)  # 等待0.5秒
    ```
    
- 代码【创建热点】
  
    ```python
    # 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
    # 开发板官网：www.lckfb.com
    # 技术支持常驻论坛，任何技术问题欢迎随时交流学习
    # 立创论坛：www.jlc-bbs.com/lckfb
    # 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
    # 不靠卖板赚钱，以培养中国工程师为己任
    
    import network
    import time
    
    AP_SSID = 'LushanPi-AP'  # 热点名称
    AP_KEY = '123456781'  # 至少8位密码
    
    def ap_test():
        # 初始化AP模式
        ap = network.WLAN(network.AP_IF)
    
        # 激活AP模式
        if not ap.active():
            ap.active(True)
        print("AP模式激活状态:", ap.active())
    
        # 配置热点参数
        ap.config(ssid=AP_SSID,key=AP_KEY)
        print("\n热点已创建:")
        print(f"SSID: {AP_SSID}")
        print(f"Channel: {AP_KEY}")
    
        # 等待热点启动（暂定3秒）
        time.sleep(3)
    
        # 获取并打印IP信息
        ip_info = ap.ifconfig()
        print("\nAP网络配置:")
        print(f"IP地址: {ip_info[0]}")
        print(f"子网掩码: {ip_info[1]}")
        print(f"网关: {ip_info[2]}")
        print(f"DNS服务器: {ip_info[3]}")
    
        # 持续监控连接设备
        while True:
            clients = ap.status('stations')
            print(f"\n已连接设备数: {len(clients)}")
    
            time.sleep(1)
    
    ap_test()
    ```
    

# 屏幕和触摸✅

- 代码【画板程序】
  
    ```python
    # 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
    # 开发板官网：www.lckfb.com
    # 技术支持常驻论坛，任何技术问题欢迎随时交流学习
    # 立创论坛：www.jlc-bbs.com/lckfb
    # 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
    # 不靠卖板赚钱，以培养中国工程师为己任
    
    import network
    import time
    
    AP_SSID = 'LushanPi-AP'  # 热点名称
    AP_KEY = '123456781'  # 至少8位密码
    
    def ap_test():
        # 初始化AP模式
        ap = network.WLAN(network.AP_IF)
    
        # 激活AP模式
        if not ap.active():
            ap.active(True)
        print("AP模式激活状态:", ap.active())
    
        # 配置热点参数
        ap.config(ssid=AP_SSID,key=AP_KEY)
        print("\n热点已创建:")
        print(f"SSID: {AP_SSID}")
        print(f"Channel: {AP_KEY}")
    
        # 等待热点启动（暂定3秒）
        time.sleep(3)
    
        # 获取并打印IP信息
        ip_info = ap.ifconfig()
        print("\nAP网络配置:")
        print(f"IP地址: {ip_info[0]}")
        print(f"子网掩码: {ip_info[1]}")
        print(f"网关: {ip_info[2]}")
        print(f"DNS服务器: {ip_info[3]}")
    
        # 持续监控连接设备
        while True:
            clients = ap.status('stations')
            print(f"\n已连接设备数: {len(clients)}")
    
            time.sleep(1)
    
    ap_test()
    ```
    
- 代码【拍照保存图像程序】
  
    ```python
    # 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
    # 开发板官网：www.lckfb.com
    # 技术支持常驻论坛，任何技术问题欢迎随时交流学习
    # 立创论坛：www.jlc-bbs.com/lckfb
    # 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
    # 不靠卖板赚钱，以培养中国工程师为己任
    
    import time, os, sys
    
    #使用默认摄像头，可选参数:0,1,2.
    sensor_id = 1
    
    # ========== 多媒体/图像相关模块 ==========
    from media.sensor import Sensor, CAM_CHN_ID_0
    from media.display import Display
    from media.media import MediaManager
    import image
    
    # ========== GPIO/按键/LED相关模块 ==========
    from machine import Pin
    from machine import FPIOA
    
    # ========== 创建FPIOA对象并为引脚功能分配 ==========
    fpioa = FPIOA()
    # 设置引脚功能，将指定的引脚配置为普通GPIO功能,
    fpioa.set_function(65,FPIOA.GPIO65)
    fpioa.set_function(66,FPIOA.GPIO66)
    fpioa.set_function(71,FPIOA.GPIO71)
    
    # 实例化Pin62, Pin20, Pin63为输出，分别控制红、绿、蓝灯
    LED_R = Pin(65, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    LED_G = Pin(66, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    LED_B = Pin(71, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    
    # 初始化时关闭所有LED灯
    LED_R.low()
    LED_G.low()
    LED_B.low()
    
    # 选一个LED用来拍照提示
    PHOTO_LED = LED_G
    
    # ========== 初始化按键：按下时高电平 ==========
    button = Pin(64, Pin.IN, Pin.PULL_DOWN)
    debounce_delay = 200  # 按键消抖时长(ms)
    last_press_time = 0
    button_last_state = 0
    
    # ========== 显示配置 ==========
    DISPLAY_MODE = "LCD"   # 可选："VIRT","LCD","HDMI"
    if DISPLAY_MODE == "VIRT":
        DISPLAY_WIDTH = 1920
        DISPLAY_HEIGHT = 1080
        FPS = 30
    elif DISPLAY_MODE == "LCD":
        DISPLAY_WIDTH = 800
        DISPLAY_HEIGHT = 480
        FPS = 60
    elif DISPLAY_MODE == "HDMI":
        DISPLAY_WIDTH = 1920
        DISPLAY_HEIGHT = 1080
        FPS = 30
    else:
        raise ValueError("未知的 DISPLAY_MODE，请选择 'VIRT', 'LCD' 或 'HDMI'")
    
    def lckfb_save_jpg(img, filename, quality=95):
        """
        将图像压缩成JPEG后写入文件 (不依赖第一段 save_jpg/MediaManager.convert_to_jpeg 的写法)
        :param img:    传入的图像对象 (Sensor.snapshot() 得到)
        :param filename: 保存的目标文件名 (含路径)
        :param quality:  压缩质量 (1-100)
        """
        compressed_data = img.compress(quality=quality)
    
        with open(filename, "wb") as f:
            f.write(compressed_data)
    
        print(f"[INFO] 使用 lckfb_save_jpg() 保存完毕: {filename}")
    
    # ========== 自动创建图片保存文件夹 & 计算已有图片数量 ==========
    image_folder = "/sdcard/images"
    
    # 若不存在该目录则创建
    try:
        os.stat(image_folder)  # 尝试获取目录信息
    except OSError:
        os.mkdir(image_folder)  # 若失败则创建该目录
    
    # 统计当前目录下以 “lckfb_XX.jpg” 命名的文件数量，自动从最大编号继续
    image_count = 0
    existing_images = [fname for fname in os.listdir(image_folder)
                       if fname.startswith("lckfb_") and fname.endswith(".jpg")]
    
    if existing_images:
        # 提取编号并找出最大值
        numbers = []
        for fname in existing_images:
            # 假设文件名格式为 "lckfb_XX.jpg"
            # 取中间 XX 部分转为数字
            try:
                num_part = fname[6:11]  # "lckfb_" 长度为6，取到 ".jpg" 前还要注意下标
                numbers.append(int(num_part))
            except:
                pass
        if numbers:
            image_count = max(numbers)
    
    try:
        print("[INFO] 初始化摄像头 ...")
        sensor = Sensor(id=sensor_id)
        sensor.reset()
    
        # 在本示例中使用 VGA (640x480) 做演示
        sensor.set_framesize(width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, chn=CAM_CHN_ID_0)
        sensor.set_pixformat(Sensor.RGB565, chn=CAM_CHN_ID_0)
    
        # ========== 初始化显示 ==========
        if DISPLAY_MODE == "VIRT":
            Display.init(Display.VIRT, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, fps=FPS)
        elif DISPLAY_MODE == "LCD":
            Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
        elif DISPLAY_MODE == "HDMI":
            Display.init(Display.LT9611, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    
        # ========== 初始化媒体管理器 ==========
        MediaManager.init()
    
        # ========== 启动摄像头 ==========
        sensor.run()
        print("[INFO] 摄像头已启动，进入主循环 ...")
    
        fps = time.clock()
    
        while True:
            fps.tick()
            os.exitpoint()
    
            #抓取通道0的图像
            img = sensor.snapshot(chn=CAM_CHN_ID_0)
    
            #按键处理（检测上升沿）
            current_time = time.ticks_ms()
            button_state = button.value()
    
            if button_state == 1 and button_last_state == 0:  # 上升沿
                if current_time - last_press_time > debounce_delay:
                    # LED闪烁提示
                    PHOTO_LED.high()   # 点亮LED
                    time.sleep_ms(20)
                    PHOTO_LED.low()  # 熄灭LED
    
                    # 拍照并保存
                    image_count += 1
                    filename = f"{image_folder}/lckfb_{image_count:05d}_{img.width()}x{img.height()}.jpg"
                    print(f"[INFO] 拍照保存 -> {filename}")
    
                    # 直接调用自定义的 lckfb_save_jpg() 函数
                    lckfb_save_jpg(img, filename, quality=95)
    
                    last_press_time = current_time
    
            button_last_state = button_state
    
            img.draw_string_advanced(0, 0, 32, str(image_count), color=(255, 0, 0))
            img.draw_string_advanced(0, DISPLAY_HEIGHT-32, 32, str(fps.fps()), color=(255, 0, 0))
    
            Display.show_image(img)
    
    except KeyboardInterrupt:
        print("[INFO] 用户停止")
    except BaseException as e:
        print(f"[ERROR] 出现异常: {e}")
    finally:
        if 'sensor' in locals() and isinstance(sensor, Sensor):
            sensor.stop()
        Display.deinit()
        os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
        time.sleep_ms(100)
        MediaManager.deinit()
    ```
    

# HDMI扩展板✅

# 电源相关✅

三个串口gh1.25座子用5V供电✅

12v口供电 ✅ 24V供电长时间测试✅

分别模拟 usb 上电，12V口供电，外部5V供电  上电 下电场景 ✅

# 各个IO口测试✅

## 三个串口座子✅

- 串口2 ✅
  
    ![image.png](image%202.png)
    
    ```python
    import time
    from machine import UART
    from machine import FPIOA
    
    # =========================
    # 1. 配置 UART2 引脚
    # =========================
    fpioa = FPIOA()
    
    # UART2_TXD -> GPIO11
    # UART2_RXD -> GPIO12
    fpioa.set_function(11, FPIOA.UART2_TXD)
    fpioa.set_function(12, FPIOA.UART2_RXD)
    
    # =========================
    # 2. 初始化 UART2
    # =========================
    uart = UART(
        UART.UART2,
        baudrate=115200,
        bits=UART.EIGHTBITS,
        parity=UART.PARITY_NONE,
        stop=UART.STOPBITS_ONE
    )
    
    # =========================
    # 3. 参数配置
    # =========================
    tx_count = 0
    tx_interval_ms = 500          # 每 500ms 主动发送一次
    last_tx_time = time.ticks_ms()
    
    # =========================
    # 4. 主循环：持续发送 + 持续接收
    # =========================
    while True:
        now = time.ticks_ms()
    
        # ---------- 周期性发送 ----------
        if time.ticks_diff(now, last_tx_time) >= tx_interval_ms:
            tx_msg = "[TX] LuShan-Pi-lite UART2 count = {}\r\n".format(tx_count)
            uart.write(tx_msg)
    
            tx_count += 1
            last_tx_time = now
    
        # ---------- 持续接收 ----------
        data = uart.read()
    
        if data:
            # 在 CanMV IDE 的串行终端打印
            print("[RX raw]:", data)
    
            # 回传给电脑串口工具
            uart.write(b"[RX echo] ")
            uart.write(data)
            uart.write(b"\r\n")
    
        # 小延时，避免 CPU 空转过高
        time.sleep_ms(10)
    ```
    
- 串口3 ✅
  
    ![image.png](image%203.png)
    
    ```python
    import time
    from machine import UART
    from machine import FPIOA
    
    # =========================
    # 1. 配置 UART2 引脚
    # =========================
    fpioa = FPIOA()
    
    # UART2_TXD -> GPIO32
    # UART2_RXD -> GPIO33
    fpioa.set_function(32, FPIOA.UART3_TXD)
    fpioa.set_function(33, FPIOA.UART3_RXD)
    
    # =========================
    # 2. 初始化 UART2
    # =========================
    uart = UART(
        UART.UART3,
        baudrate=115200,
        bits=UART.EIGHTBITS,
        parity=UART.PARITY_NONE,
        stop=UART.STOPBITS_ONE
    )
    
    # =========================
    # 3. 参数配置
    # =========================
    tx_count = 0
    tx_interval_ms = 500          # 每 500ms 主动发送一次
    last_tx_time = time.ticks_ms()
    
    # =========================
    # 4. 主循环：持续发送 + 持续接收
    # =========================
    while True:
        now = time.ticks_ms()
    
        # ---------- 周期性发送 ----------
        if time.ticks_diff(now, last_tx_time) >= tx_interval_ms:
            tx_msg = "[TX] LuShan-Pi-lite UART2 count = {}\r\n".format(tx_count)
            uart.write(tx_msg)
    
            tx_count += 1
            last_tx_time = now
    
        # ---------- 持续接收 ----------
        data = uart.read()
    
        if data:
            # 在 CanMV IDE 的串行终端打印
            print("[RX raw]:", data)
    
            # 回传给电脑串口工具
            uart.write(b"[RX echo] ")
            uart.write(data)
            uart.write(b"\r\n")
    
        # 小延时，避免 CPU 空转过高
        time.sleep_ms(10)
    ```
    
- 串口0 ✅
  
    ![image.png](image%204.png)
    
    ```python
    【测不了，已经被系统占用了，只能看终端】
    ```
    

## 背面的各种IO，裸漏焊盘 ✅

全部用万用表测过了，和正面的电路是通的。

## 40P排针脚✅

所有3.3V和5V gnd  5V也要能供电工作✅

所有io都运行一次 io输入 ✅

- 代码
  
    ```python
    # 立创·庐山派 K230 CanMV
    # GPIO 排针逐个接地测试程序
    # 用法：
    # 1. 运行程序
    # 2. 程序提示 GPIOxx
    # 3. 用杜邦线把该 GPIO 接到 GND
    # 4. 检测到低电平后，程序提示松开
    # 5. 松开后自动进入下一个 GPIO
    
    from machine import Pin, FPIOA
    import time
    
    # 按图片里的 40Pin 物理排针顺序排列
    # 格式: (物理引脚编号, GPIO编号)
    TEST_GPIOS = [
        (3,  49),
        (5,  48),
        (7,  2),
        (8,  3),
        (10, 4),
        (11, 5),
        (12, 20),
        (13, 6),
        (15, 21),
        (16, 18),
        (18, 19),
        (19, 16),
        (21, 17),
        (22, 10),
        (23, 15),
        (24, 14),
        (26, 62),
        (27, 41),
        (28, 40),
        (29, 36),
        (31, 37),
        (32, 63),
        (33, 59),
        (35, 60),
        (36, 35),
        (37, 32),
        (38, 34),
        (40, 33),
    ]
    
    STABLE_COUNT = 5          # 连续读到多少次相同电平才认为稳定
    SAMPLE_DELAY_MS = 10      # 每次采样间隔
    REPORT_INTERVAL_MS = 1000 # 等待时每隔多久打印一次当前状态
    
    fpioa = FPIOA()
    
    def ticks_elapsed(start):
        return time.ticks_diff(time.ticks_ms(), start)
    
    def get_gpio_func(gpio_num):
        return getattr(FPIOA, "GPIO{}".format(gpio_num))
    
    def config_as_input_pullup(gpio_num):
        """
        只把当前这个 GPIO 配置成普通 GPIO + 输入上拉。
        其余 GPIO 不主动配置，避免同一时刻多个 IO 动作。
        """
        func = get_gpio_func(gpio_num)
    
        # 配成普通 GPIO，同时打开输入、上拉、施密特触发
        # oe=0 禁止输出，避免误输出
        fpioa.set_function(
            gpio_num,
            func,
            ie=1,
            oe=0,
            pu=1,
            pd=0,
            st=1
        )
    
        pin = Pin(gpio_num, Pin.IN, Pin.PULL_UP)
        time.sleep_ms(50)
        return pin
    
    def release_pin(pin):
        """
        当前 GPIO 测完后，改成输入无上下拉，降低对外部电路影响。
        """
        try:
            pin.init(Pin.IN, pull=Pin.PULL_NONE, drive=7)
        except Exception as e:
            print("释放引脚失败:", e)
    
    def wait_level_stable(pin, target_level, timeout_ms=None, report_text=""):
        """
        等待某个电平稳定出现。
        target_level: 0 或 1
        timeout_ms: None 表示一直等待
        """
        stable_cnt = 0
        start = time.ticks_ms()
        last_report = time.ticks_ms()
    
        while True:
            val = pin.value()
    
            if val == target_level:
                stable_cnt += 1
                if stable_cnt >= STABLE_COUNT:
                    return True
            else:
                stable_cnt = 0
    
            now = time.ticks_ms()
    
            if time.ticks_diff(now, last_report) >= REPORT_INTERVAL_MS:
                if report_text:
                    print(report_text, "当前读数:", val, "等待电平:", target_level)
                last_report = now
    
            if timeout_ms is not None:
                if time.ticks_diff(now, start) >= timeout_ms:
                    return False
    
            time.sleep_ms(SAMPLE_DELAY_MS)
    
    def main():
        print("")
        print("========== K230 GPIO 排针接地测试 ==========")
        print("测试方式：当前 GPIO 输入上拉，空闲应为 1，接 GND 后应为 0")
        print("注意：只接 GPIO 到 GND，不要接 3V3/5V0 到 GND")
        print("测试数量:", len(TEST_GPIOS))
        print("==========================================")
        print("")
    
        passed = []
        abnormal_high = []
    
        current_pin = None
    
        for index, item in enumerate(TEST_GPIOS):
            physical_pin, gpio_num = item
    
            if current_pin is not None:
                release_pin(current_pin)
                current_pin = None
                time.sleep_ms(100)
    
            print("")
            print("------------------------------------------")
            print("进度: {}/{}".format(index + 1, len(TEST_GPIOS)))
            print("请测试：物理引脚 Pin{} / GPIO{}".format(physical_pin, gpio_num))
    
            current_pin = config_as_input_pullup(gpio_num)
    
            # 先检查未接地时是否能读到高电平
            high_ok = wait_level_stable(
                current_pin,
                1,
                timeout_ms=1500,
                report_text="等待空闲高电平"
            )
    
            if high_ok:
                print("空闲高电平正常：GPIO{} = 1".format(gpio_num))
            else:
                print("异常提示：GPIO{} 未接地时没有稳定读到高电平".format(gpio_num))
                print("可能原因：该引脚已被外部拉低、短路到 GND、或外设占用")
                abnormal_high.append((physical_pin, gpio_num))
                print("请先松开/排查，程序会继续等待该脚恢复高电平...")
                wait_level_stable(
                    current_pin,
                    1,
                    timeout_ms=None,
                    report_text="等待恢复高电平"
                )
    
            print("现在请把 GPIO{} 接到 GND...".format(gpio_num))
    
            wait_level_stable(
                current_pin,
                0,
                timeout_ms=None,
                report_text="等待接地低电平"
            )
    
            print("PASS：GPIO{} 接地后稳定读到 0".format(gpio_num))
            passed.append((physical_pin, gpio_num))
    
            print("请松开 GPIO{} 与 GND 的连接...".format(gpio_num))
    
            wait_level_stable(
                current_pin,
                1,
                timeout_ms=None,
                report_text="等待松开后恢复高电平"
            )
    
            print("GPIO{} 已恢复高电平，进入下一个".format(gpio_num))
    
        if current_pin is not None:
            release_pin(current_pin)
    
        print("")
        print("========== 测试完成 ==========")
        print("通过数量:", len(passed), "/", len(TEST_GPIOS))
    
        if abnormal_high:
            print("")
            print("以下 GPIO 曾经出现“未接地时不是稳定高电平”：")
            for physical_pin, gpio_num in abnormal_high:
                print("Pin{} / GPIO{}".format(physical_pin, gpio_num))
        else:
            print("所有 GPIO 空闲高电平检查均正常")
    
        print("================================")
    
    main()
    ```
    

## FPC -ADC3个脚✅

- 代码备份-更改这个序号就可以 `adc = ADC(0)`
  
    ```python
    # 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
    # 开发板官网：www.lckfb.com
    # 技术支持常驻论坛，任何技术问题欢迎随时交流学习
    # 立创论坛：www.jlc-bbs.com/lckfb
    # 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
    # 不靠卖板赚钱，以培养中国工程师为己任
    from machine import ADC
    import time
    
    # 实例化 ADC 通道 0，用于读取模拟信号的数字值
    adc = ADC(0)
    
    # 主循环，持续运行程序逻辑
    while True:
        # 获取 ADC 通道 0 的采样值
        # ADC 采样值是一个无符号 16 位整数，范围为 0 到 65535
        adc_value = adc.read_u16()
    
        # 获取 ADC 通道 0 的电压值，单位为微伏（uV）
        adc_voltage_uv = adc.read_uv()
    
        # 将电压值从微伏转换为伏特（V）
        # 1 伏特 = 1,000,000 微伏
        adc_voltage_v = adc_voltage_uv / (1000 * 1000)
    
        # 打印采样值和电压值
        # 输出格式为 "ADC Value: <采样值>, Voltage: <微伏值> uV, <伏特值> V"
        print("ADC Value: %d, Voltage: %d uV, %.6f V" % (adc_value, adc_voltage_uv, adc_voltage_v))
    
        # 简单延时 100 毫秒，防止主循环运行速度过快
        time.sleep_ms(100)
    ```
    

# WAV 音频播放器✅

单击用户按键：播放 / 暂停

双击：下一首

三击：上一首

说明：把 WAV 文件放到 SD 卡 `/data/` 目录下即可。MP3 暂时不支持直接播放（CanMV K230 MicroPython 里没有 MP3 解码器，建议先用 ffmpeg/Audacity 转成 44.1kHz / 16bit 立体声 WAV）。

- 代码【单击播放/暂停，双击下一首，三击上一首】
  
    ```python
    # 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
    # 开发板官网：www.lckfb.com
    # 技术支持常驻论坛，任何技术问题欢迎随时交流学习
    # 立创论坛：www.jlc-bbs.com/lckfb
    # 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
    # 不靠卖板赚钱，以培养中国工程师为己任
    
    # WAV 播放器：单击=播放/暂停，双击=下一首，三击=上一首
    import os, time, _thread
    from machine import Pin, FPIOA
    from media.media import *
    from media.pyaudio import *
    import media.wave as wave
    
    # ---------- 引脚配置 ----------
    fpioa = FPIOA()
    fpioa.set_function(10, FPIOA.GPIO10)   # 功放 EN
    fpioa.set_function(64, FPIOA.GPIO64)   # 用户按键
    
    HT_CTRL = Pin(10, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    HT_CTRL.high()                          # 打开功放
    
    button = Pin(64, Pin.IN, Pin.PULL_DOWN) # 按下=高电平
    
    # ---------- 播放列表 ----------
    MUSIC_DIR = "/data/"             # WAV 文件放这里
    try:
        os.stat(MUSIC_DIR)
    except OSError:
        os.mkdir(MUSIC_DIR)
    
    playlist = sorted([
        MUSIC_DIR + "/" + f
        for f in os.listdir(MUSIC_DIR)
        if f.lower().endswith(".wav")
    ])
    if not playlist:
        raise RuntimeError("没有找到 wav 文件，请把 wav 放到 " + MUSIC_DIR)
    
    print("曲目列表:")
    for i, p in enumerate(playlist):
        print(" ", i, p)
    
    # ---------- 播放状态 ----------
    state = {
        "index": 0,
        "paused": False,
        "skip": False,     # 切歌信号（双击/三击置位）
        "running": True,
    }
    
    # ---------- 播放线程 ----------
    def play_thread():
        p = PyAudio()
        try:
            while state["running"]:
                path = playlist[state["index"]]
                print("▶ 播放:", path)
                stream = None
                wf = None
                try:
                    wf = wave.open(path, 'rb')
                    CHUNK = int(wf.get_framerate() / 25)
                    stream = p.open(
                        format=p.get_format_from_width(wf.get_sampwidth()),
                        channels=wf.get_channels(),
                        rate=wf.get_framerate(),
                        output=True,
                        frames_per_buffer=CHUNK,
                    )
                    stream.volume(vol=60)
    
                    data = wf.read_frames(CHUNK)
                    while data and not state["skip"] and state["running"]:
                        # 暂停：阻塞在这里但仍能响应切歌
                        while state["paused"] and not state["skip"] and state["running"]:
                            time.sleep_ms(50)
                        if state["skip"] or not state["running"]:
                            break
                        stream.write(data)
                        data = wf.read_frames(CHUNK)
    
                except BaseException as e:
                    import sys
                    sys.print_exception(e)
                finally:
                    if stream:
                        try: stream.stop_stream()
                        except: pass
                        try: stream.close()
                        except: pass
                    if wf:
                        try: wf.close()
                        except: pass
    
                if state["skip"]:
                    # 主线程已经改好 index，这里只清标志
                    state["skip"] = False
                else:
                    # 自然播完，自动下一首
                    state["index"] = (state["index"] + 1) % len(playlist)
        finally:
            p.terminate()
    
    _thread.start_new_thread(play_thread, ())
    
    # ---------- 按键多击识别 ----------
    DEBOUNCE_MS = 30      # 消抖
    CLICK_GAP_MS = 350    # 多击之间的最大间隔，超过则判定结束
    
    click_count = 0
    last_state = 0
    press_time = 0
    last_release_time = 0
    
    print("准备就绪：单击=播放/暂停，双击=下一首，三击=上一首")
    
    try:
        while True:
            s = button.value()
            now = time.ticks_ms()
    
            # 按下（上升沿）
            if s == 1 and last_state == 0:
                if time.ticks_diff(now, press_time) > DEBOUNCE_MS:
                    press_time = now
            # 松开（下降沿）
            elif s == 0 and last_state == 1:
                if time.ticks_diff(now, press_time) > DEBOUNCE_MS:
                    click_count += 1
                    last_release_time = now
            last_state = s
    
            # 判定一串多击是否结束
            if click_count > 0 and time.ticks_diff(now, last_release_time) > CLICK_GAP_MS and s == 0:
                if click_count == 1:
                    state["paused"] = not state["paused"]
                    print("⏯ 暂停状态:", state["paused"])
                elif click_count == 2:
                    state["index"] = (state["index"] + 1) % len(playlist)
                    state["paused"] = False
                    state["skip"] = True
                    print("⏭ 下一首 ->", playlist[state["index"]])
                else:  # >=3
                    state["index"] = (state["index"] - 1) % len(playlist)
                    state["paused"] = False
                    state["skip"] = True
                    print("⏮ 上一首 ->", playlist[state["index"]])
                click_count = 0
    
            time.sleep_ms(5)
    
    except KeyboardInterrupt:
        print("退出")
    finally:
        state["running"] = False
        state["skip"] = True
        state["paused"] = False
        time.sleep_ms(200)
        HT_CTRL.low()   # 关功放，防底噪
    ```
    

# 10.1寸屏幕测试✅

- 背光测试
  
    ```python
    # 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
    # 开发板官网：www.lckfb.com
    # 技术支持常驻论坛，任何技术问题欢迎随时交流学习
    # 立创论坛：www.jlc-bbs.com/lckfb
    # 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
    # 不靠卖板赚钱，以培养中国工程师为己任
    
    # WAV 播放器：单击=播放/暂停，双击=下一首，三击=上一首
    import os, time, _thread
    from machine import Pin, FPIOA
    from media.media import *
    from media.pyaudio import *
    import media.wave as wave
    
    # ---------- 引脚配置 ----------
    fpioa = FPIOA()
    fpioa.set_function(10, FPIOA.GPIO10)   # 功放 EN
    fpioa.set_function(64, FPIOA.GPIO64)   # 用户按键
    
    HT_CTRL = Pin(10, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
    HT_CTRL.high()                          # 打开功放
    
    button = Pin(64, Pin.IN, Pin.PULL_DOWN) # 按下=高电平
    
    # ---------- 播放列表 ----------
    MUSIC_DIR = "/data/"             # WAV 文件放这里
    try:
        os.stat(MUSIC_DIR)
    except OSError:
        os.mkdir(MUSIC_DIR)
    
    playlist = sorted([
        MUSIC_DIR + "/" + f
        for f in os.listdir(MUSIC_DIR)
        if f.lower().endswith(".wav")
    ])
    if not playlist:
        raise RuntimeError("没有找到 wav 文件，请把 wav 放到 " + MUSIC_DIR)
    
    print("曲目列表:")
    for i, p in enumerate(playlist):
        print(" ", i, p)
    
    # ---------- 播放状态 ----------
    state = {
        "index": 0,
        "paused": False,
        "skip": False,     # 切歌信号（双击/三击置位）
        "running": True,
    }
    
    # ---------- 播放线程 ----------
    def play_thread():
        p = PyAudio()
        try:
            while state["running"]:
                path = playlist[state["index"]]
                print("▶ 播放:", path)
                stream = None
                wf = None
                try:
                    wf = wave.open(path, 'rb')
                    CHUNK = int(wf.get_framerate() / 25)
                    stream = p.open(
                        format=p.get_format_from_width(wf.get_sampwidth()),
                        channels=wf.get_channels(),
                        rate=wf.get_framerate(),
                        output=True,
                        frames_per_buffer=CHUNK,
                    )
                    stream.volume(vol=60)
    
                    data = wf.read_frames(CHUNK)
                    while data and not state["skip"] and state["running"]:
                        # 暂停：阻塞在这里但仍能响应切歌
                        while state["paused"] and not state["skip"] and state["running"]:
                            time.sleep_ms(50)
                        if state["skip"] or not state["running"]:
                            break
                        stream.write(data)
                        data = wf.read_frames(CHUNK)
    
                except BaseException as e:
                    import sys
                    sys.print_exception(e)
                finally:
                    if stream:
                        try: stream.stop_stream()
                        except: pass
                        try: stream.close()
                        except: pass
                    if wf:
                        try: wf.close()
                        except: pass
    
                if state["skip"]:
                    # 主线程已经改好 index，这里只清标志
                    state["skip"] = False
                else:
                    # 自然播完，自动下一首
                    state["index"] = (state["index"] + 1) % len(playlist)
        finally:
            p.terminate()
    
    _thread.start_new_thread(play_thread, ())
    
    # ---------- 按键多击识别 ----------
    DEBOUNCE_MS = 30      # 消抖
    CLICK_GAP_MS = 350    # 多击之间的最大间隔，超过则判定结束
    
    click_count = 0
    last_state = 0
    press_time = 0
    last_release_time = 0
    
    print("准备就绪：单击=播放/暂停，双击=下一首，三击=上一首")
    
    try:
        while True:
            s = button.value()
            now = time.ticks_ms()
    
            # 按下（上升沿）
            if s == 1 and last_state == 0:
                if time.ticks_diff(now, press_time) > DEBOUNCE_MS:
                    press_time = now
            # 松开（下降沿）
            elif s == 0 and last_state == 1:
                if time.ticks_diff(now, press_time) > DEBOUNCE_MS:
                    click_count += 1
                    last_release_time = now
            last_state = s
    
            # 判定一串多击是否结束
            if click_count > 0 and time.ticks_diff(now, last_release_time) > CLICK_GAP_MS and s == 0:
                if click_count == 1:
                    state["paused"] = not state["paused"]
                    print("⏯ 暂停状态:", state["paused"])
                elif click_count == 2:
                    state["index"] = (state["index"] + 1) % len(playlist)
                    state["paused"] = False
                    state["skip"] = True
                    print("⏭ 下一首 ->", playlist[state["index"]])
                else:  # >=3
                    state["index"] = (state["index"] - 1) % len(playlist)
                    state["paused"] = False
                    state["skip"] = True
                    print("⏮ 上一首 ->", playlist[state["index"]])
                click_count = 0
    
            time.sleep_ms(5)
    
    except KeyboardInterrupt:
        print("退出")
    finally:
        state["running"] = False
        state["skip"] = True
        state["paused"] = False
        time.sleep_ms(200)
        HT_CTRL.low()   # 关功放，防底噪
    ```
    
- 显示测试
  
    ```python
    import time, os, urandom, sys
    
    from media.display import *
    from media.media import *
    
    DISPLAY_WIDTH = ALIGN_UP(1280, 16)
    DISPLAY_HEIGHT = 800
    
    def display_test():
        print("display test")
    
        # create image for drawing
        img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
    
        # use lcd as display output
        Display.init(Display.ILI9881, width = DISPLAY_WIDTH, height = DISPLAY_HEIGHT, to_ide = True)
    
        try:
            while True:
                img.clear()
                for i in range(10):
                    x = (urandom.getrandbits(11) % img.width())
                    y = (urandom.getrandbits(11) % img.height())
                    r = (urandom.getrandbits(8))
                    g = (urandom.getrandbits(8))
                    b = (urandom.getrandbits(8))
                    size = (urandom.getrandbits(30) % 64) + 32
                    # If the first argument is a scaler then this method expects
                    # to see x, y, and text. Otherwise, it expects a (x,y,text) tuple.
                    # Character and string rotation can be done at 0, 90, 180, 270, and etc. degrees.
                    img.draw_string_advanced(x,y,size, "Hello World!，你好世界！！！", color = (r, g, b),)
    
                # draw result to screen
                Display.show_image(img)
    
                time.sleep(1)
                os.exitpoint()
        except KeyboardInterrupt as e:
            print("user stop: ", e)
        except BaseException as e:
            import sys
            sys.print_exception(e)
    
        # deinit display
        Display.deinit()
        os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
        time.sleep_ms(100)
    
    if __name__ == "__main__":
        os.exitpoint(os.EXITPOINT_ENABLE)
        display_test()
    
    ```
    
- 摄像头显示测试
  
    ```python
    import time, os, urandom, sys
    
    from media.display import *
    from media.media import *
    
    DISPLAY_WIDTH = ALIGN_UP(1280, 16)
    DISPLAY_HEIGHT = 800
    
    def display_test():
        print("display test")
    
        # create image for drawing
        img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
    
        # use lcd as display output
        Display.init(Display.ILI9881, width = DISPLAY_WIDTH, height = DISPLAY_HEIGHT, to_ide = True)
    
        try:
            while True:
                img.clear()
                for i in range(10):
                    x = (urandom.getrandbits(11) % img.width())
                    y = (urandom.getrandbits(11) % img.height())
                    r = (urandom.getrandbits(8))
                    g = (urandom.getrandbits(8))
                    b = (urandom.getrandbits(8))
                    size = (urandom.getrandbits(30) % 64) + 32
                    # If the first argument is a scaler then this method expects
                    # to see x, y, and text. Otherwise, it expects a (x,y,text) tuple.
                    # Character and string rotation can be done at 0, 90, 180, 270, and etc. degrees.
                    img.draw_string_advanced(x,y,size, "Hello World!，你好世界！！！", color = (r, g, b),)
    
                # draw result to screen
                Display.show_image(img)
    
                time.sleep(1)
                os.exitpoint()
        except KeyboardInterrupt as e:
            print("user stop: ", e)
        except BaseException as e:
            import sys
            sys.print_exception(e)
    
        # deinit display
        Display.deinit()
        os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
        time.sleep_ms(100)
    
    if __name__ == "__main__":
        os.exitpoint(os.EXITPOINT_ENABLE)
        display_test()
    
    ```
    

# SD NAND✅