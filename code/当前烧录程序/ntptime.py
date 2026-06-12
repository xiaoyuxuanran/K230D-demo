from time import gmtime
import socket
import struct
import machine

# 时区偏移（秒）
TIMEZONE_OFFSET = 8 * 3600  # UTC+8

# NTP服务器地址
host = "pool.ntp.org"
# NTP查询超时时间
timeout = 1

def time():
    """
    从NTP服务器获取时间。
    """
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B  # NTP请求包的第一个字节
    addr = socket.getaddrinfo(host, 123)[0][-1]  # 获取NTP服务器的IP地址
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建UDP套接字
    try:
        s.settimeout(timeout)  # 设置套接字超时时间
        s.sendto(NTP_QUERY, addr)  # 发送NTP请求
        msg = s.recv(48)  # 接收NTP响应
    finally:
        s.close()  # 关闭套接字
    val = struct.unpack("!I", msg[40:44])[0]  # 解析NTP响应中的时间戳

    # 2024-01-01 00:00:00 转换为NTP时间戳
    MIN_NTP_TIMESTAMP = 3913056000

    # Y2036问题修复
    # NTP时间戳是一个32位的秒数计数器，在2036年2月7日06:28:16会回绕到0。
    # 我们知道这段软件是在2024年或之后编写的，所以小于MIN_NTP_TIMESTAMP的时间戳是不可能的。
    # 如果时间戳小于MIN_NTP_TIMESTAMP，很可能是因为NTP时间回绕到了2^32秒之前。
    # 因此在这种情况下，我们需要加上额外的2^32秒，以获得正确的时间戳。
    # 这意味着这段代码将在2160年之前有效，更精确地说，在2160年2月7日06:28:15之后无效。
    if val < MIN_NTP_TIMESTAMP:
        val += 0x100000000  # 加上额外的2^32秒

    # 将NTP时间戳转换为我们内部的时间格式
    EPOCH_YEAR = gmtime(0)[0]  # 获取内部时间的纪元年份
    if EPOCH_YEAR == 2000:
        # 从2000年1月1日到1900年1月1日的秒数
        NTP_DELTA = 3155673600
    elif EPOCH_YEAR == 1970:
        # 从1970年1月1日到1900年1月1日的秒数
        NTP_DELTA = 2208988800
    else:
        raise Exception("不支持的纪元年份: {}".format(EPOCH_YEAR))

    return val - NTP_DELTA  # 返回转换后的UTC时间戳

def settime():
    """
    获取UTC时间，并将其调整为UTC+8时间，然后设置RTC时间。
    """
    # 获取UTC时间
    t = time()
    
    # 调整为UTC+8时间
    t += TIMEZONE_OFFSET
    
    # 将时间转换为gmtime格式
    tm = gmtime(t)
    
    # 设置RTC时间
    rtc = machine.RTC()
    rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))

# 保留原始的ntptime.settime以便在其他地方使用
original_settime = settime

# 替换settime为我们新的带有时区偏移的版本
settime = settime

