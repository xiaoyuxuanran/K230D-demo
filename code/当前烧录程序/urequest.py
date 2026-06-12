import usocket

# 定义一个函数来打开 URL 并处理 HTTP 请求
def urlopen(url, data=None, method="GET"):
    # 如果提供了 data 参数并且 method 为 GET，则改为 POST 方法
    if data is not None and method == "GET":
        method = "POST"
        
    try:
        # 尝试解析 URL，分离协议、主机名、路径
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        # 如果 URL 格式不符合预期，则尝试另一种方式解析
        proto, dummy, host = url.split("/", 2)
        path = ""
        
        # 根据协议确定端口号
    if proto == "http:":
        port = 80
    elif proto == "https:":
        import ussl # 引入 SSL/TLS 支持

        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)
        
    # 如果主机名中包含冒号，说明可能指定了端口
    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)
        
    # 获取地址信息，包括 IP 地址等
    ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
    ai = ai[0]  # 取第一个结果
    
    # 创建一个 TCP 套接字
    s = usocket.socket(ai[0], ai[1], ai[2])
    try:
        # 连接到服务器
        s.connect(ai[-1])
        # 如果是 HTTPS 协议，则需要进行 SSL 包装
        if proto == "https:":
            s = ussl.wrap_socket(s, server_hostname=host)
            
        # 向服务器写入 HTTP 请求头
        s.write(method)
        s.write(b" /")
        s.write(path)
        s.write(b" HTTP/1.0\r\nHost: ")
        s.write(host)
        s.write(b"\r\n")
        
        # 如果有数据要发送，则写入 Content-Length 头
        if data:
            s.write(b"Content-Length: ")
            s.write(str(len(data)))
            s.write(b"\r\n")
        s.write(b"\r\n")    # 结束请求头
        
        # 如果有数据，则发送数据体
        if data:
            s.write(data)
            
        # 读取服务器返回的第一行，即状态行
        l = s.readline()
        l = l.split(None, 2)
        # print(l)
        status = int(l[1])   # 获取状态码
        
        # 读取响应头直到遇到空行
        while True:
            l = s.readline()
            if not l or l == b"\r\n":
                break
            # print(l)
            
            # 检查 Transfer-Encoding 是否为 chunked，如果是则抛出异常
            if l.startswith(b"Transfer-Encoding:"):
                if b"chunked" in l:
                    raise ValueError("Unsupported " + l)
                    
            # 检查是否有重定向，如果是则抛出异常
            elif l.startswith(b"Location:"):
                raise NotImplementedError("Redirects not yet supported")
    except OSError:
        # 如果发生错误，则关闭套接字并抛出异常
        s.close()
        raise
        
    # 返回已连接的套接字
    return s
