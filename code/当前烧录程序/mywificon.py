# WiFi 配网功能（热点 + 网页配网） - 立创·庐山派-K230-CanMV
# 开启热点 → 手机连接 → 网页选择WiFi输密码 → K230连接WiFi → 关闭热点

import os, time, image, network, socket
from media.display import *
from media.media import *
from machine import TOUCH

# ============================================================
# 参数
# ============================================================
DISPLAY_WIDTH  = 800
DISPLAY_HEIGHT = 480

AP_SSID   = "LushanPi-Config"
AP_KEY    = "12345678"
HTTP_PORT = 80

# ============================================================
# WiFi 状态
# ============================================================
_sta = None
_connected = False
_connected_ssid = ""
_connected_ip = ""

def _get_sta():
    global _sta
    if _sta is None:
        _sta = network.WLAN(network.STA_IF)
    return _sta

def is_connected():
    global _connected, _connected_ssid, _connected_ip
    try:
        sta = _get_sta()
        if sta.active() and sta.isconnected():
            _connected = True
            raw_ssid = sta.config('ssid')
            if isinstance(raw_ssid, bytes):
                _connected_ssid = raw_ssid.decode()
            else:
                _connected_ssid = str(raw_ssid) if raw_ssid else ""
            _connected_ip = str(sta.ifconfig()[0])
            return True
    except:
        pass
    _connected = False
    return False

def get_connected_info():
    if is_connected():
        ssid = _connected_ssid
        if isinstance(ssid, bytes):
            ssid = ssid.decode()
        return str(ssid) if ssid else "", str(_connected_ip) if _connected_ip else ""
    return "", ""

def scan_networks():
    sta = _get_sta()
    if not sta.active():
        sta.active(True)
    results = []
    try:
        for w in sta.scan():
            raw = w.ssid
            ssid = raw.decode() if isinstance(raw, bytes) else str(raw) if raw else ""
            if not ssid:
                continue
            rssi = w.rssi
            found = False
            for i, (s, r) in enumerate(results):
                if s == ssid:
                    if rssi > r:
                        results[i] = (ssid, rssi)
                    found = True
                    break
            if not found:
                results.append((ssid, rssi))
        results.sort(key=lambda x: x[1], reverse=True)
    except:
        pass
    return results

# ============================================================
# WiFi 图标（主界面右上角使用）
# ============================================================
def draw_icon(img, x, y):
    w, h = 28, 22
    if is_connected():
        c = (50, 220, 120)
    else:
        c = (220, 50, 50)
    cx, cy = x + w // 2, y + h - 2
    img.draw_circle(cx, cy, 6, color=c, thickness=2, fill=False)
    img.draw_circle(cx, cy, 12, color=c, thickness=2, fill=False)
    img.draw_circle(cx, cy, 18, color=c, thickness=2, fill=False)
    img.draw_circle(cx, cy - 2, 3, color=c, thickness=1, fill=True)
    if not is_connected():
        img.draw_line(x + 2, y + 2, x + w - 2, y + h - 2, color=(255, 60, 50), thickness=2)
        img.draw_line(x + w - 2, y + 2, x + 2, y + h - 2, color=(255, 60, 50), thickness=2)

# ============================================================
# 热点 + HTTP 服务器
# ============================================================
_ap = None
_server = None
_ap_active = False
_ap_ip = ""
_scan_cache = []
_client_connected = False
_received_ssid = ""
_received_pwd = ""

def start_ap():
    global _ap, _ap_active, _ap_ip
    try:
        _ap = network.WLAN(network.AP_IF)
        if not _ap.active():
            _ap.active(True)
        _ap.config(ssid=AP_SSID, key=AP_KEY)
        time.sleep(2)
        _ap_ip = _ap.ifconfig()[0]
        _ap_active = True
        print("[WiFi] 热点已开启: " + AP_SSID + " IP: " + _ap_ip)
        return True
    except Exception as e:
        print("[WiFi] 热点开启失败: " + str(e))
        return False

