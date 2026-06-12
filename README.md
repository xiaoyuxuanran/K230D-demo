# 使用方法

1. 将**lckfb_k230\code\当前烧录程序**下所有 `.py` 文件烧录到 K230D 的 `/sdcard/` 目录
2. 将**\code\当前素材文件**内容拷贝放入 `/data/` 路径
3. 放入至少一个 `.wav` 音乐文件到 `/data/code/music/`
4. 上电自动运行 `main.py` → 启动画面 → 主界面
5. 点击图标进入各功能，点击退出/返回按钮回主界面

### SD卡 `/data/` 目录下的资源文件

```
/data/
├── code/
│   ├── photo/
│   │   └── img_top.jpg          # 主界面背景图（800×480）
│   ├── music/
│   │   └── *.wav                # WAV音乐文件
│   ├── picture/
│   │   ├── photo_*.jpg          # 相机拍摄的照片
│   │   └── painting_*.jpg       # 画板保存的图片
│   ├── audio/
│   │   └── rec_*.wav            # 录音机录制的音频
│   ├── doc/
│   │   ├── *.txt                # 小说TXT文件
│   │   └── doc_read.txt         # 阅读进度（自动生成）
│   ├── video/
│   │   └── new.mp4              # 测试视频
│   ├── setup/
│   │   ├── setup.png            # 启动画面图片
│   │   └── setup.wav            # 启动画面音频
│   └── font/                    # 字体文件（可选）
```
### SD卡 `/sdcard/` 目录下的代码文件放在根目录下即可

| 文件 | 功能 | 必需 |
|---|---|---|
| `main.py` | 程序入口 | ✓ |
| `setup.py` | 开机启动画面 | ✓ |
| `test_touch.py` | 主界面 + 图标路由 | ✓ |
| `music_player_copy.py` | 音乐播放器 | ✓ |
| `takephoto.py` | 相机拍照 | ✓ |
| `audiowr.py` | 录音机 | ✓ |
| `picWarehouse.py` | 相册 | ✓ |
| `painting.py` | 画板 | ✓ |
| `mywificon.py` | WiFi配网 | ✓ |
| `weather_my.py` | 天气 | ✓ |
| `clock_time.py` | NTP时间+显示 | ✓ |
| `stby.py` | 待机屏保 | ✓ |
| `sys_setting.py` | 系统设置 | ✓ |
| `novel_reader.py` | 小说阅读器 | ✓ |
| `ntptime.py` | NTP时间协议 | ✓ |
| `urequest.py` | HTTP请求 | ✓ |
| `old_music.py` | 旧版播放器（未启用） | ✗ |
