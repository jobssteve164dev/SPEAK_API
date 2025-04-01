# TTS SDK 使用指南

这是一个基于Edge TTS的文字转语音SDK，提供了简单易用的API，可以轻松地将文本转换为语音。

## 特性

- 支持多种语音和语言
- 提供同步和异步API
- 可调整语速、音量和音调
- 支持输出为音频数据或Base64编码
- 可直接保存到文件
- 内置日志记录

## 安装

首先安装必要的依赖：

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

## 进阶用法

### 批量处理

```python
from tts_edge_sdk import SyncTTSClient

client = SyncTTSClient()

# 批量处理多段文本
sentences = [
    "第一段文本。",
    "第二段文本。",
    "第三段文本。"
]

for i, sentence in enumerate(sentences):
    client.save_to_file(sentence, f"output_{i+1}.mp3")
```

### 异步并行处理

```python
import asyncio
from tts_edge_sdk import TTSClient

async def process_text(client, text, output_file, voice=None):
    await client.save_to_file(text, output_file, voice)
    print(f"已生成 {output_file}")

async def main():
    client = TTSClient()
    
    # 创建多个任务并行处理
    tasks = []
    texts = ["第一段", "第二段", "第三段", "第四段", "第五段"]
    
    for i, text in enumerate(texts):
        task = asyncio.create_task(
            process_text(client, text, f"parallel_{i+1}.mp3")
        )
        tasks.append(task)
    
    # 等待所有任务完成
    await asyncio.gather(*tasks)
    print("所有任务已完成")

asyncio.run(main())
```

## 可用参数

- `text`: 要转换的文本
- `voice`: 语音名称，例如 `zh-CN-XiaoxiaoNeural`（默认中文女声）
- `rate`: 语速，范围 `-50%` 到 `+50%`
- `volume`: 音量，范围 `-50%` 到 `+50%`
- `pitch`: 音调，范围 `-50%` 到 `+50%`

## 示例代码

查看 `examples` 目录中的示例代码，了解更多使用方法：

- `basic_usage.py`: 基本使用示例
- `advanced_usage.py`: 高级使用示例

## 日志记录

SDK内置了日志记录功能，您可以通过配置Python的日志系统来调整日志级别：

```python
import logging
logging.getLogger("tts-edge-sdk").setLevel(logging.DEBUG)
``` 