def stop_ap():
    global _ap, _ap_active, _server, _ap_ip
    try:
        if _server:
            _server.close()
    except:
        pass
    _server = None
    try:
        if _ap:
            _ap.active(False)
    except:
        pass
    _ap = None
    _ap_active = False
    _ap_ip = ""
    print("[WiFi] 热点已关闭")

def start_server():
    global _server
    try:
        _server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _server.bind(('0.0.0.0', HTTP_PORT))
        _server.listen(1)
        _server.settimeout(0.3)
        print("[WiFi] HTTP 服务器已启动, 端口 " + str(HTTP_PORT))
    except Exception as e:
        print("[WiFi] 服务器启动失败: " + str(e))
        _server = None

def html_escape(s):
    if isinstance(s, bytes):
        s = s.decode()
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def build_config_page():
    """生成配网网页"""
    networks = _scan_cache if _scan_cache else [("(点击刷新)", 0)]
    options = ""
    for ssid, rssi in networks:
        ssid_safe = html_escape(ssid)
        options += '<option value="' + ssid_safe + '">' + ssid_safe + ' (' + str(rssi) + 'dBm)</option>\n'

    html = """HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n"""
    html += """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WiFi配网</title>"""
    html += """<style>body{font-family:Arial;background:#1a1e2b;color:#e0e5f0;padding:20px;text-align:center}"""
    html += """h2{color:#32d4a0}select,input{width:90%%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #444;background:#262a38;color:#fff;font-size:16px}"""
    html += """button{width:90%%;padding:14px;margin-top:10px;background:#32d4a0;color:#fff;border:none;border-radius:8px;font-size:18px}"""
    html += """</style></head><body><h2>庐山派 WiFi 配网</h2>"""
    html += """<form method="post" action="/connect"><select name="ssid">""" + options + """</select>"""
    html += """<input type="password" name="pwd" placeholder="WiFi 密码（至少8位）">"""
    html += """<button type="submit">连接 WiFi</button></form>"""
    html += """<p style="color:#888;font-size:12px;margin-top:20px">连接后热点将自动关闭</p></body></html>"""
    return html

def build_ok_page(ssid):
    """连接成功后的确认页"""
    html = """HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n"""
    html += """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">"""
    html += """<title>连接成功</title><style>body{font-family:Arial;background:#1a1e2b;color:#e0e5f0;text-align:center;padding:30px}"""
    html += """h2{color:#32d4a0}.ok{font-size:60px}</style></head><body>"""
    html += """<div class="ok">✓</div><h2>连接成功</h2><p>已连接到 """ + html_escape(ssid) + """</p>"""
    html += """<p style="color:#888">热点已关闭，设备将自动连接WiFi</p></body></html>"""
    return html

def handle_http():
    """非阻塞处理 HTTP 请求，返回 True 表示收到配网信息"""
    global _client_connected, _received_ssid, _received_pwd

    if _server is None:
        return False

    try:
        conn, addr = _server.accept()
        _client_connected = True
        print("[WiFi] 客户端连接: " + str(addr))
    except OSError:
        return False

    try:
        conn.settimeout(2)
        req = b""
        try:
            while True:
                chunk = conn.recv(256)
                if not chunk:
                    break
                req += chunk
                if b"\r\n\r\n" in req:
                    break
        except:
            pass

        req_str = req.decode('utf-8', 'ignore')

        if req_str.startswith("POST /connect"):
            # 解析表单
            body = ""
            if "\r\n\r\n" in req_str:
                body = req_str.split("\r\n\r\n", 1)[1]
            ssid = ""
            pwd = ""
            for part in body.split('&'):
                if '=' in part:
                    k, v = part.split('=', 1)
                    v = v.replace('+', ' ').replace('%20', ' ')
                    if k == 'ssid':
                        ssid = v
                    elif k == 'pwd':
                        pwd = v

            if ssid and len(pwd) >= 8:
                _received_ssid = ssid
                _received_pwd = pwd
                conn.send(build_ok_page(ssid).encode())
                conn.close()
                return True
            else:
                # 密码不足 8 位，返回错误
                err_html = """HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"""
                err_html += """<html><body style="font-family:Arial;text-align:center;padding:20px;background:#1a1e2b;color:#e0e5f0">"""
                err_html += """<h2 style="color:#f04040">错误</h2><p>密码至少需要 8 位</p>"""
                err_html += """<a href="/" style="color:#32d4a0">返回重试</a></body></html>"""
                conn.send(err_html.encode())
                conn.close()
                return False
        else:
            # GET / → 配网页面
            conn.send(build_config_page().encode())
            conn.close()
            return False

    except Exception as e:
        print("[WiFi] HTTP 异常: " + str(e))
    finally:
        try:
            conn.close()
        except:
            pass

    return False

