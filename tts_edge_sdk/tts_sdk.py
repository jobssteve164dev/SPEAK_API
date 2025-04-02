import edge_tts
import asyncio
import base64
from typing import Optional, Dict, List, Any, Union, Callable
import logging
from pydub import AudioSegment
import io
import time
import tempfile
import os
import sys
import subprocess

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tts-sdk")

# 添加事件通知系统
class EventEmitter:
    """简单的事件发射器，用于通知外部监听器SDK内部事件"""
    
    def __init__(self):
        self._listeners = {}
    
    def on(self, event: str, callback: Callable) -> None:
        """注册事件监听器"""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)
    
    def emit(self, event: str, *args, **kwargs) -> None:
        """触发事件，并调用所有监听该事件的回调函数"""
        if event in self._listeners:
            for callback in self._listeners[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"事件回调执行错误: {str(e)}")

# 创建全局事件发射器
events = EventEmitter()

# 检查pydub和ffmpeg是否可用
PYDUB_AVAILABLE = False
FFMPEG_AVAILABLE = False

try:
    import pydub
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
    
    # 检查ffmpeg是否可用
    try:
        subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=False,
            timeout=2
        )
        FFMPEG_AVAILABLE = True
    except (FileNotFoundError, subprocess.SubprocessError, subprocess.TimeoutExpired):
        logger.warning("警告: 未找到ffmpeg，部分音频处理功能将受限")
        logger.warning("如需完整功能，请安装ffmpeg: https://ffmpeg.org/download.html")
except ImportError:
    logger.warning("警告: 未安装pydub，无法使用高级音频处理功能")
    logger.warning("如需完整功能，请安装pydub: pip install pydub")

