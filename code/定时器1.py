from machine import Timer
import time

# 创建一个软件定时器实例，-1 表示使用软件定时器
tim = Timer(-1)

# 配置定时器，单次模式（ONE_SHOT），定时100毫秒，回调函数打印数字1
tim.init(period=100, mode=Timer.ONE_SHOT, callback=lambda t: print("Timer Callback: 1"))

# 再次配置定时器，这次为周期模式（PERIODIC），每隔1000毫秒（1秒）打印数字2
tim.init(period=1000, mode=Timer.PERIODIC, callback=lambda t: print("Timer Callback: 2"))

# 延时5.1秒，让定时有时间执行
time.sleep(5.1)

# 当不再需要定时器时，可以停用它
tim.deinit()