def do_connect(ssid, pwd):
    """连接 WiFi"""
    global _connected, _connected_ssid, _connected_ip
    sta = _get_sta()
    if not sta.active():
        sta.active(True)

    if isinstance(ssid, bytes):
        ssid = ssid.decode()
    sta.connect(ssid, pwd)

    for _ in range(15):
        if sta.isconnected():
            break
        time.sleep(1)
        sta.connect(ssid, pwd)

    timeout = 60
    while sta.ifconfig()[0] == '0.0.0.0' and timeout > 0:
        time.sleep(0.1)
        timeout -= 1

    if sta.isconnected():
        _connected = True
        _connected_ssid = ssid
        _connected_ip = sta.ifconfig()[0]
        return True
    _connected = False
    return False

# ============================================================
# UI 布局
# ============================================================
BTN_RETURN = (680, 10, 110, 36)
TOGGLE_X, TOGGLE_Y, TOGGLE_W, TOGGLE_H = 40, 190, 240, 50

# ============================================================
# 触摸
# ============================================================
def in_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx + rw and ry <= py <= ry + rh

# ============================================================
# 绘制
# ============================================================
def draw_ui(img, status_text):
    img.clear()
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, color=(18, 20, 32), fill=True)

    # 标题栏
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, 50, color=(28, 31, 46), fill=True)
    img.draw_string_advanced(20, 12, 20, "WiFi 配网", color=(255, 255, 255))
    img.draw_rectangle(BTN_RETURN[0], BTN_RETURN[1], BTN_RETURN[2], BTN_RETURN[3],
                       color=(100, 105, 125), fill=True)
    img.draw_string_advanced(700, 18, 16, "← 返回", color=(255, 255, 255))

    y = 62

    # ── 热点信息 ──
    img.draw_string_advanced(20, y, 14, "━━ 热点信息 ━━", color=(160, 165, 180))
    y += 24
    img.draw_string_advanced(30, y, 14, "名称: " + AP_SSID, color=(200, 210, 230))
    y += 22
    img.draw_string_advanced(30, y, 14, "密码: " + AP_KEY, color=(200, 210, 230))
    y += 22
    if _ap_active:
        img.draw_string_advanced(30, y, 14, "IP: " + _ap_ip + "  端口: " + str(HTTP_PORT),
                                 color=(50, 210, 130))
    else:
        img.draw_string_advanced(30, y, 14, "IP: ---  端口: ---", color=(120, 125, 140))
    y += 28

    # ── 开关按钮 ──
    tx, ty, tw, th = TOGGLE_X, TOGGLE_Y, TOGGLE_W, TOGGLE_H
    if _ap_active:
        toggle_color = (50, 200, 130)
        toggle_label = "● 热点已开启（点击关闭）"
    else:
        toggle_color = (80, 85, 100)
        toggle_label = "○ 热点已关闭（点击开启）"
    img.draw_rectangle(tx, ty, tw, th, color=toggle_color, fill=True)
    img.draw_rectangle(tx, ty, tw, th, color=(120, 130, 150), thickness=1, fill=False)
    lw = len(toggle_label) * 12
    img.draw_string_advanced(tx + (tw - lw) // 2, ty + 15, 16, toggle_label, color=(255, 255, 255))

    y = TOGGLE_Y + TOGGLE_H + 20

    # ── 状态 ──
    img.draw_string_advanced(20, y, 14, "━━ 状态 ━━", color=(160, 165, 180))
    y += 24
    img.draw_string_advanced(30, y, 14, status_text, color=(200, 210, 230))
    y += 28

    # ── 已连接 WiFi 信息 ──
    img.draw_string_advanced(20, y, 14, "━━ 已连接 WiFi ━━", color=(160, 165, 180))
    y += 24
    wssid, wip = get_connected_info()
    if wssid:
        img.draw_string_advanced(30, y, 14, "名称: " + wssid, color=(50, 210, 130))
        y += 22
        img.draw_string_advanced(30, y, 14, "IP:   " + wip, color=(50, 210, 130))
    else:
        img.draw_string_advanced(30, y, 14, "未连接 WiFi", color=(200, 60, 50))
        y += 22
        img.draw_string_advanced(30, y, 14, "请用手机连接上方热点进行配网", color=(120, 125, 140))

# ============================================================
# 主入口
# ============================================================
def main():
    global _ap_active, _scan_cache, _client_connected
    global _received_ssid, _received_pwd

    print("[WiFi] 启动配网")

    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    MediaManager.init()
    tp = TOUCH(0)

    _ap_active = False
    _scan_cache = []
    _client_connected = False
    _received_ssid = ""
    _received_pwd = ""

    status_text = "点击开关开启热点"
    pressed = False
    debounce = 0
    last_scan = 0

    try:
        while True:
            os.exitpoint()
            now = time.ticks_ms()

            # 触摸
            points = tp.read(5)
            if points:
                if not pressed:
                    pt = points[0]
                    x, y = pt.x, pt.y
                    if time.ticks_diff(now, debounce) < 0:
                        pressed = True
                        continue

                    # 返回
                    if in_rect(x, y, *BTN_RETURN):
                        if _ap_active:
                            stop_ap()
                        debounce = time.ticks_add(now, 500)
                        pressed = True
                        print("[WiFi] 退出")
                        break

                    # 开关按钮
                    if in_rect(x, y, TOGGLE_X, TOGGLE_Y, TOGGLE_W, TOGGLE_H):
                        if _ap_active:
                            stop_ap()
                            status_text = "热点已关闭"
                        else:
                            if start_ap():
                                start_server()
                                _scan_cache = scan_networks()
                                status_text = "热点已开启，等待设备连接..."
                            else:
                                status_text = "热点开启失败"
                        debounce = time.ticks_add(now, 600)
                        pressed = True
                        continue

                    debounce = time.ticks_add(now, 200)
                    pressed = True
            else:
                pressed = False

            # 热点运行时：处理 HTTP + 扫描
            if _ap_active:
                # 处理配网请求
                if handle_http():
                    if _received_ssid and _received_pwd:
                        ssid = _received_ssid
                        pwd = _received_pwd
                        status_text = "正在连接 " + ssid + " ..."
                        # 立即绘制状态
                        img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
                        draw_ui(img, status_text)
                        Display.show_image(img)

                        success = do_connect(ssid, pwd)
                        if success:
                            status_text = "已连接到 " + ssid + "，热点已关闭"
                            stop_ap()
                        else:
                            status_text = "连接 " + ssid + " 失败，热点保持开启"
                        _received_ssid = ""
                        _received_pwd = ""

                # 每 5 秒扫描一次
                if time.ticks_diff(now, last_scan) > 5000:
                    _scan_cache = scan_networks()
                    last_scan = now

            # 绘制 UI
            img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
            draw_ui(img, status_text)
            Display.show_image(img)

            time.sleep_ms(50)

    except KeyboardInterrupt:
        print("[WiFi] 用户停止")
    except BaseException as e:
        print("[WiFi] 异常: " + str(e))
        import sys
        sys.print_exception(e)
    finally:
        stop_ap()
        Display.deinit()
        time.sleep_ms(60)
        MediaManager.deinit()

if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)
    main()
