#!/usr/bin/env python
"""
基本使用示例 - 展示TTS SDK的基本功能
"""

import sys
import os

# 添加父目录到路径，使示例代码可以导入SDK
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tts_edge_sdk import SyncTTSClient, text_to_speech

def basic_example():
    """基本使用示例"""
    print("======= 基本示例 - 快速转换 =======")
    # 使用快速函数
    audio_data = text_to_speech("这是一个简单的语音合成测试。使用快速函数进行转换。")
    # 保存到文件
    with open("output_quick.mp3", "wb") as f:
        f.write(audio_data)
    print(f"已保存到 output_quick.mp3，大小: {len(audio_data)} 字节")

def client_example():
    """客户端使用示例"""
    print("\n======= 客户端示例 - 更多功能 =======")
    # 创建客户端
    client = SyncTTSClient()
    
    # 获取可用语音
    voices = client.get_voices()
    print(f"找到 {len(voices)} 个可用语音")
    
    # 打印前5个中文语音
    zh_voices = [v for v in voices if v["Locale"] == "zh-CN"]
    print("中文语音示例:")
    for i, voice in enumerate(zh_voices[:5]):
        print(f"  {i+1}. {voice['LocalName']} ({voice['ShortName']})")
    
    # 使用不同语音生成
    text = "这是使用客户端API生成的语音示例，可以调整语速和音调。"
    
    # 使用默认设置
    client.save_to_file(text, "output_default.mp3")
    print("已保存默认语音到 output_default.mp3")
    
    # 使用不同语音、语速和音调
    if zh_voices:
        male_voice = next((v["ShortName"] for v in zh_voices if v["Gender"] == "Male"), None)
        if male_voice:
            client.save_to_file(
                text, 
                "output_custom.mp3", 
                voice=male_voice,
                rate="+20%",
                pitch="+10%"
            )
            print(f"已保存自定义语音到 output_custom.mp3 (语音: {male_voice}, 语速: +20%, 音调: +10%)")

def batch_example():
    """批量处理示例"""
    print("\n======= 批量处理示例 =======")
    client = SyncTTSClient()
    
    sentences = [
        "第一句示例文本，用于测试批量转换功能。",
        "第二句示例文本，可以使用不同的语音或参数。",
        "第三句示例文本，展示SDK的易用性。"
    ]
    
    for i, sentence in enumerate(sentences):
        output_file = f"output_batch_{i+1}.mp3"
        client.save_to_file(sentence, output_file)
        print(f"已保存第 {i+1} 个文件到 {output_file}")

if __name__ == "__main__":
    # 运行示例
    basic_example()
    client_example()
    batch_example()
    
    print("\n所有示例已完成，生成的音频文件保存在当前目录") 