#!/usr/bin/env python
"""
高级使用示例 - 展示TTS SDK的更多高级功能
"""

import sys
import os
import asyncio

# 添加父目录到路径，使示例代码可以导入SDK
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tts_edge_sdk import TTSClient

async def async_example():
    """异步API使用示例"""
    print("======= 异步API示例 =======")
    
    # 创建异步客户端
    client = TTSClient()
    
    # 获取所有语音
    voices = await client.get_voices()
    
    # 获取一些不同语言的语音
    languages = {}
    for voice in voices:
        locale = voice["Locale"]
        if locale not in languages and len(languages) < 5:
            languages[locale] = voice["ShortName"]
    
    print("使用不同语言生成同一段文本:")
    
    # 创建异步任务
    tasks = []
    for locale, voice in languages.items():
        text = "这是一个多语种测试示例。"
        if locale.startswith("en"):
            text = "This is a multilingual test example."
        elif locale.startswith("ja"):
            text = "これは多言語テストの例です。"
        elif locale.startswith("fr"):
            text = "Ceci est un exemple de test multilingue."
        elif locale.startswith("de"):
            text = "Dies ist ein mehrsprachiges Testbeispiel."
            
        output_file = f"output_{locale}.mp3"
        task = asyncio.create_task(save_audio(client, text, output_file, voice))
        tasks.append((locale, task))
    
    # 等待所有任务完成
    for locale, task in tasks:
        await task
        print(f"已生成 {locale} 语音文件")

async def save_audio(client, text, output_file, voice):
    """保存音频到文件"""
    await client.save_to_file(text, output_file, voice)

async def long_text_example():
    """长文本处理示例"""
    print("\n======= 长文本处理示例 =======")
    
    client = TTSClient()
    
    # 长文本示例
    long_text = """
    文字转语音技术是人工智能领域的重要应用之一，它能够将书面文字转换为自然流畅的语音输出。
    这项技术在提高信息无障碍获取、辅助视力障碍人士、增强人机交互体验等方面发挥着重要作用。
    现代文字转语音系统通常基于深度学习模型，能够生成具有自然语调、情感表达和韵律变化的语音。
    系统可以通过调整语速、音调和音量等参数，实现个性化的语音合成效果。
    随着技术的不断发展，文字转语音系统的应用场景也在不断扩展，如智能客服、导航系统、有声读物等众多领域。
    """
    
    # 清理文本
    long_text = long_text.strip()
    
    # 保存到文件
    await client.save_to_file(long_text, "output_long_text.mp3")
    print("已生成长文本语音文件")

async def streaming_example():
    """模拟流式处理示例"""
    print("\n======= 流式处理模拟示例 =======")
    
    client = TTSClient()
    
    # 分段的文本
    sentences = [
        "这是第一段话，模拟实时输入的文本。",
        "当用户继续说话时，我们可以持续处理新的文本。",
        "这种方式非常适合语音对话或实时字幕等应用场景。",
        "通过分段处理，我们可以实现更快的响应速度。",
        "最后，流式处理可以提供更好的用户体验。"
    ]
    
    print("模拟流式处理中...")
    for i, sentence in enumerate(sentences):
        # 生成语音
        audio_data = await client.text_to_speech(sentence)
        
        # 在真实应用中，这里可以直接播放音频或发送到客户端
        # 这里我们只是保存到文件作为示例
        with open(f"stream_part_{i+1}.mp3", "wb") as f:
            f.write(audio_data)
        
        print(f"已处理第 {i+1} 段文本: {sentence[:20]}...")
        
        # 模拟延迟
        await asyncio.sleep(0.5)
    
    print("流式处理完成")

async def main():
    """运行所有异步示例"""
    await async_example()
    await long_text_example()
    await streaming_example()

if __name__ == "__main__":
    # 运行异步示例
    asyncio.run(main()) 