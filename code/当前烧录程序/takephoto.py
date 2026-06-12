# 相机拍照功能 - 立创·庐山派-K230-CanMV
# 触摸虚拟按钮：拍照 / 退出，拍照时蜂鸣器响一声

import time, os, image
from media.sensor import Sensor, CAM_CHN_ID_0
from media.display import *
from media.media import *
from machine import TOUCH
from machine import PWM
from machine import Pin
from machine import FPIOA

# ============================================================
# 参数
# ============================================================
SENSOR_ID = 2
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480
PHOTO_DIR = "/data/code/picture"
BUZZER_PIN = 61

# ============================================================
# 全局硬件引用（单例）
# ============================================================
_fpioa = None
_beep_pwm = None
sensor = None
tp = None
photo_should_exit = False

# ============================================================
# 蜂鸣器
# ============================================================
def beep_init():
    global _fpioa, _beep_pwm
    if _beep_pwm is not None:
        return
    if _fpioa is None:
        _fpioa = FPIOA()
    _fpioa.set_function(BUZZER_PIN, FPIOA.PWM1)
    _beep_pwm = PWM(1)
    _beep_pwm.freq(4000)

def beep():
    """短促鸣叫一声"""
    if _beep_pwm is None:
        return
    try:
        _beep_pwm.duty_u16(32768)       # 50% 占空比，响
        time.sleep_ms(80)
        _beep_pwm.duty_u16(0)           # 关闭
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
# 拍照存储
# ============================================================
def ensure_photo_dir():
    try:
        os.stat(PHOTO_DIR)
    except OSError:
        os.mkdir(PHOTO_DIR)

def get_next_photo_name():
    """自动编号: photo_00001.jpg ~ photo_99999.jpg"""
    try:
        existing = [f for f in os.listdir(PHOTO_DIR)
                    if f.startswith("photo_") and f.endswith(".jpg")]
        nums = []
        for f in existing:
            try:
                nums.append(int(f[6:11]))
            except:
                pass
        next_num = max(nums) + 1 if nums else 1
    except:
        next_num = 1
    return f"{PHOTO_DIR}/photo_{next_num:05d}.jpg"

def save_photo(img, filename):
    """压缩 JPEG 并写入文件"""
    data = img.compress(quality=95)
    with open(filename, "wb") as f:
        f.write(data)

# ============================================================
# UI 按钮坐标
# ============================================================
BTN_PHOTO_X, BTN_PHOTO_Y, BTN_PHOTO_W, BTN_PHOTO_H = 260, 400, 280, 56
BTN_EXIT_X,  BTN_EXIT_Y,  BTN_EXIT_W,  BTN_EXIT_H  = 682, 14, 104, 36

# ============================================================
# 触摸检测
# ============================================================
def in_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx + rw and ry <= py <= ry + rh

touch_pressed = False
debounce_until = 0

def handle_touch(points):
    global photo_should_exit, touch_pressed, debounce_until
    now = time.ticks_ms()

    if not points:
        touch_pressed = False
        return

    if time.ticks_diff(debounce_until, now) > 0:
        return

    pt = points[0]
    x, y = pt.x, pt.y

    is_down = not touch_pressed
    touch_pressed = True

    if not is_down:
        return

    # 退出按钮
    if in_rect(x, y, BTN_EXIT_X - 8, BTN_EXIT_Y - 8, BTN_EXIT_W + 16, BTN_EXIT_H + 16):
        photo_should_exit = True
        debounce_until = time.ticks_add(now, 400)
        return

    # 拍照按钮
    if in_rect(x, y, BTN_PHOTO_X - 12, BTN_PHOTO_Y - 12, BTN_PHOTO_W + 24, BTN_PHOTO_H + 24):
        debounce_until = time.ticks_add(now, 600)
        return True

    return False

# ============================================================
# UI 绘制
# ============================================================
photo_count = 0

def draw_ui(img):
    # 半透明遮罩条 — 底部按钮区
    img.draw_rectangle(0, DISPLAY_HEIGHT - 75, DISPLAY_WIDTH, 75,
                       color=(0, 0, 0, 128), fill=True)

    # 拍照按钮（圆形大按钮）
    cx, cy = 400, 438
    r = 30
    img.draw_circle(cx, cy + 2, r + 1, color=(60, 60, 60), thickness=3, fill=True)
    img.draw_circle(cx, cy, r, color=(255, 255, 255), thickness=3, fill=True)
    img.draw_circle(cx, cy, r - 4, color=(50, 50, 50), thickness=2, fill=False)
    # 中心快门图标
    inner = 12
    img.draw_circle(cx, cy, inner, color=(200, 200, 200), thickness=2, fill=False)
    img.draw_circle(cx, cy, inner - 4, color=(230, 230, 230), thickness=1, fill=True)

    # 拍照文字
    img.draw_string_advanced(cx - 16, DISPLAY_HEIGHT - 22, 18, "拍照", color=(255, 255, 255))

    # 退出按钮（顶部右侧）
    img.draw_rectangle(BTN_EXIT_X, BTN_EXIT_Y, BTN_EXIT_W, BTN_EXIT_H,
                       color=(220, 60, 50), fill=True)
    img.draw_rectangle(BTN_EXIT_X, BTN_EXIT_Y, BTN_EXIT_W, BTN_EXIT_H,
                       color=(180, 40, 35), thickness=2, fill=False)
    img.draw_string_advanced(BTN_EXIT_X + 21, BTN_EXIT_Y + 8, 16, "退出",
                             color=(255, 255, 255))

    # 右上角已拍张数
    img.draw_string_advanced(10, 10, 16, f"已拍: {photo_count}", color=(255, 255, 255))

# ============================================================
# 硬件初始化（每次进入调用）
# ============================================================
def init_photo():
    global sensor, tp, photo_should_exit, photo_count

    photo_should_exit = False
    photo_count = 0

    beep_init()
    ensure_photo_dir()

    sensor = Sensor(id=SENSOR_ID)
    sensor.reset()
    sensor.set_framesize(width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, chn=CAM_CHN_ID_0)
    sensor.set_pixformat(Sensor.RGB565, chn=CAM_CHN_ID_0)

    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    MediaManager.init()

    sensor.run()

    tp = TOUCH(0)

# ============================================================
# 清理
# ============================================================
def deinit_photo():
    global sensor
    if sensor:
        try:
            sensor.stop()
        except:
            pass
        sensor = None
    Display.deinit()
    time.sleep_ms(60)
    MediaManager.deinit()

# ============================================================
# 主循环
# ============================================================
def main():
    global photo_should_exit, photo_count, touch_pressed, debounce_until

    init_photo()

    touch_pressed = False
    debounce_until = 0

    print("[相机] 已启动, 按拍照按钮拍照, 退出按钮返回主界面")

    try:
        while True:
            os.exitpoint()

            # 摄像头帧
            img = sensor.snapshot(chn=CAM_CHN_ID_0)

            # 触摸
            points = tp.read(5)
            if handle_touch(points):
                # 拍照
                photo_count += 1
                filename = get_next_photo_name()
                save_photo(img, filename)
                beep()
                print(f"[相机] 拍照: {filename}")

            if photo_should_exit:
                print("[相机] 退出")
                break

            # 绘制 UI 叠加层
            draw_ui(img)

            # 显示
            Display.show_image(img)

            time.sleep_ms(30)

    except KeyboardInterrupt:
        print("[相机] 用户停止")
    except BaseException as e:
        print(f"[相机] 异常: {e}")
    finally:
        deinit_photo()

if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()
