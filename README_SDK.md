# TTS Edge SDK

这是一个基于Edge TTS的文字转语音SDK，提供了简单易用的API，可以轻松地将文本转换为语音。

## 特性

- 支持多种语音和语言
- 提供同步和异步API
- 可调整语速、音量和音调
- 支持输出为音频数据或Base64编码
- 可直接保存到文件
- 内置日志记录
- 支持长文本分段处理

## 安装

```bash
pip install tts-edge-sdk
```

## 快速开始

### 基本用法

最简单的用法是使用快速函数：

```python
from tts_edge_sdk import text_to_speech

# 转换文本为语音并获取音频数据
audio_data = text_to_speech("你好，这是一个测试。")

# 保存到文件
with open("output.mp3", "wb") as f:
    f.write(audio_data)
```

### 使用同步客户端

```python
from tts_edge_sdk import SyncTTSClient

# 创建客户端
client = SyncTTSClient()

# 获取可用语音列表
voices = client.get_voices()
print(f"找到 {len(voices)} 个可用语音")

# 直接保存到文件
client.save_to_file("这是一个测试。", "output.mp3")

# 自定义语音和参数
client.save_to_file(
    "这是一个自定义参数的测试。", 
    "custom.mp3",
    voice="zh-CN-YunxiNeural",  # 男声
    rate="+10%",                # 语速快10%
    volume="+20%",              # 音量大20%
    pitch="-5%"                 # 音调低5%
)
```

### 使用异步API

```python
import asyncio
from tts_edge_sdk import TTSClient

async def main():
    # 创建异步客户端
    client = TTSClient()
    
    # 获取可用语音
    voices = await client.get_voices()
    
    # 转换文本为语音
    audio_data = await client.text_to_speech("这是一个异步API测试。")
    
    # 保存到文件
    with open("async_output.mp3", "wb") as f:
        f.write(audio_data)
    
    # 或者直接保存
    await client.save_to_file("直接保存到文件。", "direct_save.mp3")
    
    # 获取Base64编码的音频
    base64_audio = await client.text_to_speech_base64("这将返回Base64编码的音频数据。")
    # 现在可以将base64_audio发送到前端播放

# 运行异步函数
asyncio.run(main())
```

## 长文本处理

对于较长的文本，SDK提供了分段处理功能，可以显著提高处理速度：

```python
from tts_edge_sdk import SyncTTSClient

client = SyncTTSClient()

# 长文本示例
long_text = """
这是一段很长的文本...
"""

# 启用分段处理
client.save_to_file(
    long_text,
    "long_text.mp3",
    enable_chunking=True,  # 启用分段处理
    chunk_size=1000,       # 每段1000字符
    concurrency=3          # 同时处理3段
)
```

## 可用参数

- `text`: 要转换的文本
- `voice`: 语音名称，例如 `zh-CN-XiaoxiaoNeural`（默认中文女声）
- `rate`: 语速，范围 `-50%` 到 `+50%`
- `volume`: 音量，范围 `-50%` 到 `+50%`
- `pitch`: 音调，范围 `-50%` 到 `+50%`
- `enable_chunking`: 是否启用分段处理（默认False）
- `chunk_size`: 每段文本字符数（默认1000）
- `concurrency`: 并发处理段数（默认3）

## 日志记录

SDK内置了日志记录功能，您可以通过配置Python的日志系统来调整日志级别：

```python
import logging
logging.getLogger("tts-edge-sdk").setLevel(logging.DEBUG)
``` 