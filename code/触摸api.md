4 获取触摸点程序
API

enumerate() 是 Python 内置的一个函数，用于遍历可迭代对象（如列表、元组、字符串等）时，同时获取元素的索引和值。它返回的是一个枚举对象，可以在遍历时同时得到每个元素的索引和该元素的值。用这个可以简化我们的代码，避免使用手动创建的计数变量。

基本语法：


enumerate(iterable, start=0)
1
iterable：任何可迭代的对象，如列表、元组、字符串等。
start：指定索引的起始值，默认为 0。可以设置为其他值，指定索引从该值开始。
enumerate() 返回一个枚举对象，这个对象可以被 for 循环遍历。每次循环中，enumerate() 返回一个元组，元组的第一个元素是索引，第二个元素是迭代对象中的元素。


fruits = ["苹果", "香蕉", "橙子"]

for index, fruit in enumerate(fruits):
    print(f"索引: {index}, 值: {fruit}")

输出：


索引: 0, 值: 苹果
索引: 1, 值: 香蕉
索引: 2, 值: 橙子

在这个示例中，enumerate(fruits) 会返回 (0, "苹果")， (1, "香蕉") 和 (2, "橙子") 这样的元组。

下面这段程序的主要功能是读取触摸屏的触摸点数据，并打印出触摸点的坐标，最多打印5个坐标点（我们的3.1寸屏幕的触摸硬件上就只支持5个触摸点）。

```python
# 立创·庐山派-K230-CanMV开发板资料与相关扩展板软硬件资料官网全部开源
# 开发板官网：www.lckfb.com
# 技术支持常驻论坛，任何技术问题欢迎随时交流学习
# 立创论坛：www.jlc-bbs.com/lckfb
# 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
# 不靠卖板赚钱，以培养中国工程师为己任

import time
from machine import TOUCH

# 实例化 TOUCH 设备 0
tp = TOUCH(0)

while True:
    # 获取最多 5 个触摸点数据，默认为1.
    p = tp.read(5)

    # 如果返回的 p 为空元组，表示没有触摸
    if p != ():
        print("触摸数据：")
        for idx, point in enumerate(p, start=1):  # 对触摸点进行编号，从 1 开始
            print(f"触摸点 {idx}: X = {point.x}, Y = {point.y}")

    time.sleep(0.01)  # 等待 10 毫秒再读取
```

