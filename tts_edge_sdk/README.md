# TTS Edge SDK

基于Edge TTS的易用文字转语音SDK，提供简单的API将文本转换为高质量语音。

## 特性

- 支持多种语音和语言
- 提供同步和异步API接口
- 支持调整语速、音量和音调
- 音频可直接保存到文件或以Base64格式返回
- 内置日志记录
- 高性能，易于集成

## 安装

```bash
# 通过pip安装
pip install tts-edge-sdk

# 或者直接从源码安装
git clone https://github.com/yourusername/tts-edge-sdk.git
cd tts-edge-sdk
pip install -e .
```

## 快速上手

```python
# 最简单的用法
from tts_edge_sdk import text_to_speech

# 转换文本为语音
audio_data = text_to_speech("你好，这是一个示例文本。")
with open("output.mp3", "wb") as f:
    f.write(audio_data)
```

## 示例代码

查看 `examples` 目录中的示例代码：

- `basic_usage.py`: 基本使用示例
- `advanced_usage.py`: 高级特性示例

## 文档

详细的API文档请参阅 `README_SDK.md`。

## 许可证

MIT License 