# 配置 tcp/udp socket 调试工具
import socket
import time

PORT = 60000

def client():
    # 获取 IP 地址及端口号
    ai = socket.getaddrinfo("10.100.228.5", PORT)
    # ai = socket.getaddrinfo("10.10.1.94", PORT)
    print("地址信息:", ai)
    addr = ai[0][-1]

    print("连接地址:", addr)
    # 创建 socket 对象
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    # 连接到指定地址
    s.connect(addr)

    for i in range(10):
        msg = "K230 TCP 客户端发送测试 {0} \r\n".format(i)
        print(msg)
        # 发送字符串数据
        print(s.write(msg))
        time.sleep(0.2)

    # 延时 1 秒后关闭 socket
    time.sleep(1)
    s.close()
    print("结束")

# 运行客户端程序
client()