class TTSClient:
    """文字转语音SDK客户端"""
    
    def __init__(self, default_voice: str = "zh-CN-XiaoxiaoNeural"):
        """
        初始化TTS客户端
        
        Args:
            default_voice: 默认语音，如不指定则使用中文女声
        """
        self.default_voice = default_voice
        logger.info(f"TTS客户端初始化，默认语音: {default_voice}")
    
    async def get_voices(self) -> List[Dict[str, Any]]:
        """
        获取所有可用的语音列表
        
        Returns:
            List[Dict[str, Any]]: 语音列表
        """
        try:
            voices = await edge_tts.list_voices()
            logger.info(f"获取到 {len(voices)} 个可用语音")
            return voices
        except Exception as e:
            logger.error(f"获取语音列表失败: {str(e)}")
            raise e
    
    async def _process_text_chunk(
        self,
        text: str,
        voice: str,
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz"
    ) -> bytes:
        """处理单个文本段"""
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch
        )
        # 使用临时文件来处理音频数据
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            await communicate.save(temp_file.name)
            with open(temp_file.name, 'rb') as f:
                audio_data = f.read()
            os.unlink(temp_file.name)  # 删除临时文件
            return audio_data
    
    async def _process_long_text(
        self,
        text: str,
        voice: str,
        rate: str,
        volume: str,
        pitch: str,
        chunk_size: int = 500,
        concurrency: int = 3
    ) -> bytes:
        """分段并行处理长文本"""
        # 按标点符号分段
        chunks = []
        current_chunk = ""
        
        # 常见中文和英文标点符号
        sentence_end_marks = ["。", "！", "？", "；", ".", "!", "?", ";"]
        
        # 确保chunk_size不为0
        chunk_size = max(chunk_size, 500)
        
        # 如果文本长度小于chunk_size的1.5倍，则不分段
        if len(text) < chunk_size * 1.5:
            chunks = [text]
        else:
            for char in text:
                current_chunk += char
                
                # 如果遇到句末标点并且当前段长度超过最小段落大小，则考虑是否分段
                if char in sentence_end_marks and len(current_chunk) >= min(200, chunk_size//5):
                    # 如果当前段落长度超过了chunk_size或接近chunk_size的80%，则分段
                    if len(current_chunk) >= chunk_size * 0.8:
                        chunks.append(current_chunk)
                        current_chunk = ""
            
            # 添加最后一段
            if current_chunk:
                chunks.append(current_chunk)
        
        logger.info(f"长文本被分为 {len(chunks)} 段进行处理，平均段长: {sum(len(c) for c in chunks)/max(1, len(chunks)):.1f} 字符")
        logger.info(f"各段长度: {[len(c) for c in chunks]}")
        
        # 创建一个信号量来限制并发任务数
        semaphore = asyncio.Semaphore(concurrency)
        
        async def process_with_semaphore(chunk: str) -> bytes:
            async with semaphore:
                logger.info(f"开始处理段落: 长度={len(chunk)}字符, 起始={chunk[:20]}...")
                chunk_data = await self._process_text_chunk(chunk, voice, rate, volume, pitch)
                logger.info(f"段落处理完成: 音频大小={len(chunk_data)}字节")
                return chunk_data
        
        # 并行处理所有文本段
        start_time = time.time()
        tasks = [process_with_semaphore(chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time
        
        logger.info(f"并行处理完成: {len(chunks)} 段文本, 总时间: {elapsed:.2f}秒, 平均每段: {elapsed/max(1, len(chunks)):.2f}秒")
        logger.info(f"各段音频大小: {[len(r) for r in results]}字节")
        
        # 使用直接拼接作为后备方案
        all_audio_data = b''
        
        # 使用pydub正确合并音频片段
        if len(results) > 1:
            # 发出合并开始信号
            events.emit("merge_start", len(results))
            merge_start_time = time.time()
            
            # 检查是否有任何空结果
            if any(not result for result in results):
                logger.warning(f"警告：检测到{sum(1 for r in results if not r)}个空音频段")
            
            valid_results = [r for r in results if r and len(r) > 0]
            if not valid_results:
                logger.error("错误：所有音频段都为空，无法处理")
                events.emit("merge_end", 0, False)  # 发出合并结束信号（失败）
                return b''
                
            logger.info(f"有效音频段数量: {len(valid_results)}/{len(results)}")
            
            # 如果pydub和ffmpeg都可用，使用专业的音频处理
            if PYDUB_AVAILABLE and FFMPEG_AVAILABLE:
                try:
                    # 为调试添加一些输出
                    logger.info("使用pydub+ffmpeg合并音频片段...")
                    
                    segments = []
                    # 处理每个非空音频数据
                    for i, audio_data in enumerate(valid_results):
                        try:
                            segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
                            segments.append(segment)
                            logger.info(f"成功加载音频段 {i+1}/{len(valid_results)}: 长度={len(segment)}ms")
                        except Exception as e:
                            logger.error(f"加载音频段 {i+1} 失败: {str(e)}")
                    
                    if segments:
                        # 合并所有音频段
                        logger.info(f"开始合并 {len(segments)} 个音频段...")
                        combined = segments[0]
                        
                        for i, segment in enumerate(segments[1:], 1):
                            try:
                                combined = combined + segment
                                logger.info(f"成功合并音频段 {i+1}/{len(segments)}")
                            except Exception as e:
                                logger.error(f"合并音频段 {i+1} 失败: {str(e)}")
                        
                        # 导出为MP3
                        buffer = io.BytesIO()
                        logger.info("导出合并后的MP3...")
                        combined.export(buffer, format="mp3", bitrate="128k")
                        all_audio_data = buffer.getvalue()
                        
                        # 计算合并耗时并发出合并结束信号
                        merge_time = time.time() - merge_start_time
                        events.emit("merge_end", merge_time, True, len(all_audio_data))
                        
                        logger.info(f"音频合并成功: 总大小={len(all_audio_data)}字节, 估计时长={len(combined)/1000:.2f}秒, 合并耗时={merge_time:.2f}秒")
                        return all_audio_data
                    else:
                        logger.error("没有有效的音频段可以合并")
                        events.emit("merge_end", time.time() - merge_start_time, False)
                except Exception as e:
                    logger.error(f"音频合并过程中发生错误: {str(e)}", exc_info=True)
                    events.emit("merge_end", time.time() - merge_start_time, False)
            
            # 如果无法使用pydub+ffmpeg，使用直接字节拼接
            logger.info("使用MP3直接字节拼接...")
            
            # 专业合并不可用时的直接字节拼接方法
            # 注意：MP3是基于帧的格式，可以直接拼接但可能在拼接处有轻微爆音
            try:
                # 为了提高字节拼接的可靠性，我们尝试处理MP3帧
                # 一个基本的MP3文件包含文件头和帧，我们保留第一个文件的头
                # 后续文件只使用其帧部分（跳过前几百个字节的文件头信息）
                all_audio_data = valid_results[0]  # 完整使用第一个文件（包含文件头）
                
                # 对后续文件跳过大约200字节的文件头（简化处理，可能不总是准确）
                for i, audio_data in enumerate(valid_results[1:], 1):
                    # 我们跳过250字节以避开大多数MP3文件头信息
                    # 这是一个简单但不完美的解决方案
                    if len(audio_data) > 250:
                        all_audio_data += audio_data[250:]
                        logger.info(f"拼接音频段 {i+1}/{len(valid_results)}")
                    else:
                        logger.warning(f"音频段 {i+1} 太小，无法安全拼接")
                
                # 计算合并耗时并发出合并结束信号
                merge_time = time.time() - merge_start_time
                events.emit("merge_end", merge_time, True, len(all_audio_data))
                
                logger.info(f"字节拼接完成: 总大小={len(all_audio_data)}字节, 合并耗时={merge_time:.2f}秒")
                return all_audio_data
            except Exception as e:
                logger.error(f"拼接过程中出错: {str(e)}")
                events.emit("merge_end", time.time() - merge_start_time, False)
                # 如果连基本拼接都失败，至少返回第一个有效结果
                return valid_results[0]
        
        elif results and results[0]:
            # 只有一个有效结果
            logger.info(f"只有一个音频段，不需要合并: 大小={len(results[0])}字节")
            return results[0]
        else:
            # 没有有效结果
            logger.error("没有生成任何有效的音频数据")
            return b''
    
    async def text_to_speech(
        self, 
        text: str, 
        voice: Optional[str] = None,
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz",
        enable_chunking: bool = False,
        chunk_size: int = 500,
        concurrency: int = 3
    ) -> bytes:
        """
        将文本转换为语音
        
        Args:
            text: 要转换的文本
            voice: 语音名称，如不指定则使用默认语音
            rate: 语速，范围 -50% 到 +50%
            volume: 音量，范围 -50% 到 +50%
            pitch: 音调，范围 -50% 到 +50%
            enable_chunking: 是否启用分段处理
            chunk_size: 每段文本字符数
            concurrency: 并发处理段数
            
        Returns:
            bytes: 音频数据
        """
        try:
            selected_voice = voice or self.default_voice
            logger.info(f"处理TTS请求: 文本长度 {len(text)} 字符, 语音 {selected_voice}")
            
            # 根据文本长度和用户选项决定是否使用分段处理
            if enable_chunking:
                # 文本较长或显式启用分段
                logger.info(f"使用分段并行处理: chunk_size={chunk_size}, concurrency={concurrency}")
                audio_data = await self._process_long_text(
                    text=text,
                    voice=selected_voice,
                    rate=rate,
                    volume=volume,
                    pitch=pitch,
                    chunk_size=chunk_size,
                    concurrency=concurrency
                )
            else:
                # 使用普通处理方式
                logger.info("使用普通处理方式")
                audio_data = await self._process_text_chunk(
                    text=text,
                    voice=selected_voice,
                    rate=rate,
                    volume=volume,
                    pitch=pitch
                )
            
            logger.info(f"TTS请求处理成功: 生成音频大小 {len(audio_data)} 字节")
            return audio_data
        except Exception as e:
            logger.error(f"TTS请求处理失败: {str(e)}")
            raise e
    
    async def text_to_speech_base64(
        self, 
        text: str, 
        voice: Optional[str] = None,
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz",
        enable_chunking: bool = False,
        chunk_size: int = 500,
        concurrency: int = 3
    ) -> str:
        """
        将文本转换为base64编码的语音
        
        Args:
            text: 要转换的文本
            voice: 语音名称，如不指定则使用默认语音
            rate: 语速，范围 -50% 到 +50%
            volume: 音量，范围 -50% 到 +50%
            pitch: 音调，范围 -50% 到 +50%
            enable_chunking: 是否启用分段处理
            chunk_size: 每段文本字符数
            concurrency: 并发处理段数
            
        Returns:
            str: base64编码的音频数据
        """
        audio_data = await self.text_to_speech(
            text, voice, rate, volume, pitch,
            enable_chunking, chunk_size, concurrency
        )
        return base64.b64encode(audio_data).decode()
    
    async def save_to_file(
        self, 
        text: str, 
        output_file: str,
        voice: Optional[str] = None,
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz",
        enable_chunking: bool = False,
        chunk_size: int = 500,
        concurrency: int = 3
    ) -> None:
        """
        将文本转换为语音并保存到文件
        
        Args:
            text: 要转换的文本
            output_file: 输出文件路径
            voice: 语音名称，如不指定则使用默认语音
            rate: 语速，范围 -50% 到 +50%
            volume: 音量，范围 -50% 到 +50%
            pitch: 音调，范围 -50% 到 +50%
            enable_chunking: 是否启用分段处理
            chunk_size: 每段文本字符数
            concurrency: 并发处理段数
        """
        try:
            audio_data = await self.text_to_speech(
                text, voice, rate, volume, pitch,
                enable_chunking, chunk_size, concurrency
            )
            with open(output_file, "wb") as f:
                f.write(audio_data)
            logger.info(f"音频已保存到文件: {output_file}")
        except Exception as e:
            logger.error(f"保存音频到文件失败: {str(e)}")
            raise e

# 同步接口封装
class SyncTTSClient:
    """同步的文字转语音SDK客户端"""
    
    def __init__(self, default_voice: str = "zh-CN-XiaoxiaoNeural"):
        """
        初始化同步TTS客户端
        
        Args:
            default_voice: 默认语音，如不指定则使用中文女声
        """
        self._async_client = TTSClient(default_voice)
    
    def get_voices(self) -> List[Dict[str, Any]]:
        """获取所有可用的语音列表"""
        return asyncio.run(self._async_client.get_voices())
    
    def text_to_speech(
        self, 
        text: str, 
        voice: Optional[str] = None,
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz",
        enable_chunking: bool = False,
        chunk_size: int = 500,
        concurrency: int = 3
    ) -> bytes:
        """将文本转换为语音"""
        return asyncio.run(self._async_client.text_to_speech(
            text, voice, rate, volume, pitch,
            enable_chunking, chunk_size, concurrency
        ))
    
    def text_to_speech_base64(
        self, 
        text: str, 
        voice: Optional[str] = None,
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz",
        enable_chunking: bool = False,
        chunk_size: int = 500,
        concurrency: int = 3
    ) -> str:
        """将文本转换为base64编码的语音"""
        return asyncio.run(self._async_client.text_to_speech_base64(
            text, voice, rate, volume, pitch,
            enable_chunking, chunk_size, concurrency
        ))
    
    def save_to_file(
        self, 
        text: str, 
        output_file: str,
        voice: Optional[str] = None,
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz",
        enable_chunking: bool = False,
        chunk_size: int = 500,
        concurrency: int = 3
    ) -> None:
        """将文本转换为语音并保存到文件"""
        asyncio.run(self._async_client.save_to_file(
            text, output_file, voice, rate, volume, pitch,
            enable_chunking, chunk_size, concurrency
        ))

# 快速使用的函数
async def async_text_to_speech(
    text: str, 
    voice: str = "zh-CN-XiaoxiaoNeural",
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
    enable_chunking: bool = False,
    chunk_size: int = 500,
    concurrency: int = 3
) -> bytes:
    """异步快速将文本转换为语音"""
    client = TTSClient(voice)
    return await client.text_to_speech(
        text, voice, rate, volume, pitch,
        enable_chunking, chunk_size, concurrency
    )

def text_to_speech(
    text: str, 
    voice: str = "zh-CN-XiaoxiaoNeural",
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
    enable_chunking: bool = False,
    chunk_size: int = 500,
    concurrency: int = 3
) -> bytes:
    """同步快速将文本转换为语音"""
    return asyncio.run(async_text_to_speech(
        text, voice, rate, volume, pitch,
        enable_chunking, chunk_size, concurrency
    ))

# 添加一些辅助函数，允许外部代码监听事件
def on_merge_start(callback: Callable) -> None:
    """注册音频合并开始事件监听器"""
    events.on("merge_start", callback)

def on_merge_end(callback: Callable) -> None:
    """注册音频合并结束事件监听器"""
    events.on("merge_end", callback) 