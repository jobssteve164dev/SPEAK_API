# TTS API 文档

## 基础信息

- 基础URL: `http://localhost:8000`
- 所有请求和响应均使用 JSON 格式
- 所有时间戳均为 UTC 时间

## API 端点

### 1. 文字转语音

将文本转换为语音。

**请求**
```http
POST /tts
Content-Type: application/json
```

**请求参数**
```json
{
    "text": "要转换的文本",
    "voice": "zh-CN-XiaoxiaoNeural",  // 可选，默认中文女声
    "rate": "+0%",                     // 可选，语速 (-50% 到 +50%)
    "volume": "+0%",                   // 可选，音量 (-50% 到 +50%)
    "pitch": "+0%"                     // 可选，音调 (-50% 到 +50%)
}
```

**响应**
```json
{
    "audio": "base64编码的音频数据"
}
```

### 2. 获取可用语音列表

获取所有可用的语音列表。

**请求**
```http
GET /voices
```

**响应**
```json
{
    "voices": [
        {
            "ShortName": "zh-CN-XiaoxiaoNeural",
            "LocalName": "晓晓",
            "Gender": "Female",
            "Locale": "zh-CN"
        },
        // ... 更多语音
    ]
}
```

## 示例代码

### Python
```python
import requests

# 文字转语音
response = requests.post(
    "http://localhost:8000/tts",
    json={
        "text": "你好，这是一个测试",
        "voice": "zh-CN-XiaoxiaoNeural"
    }
)

# 获取语音列表
voices = requests.get("http://localhost:8000/voices")
```

### curl
```bash
# 文字转语音
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，这是一个测试",
    "voice": "zh-CN-XiaoxiaoNeural"
  }'

# 获取语音列表
curl http://localhost:8000/voices
```

## 错误处理

所有错误响应都遵循以下格式：

```json
{
    "detail": "错误信息描述"
}
```

常见错误状态码：
- 400: 请求参数错误
- 401: 未授权
- 404: 资源不存在
- 500: 服务器内部错误

## 注意事项

1. 音频数据以 base64 编码返回，需要解码后才能播放
2. 建议在生产环境中使用 HTTPS
3. 所有时间戳均为 UTC 时间
4. 语音参数（rate、volume、pitch）的范围是 -50% 到 +50% 