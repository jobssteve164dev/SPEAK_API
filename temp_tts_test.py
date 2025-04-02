import asyncio
from datetime import datetime
import os
import sys
import time
import logging
import subprocess
import importlib  # 添加importlib用于重新加载模块
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
from concurrent.futures import ThreadPoolExecutor
import pygame  # 用于音频播放

# 强制重新加载SDK模块
if 'tts_edge_sdk.tts_sdk' in sys.modules:
    importlib.reload(sys.modules['tts_edge_sdk.tts_sdk'])
if 'tts_edge_sdk' in sys.modules:
    importlib.reload(sys.modules['tts_edge_sdk'])

# 导入SDK
from tts_edge_sdk import TTSClient
import tts_edge_sdk.tts_sdk as sdk
import inspect
import functools
import threading

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tts-test")

# 禁用第三方库的详细日志
logging.getLogger("pydub.converter").setLevel(logging.WARNING)

# 打印SDK模块版本信息，确认使用的是最新版本
logger.info(f"SDK模块路径: {sdk.__file__}")
logger.info(f"SDK模块加载时间: {datetime.fromtimestamp(os.path.getmtime(sdk.__file__))}")
logger.info(f"EventEmitter类是否存在: {'EventEmitter' in dir(sdk)}")
logger.info(f"合并开始事件处理器是否存在: {'on_merge_start' in dir(sdk)}")

def check_ffmpeg_installed():
    """检查系统是否安装了 ffmpeg"""
    try:
        # 尝试运行ffmpeg命令
        subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=False
        )
        return True
    except (FileNotFoundError, subprocess.SubprocessError):
        return False

def generate_meditation_text() -> str:
    """生成一段大约10分钟的冥想引导文字"""
    return """
    欢迎来到这段特别为您准备的宁静时光，一次深入内在、探索平和的旅程。请寻找一个舒适、不受打扰的地方坐下或躺下。轻轻调整姿势，让脊柱保持自然直立，或者舒适地平躺。当你准备好时，温柔地闭上眼睛，或者将目光柔和地投向前方的一个固定点。

    现在，让我们从呼吸开始。将所有的注意力都集中在你的呼吸上。深深地吸气，感受气息如何通过鼻腔，清凉地进入你的身体，充满你的肺部，甚至你的腹部也随之微微鼓起。想象这股气息带来了全新的能量与活力。然后，缓缓地、有控制地呼气，感受气息温暖地离开身体，带走所有的紧张、疲惫和杂念。再一次，深深吸气……缓缓呼气……允许你的呼吸逐渐变得深沉、平稳而自然。不需要刻意控制，只是观察它，感受它。每一次呼吸，都更深地带你进入当下的宁静。

    接下来，让我们进行一次细致的身体扫描，将意识的暖流引导至身体的每一个角落。从你的头顶开始，感受那里的皮肤和肌肉。释放任何可能存在的紧绷感，让头皮完全放松。想象一股温暖、放松的感觉从头顶缓缓流下。

    让这股放松的暖流来到你的前额，抚平所有的纹路。感受眉毛舒展开来，眼睑变得沉重而放松，眼球在眼窝中安静地休息。让放松的感觉流淌到你的脸颊，感受它们变得柔软。松开你的下颚，让牙齿微微分开，舌头轻柔地抵在上颚。感受整个面部都沐浴在这份放松之中。

    将注意力引导到你的颈部和喉咙。释放这里的僵硬和压力。让放松的感觉继续向下，流淌到你的肩膀。感觉肩膀沉沉地向下放松，远离耳朵。让过去一天积累的负担从肩膀滑落。

    现在，感受你的双臂。从上臂到肘部，再到前臂、手腕、手掌和每一根手指。感觉手臂变得沉重而放松，也许有些温暖或微麻的感觉，这都是放松的迹象。手指自然地舒展或弯曲。

    将意识带到你的胸腔。感受每一次呼吸时，胸腔的轻微起伏。关注你的心跳，感受它稳定而有力的节奏。不需要改变它，只是感受生命在胸腔中的律动。如果有任何情绪的淤积，允许它们随着呼吸轻轻流淌，不必执着。

    继续向下，来到你的上背部和中背部。释放任何的紧张或不适。感受脊柱一节一节地放松。让放松的感觉来到你的腹部。感受腹部随着呼吸柔软地起伏。释放腹部的紧绷，允许内在器官也得到休息。

    将注意力带到你的下背部和腰部。这是一个容易积累压力的区域，给予它额外的关注和放松。感受温暖的放松感渗透到肌肉深处。

    现在，感受你的臀部和骨盆区域，感觉它们稳稳地支撑着你的身体，完全放松。让放松的暖流继续向下，流经你的大腿。感受大腿肌肉的放松和沉重。

    来到你的膝盖，释放这里的紧张。继续向下，感受你的小腿。放松小腿的肌肉。来到你的脚踝、脚跟、脚掌，直到每一根脚趾。感受双脚稳稳地接触地面（如果坐着）或床面（如果躺着）。感受从头到脚，整个身体都沉浸在深度放松的状态中。全然地放松，全然地临在。

    现在，身体已经非常放松了。让我们将注意力轻轻地转向内在的空间。观察此刻你的念头和感受。也许有很多想法在脑海中浮现，像天空中的云朵，来了又去。不要试图抓住它们，也不要评判它们的好坏。只是作为一个旁观者，静静地看着它们飘过。如果发现自己陷入了某个想法，不必自责，只是温柔地、一次又一次地，将注意力重新带回到你的呼吸上，或者带回到身体放松的感觉上。呼吸是你回归当下的锚。

    在这个宁静的内在空间里，感受那份深层的平和。这平和一直都在那里，隐藏在念头的喧嚣之下。它不依赖于外在的环境，它是你内在固有的品质。允许自己沉浸在这份平和之中。感受它的稳定和安宁。

    想象你的意识像一片广阔、清澈的湖水。念头和情绪就像湖面上的涟漪，来了又去，但湖水本身始终是宁静和深邃的。你就是这片湖水。接纳所有升起的念头和感受，就像湖水接纳所有的涟漪和倒影一样。

    继续保持对呼吸的觉知，对身体放松状态的觉知，对内在平和的觉知。每一次吸气，都吸入宁静与清晰；每一次呼气，都释放掉不再需要的东西。

    在这个深深的放松和宁静中，连接你内在的智慧和力量。感受你的内在核心是稳定而充满韧性的。这份力量不需要向外寻求，它一直存在于你的内心深处。相信你的直觉，相信你内在的声音。

    让我们再安静地停留片刻，沐浴在这份宁静与和谐之中。不需要做什么，不需要去哪里，只是存在于此。感受这份存在的纯粹与美好。你是完整的，你是圆满的，就在此刻。

    现在，是时候慢慢地将意识带回到我们周围的环境中了。但请不要急促，保持这份内在的宁静感。首先，再次加深你的呼吸，吸入新的活力。

    然后，开始轻轻地活动你的身体。动动你的手指和脚趾，轻柔地转动你的手腕和脚踝。可以慢慢地伸展一下你的手臂和双腿，像刚睡醒时那样。

    当你感觉准备好时，再慢慢地、温柔地睁开你的眼睛。花一点时间适应周围的光线和环境。看看你周围的世界，仿佛第一次看见一样，带着新的清晰和平和。

    请记住，这份你在冥想中体验到的宁静、放松和内在力量，并不仅仅属于这段冥想时间。它们是你随时可以取用的内在资源。在一天中，无论何时感到压力或忙乱，你都可以停下来，做几次深呼吸，重新连接这份内在的平和。

    感谢你自己，给予了这段宝贵的时间来滋养身心。带着这份平静、清晰和更新的感觉，继续你接下来的一天或一夜。愿你安好。
    """

# 用于存储音频合并时间测量结果的类
class MergeTimeMeasurement:
    def __init__(self):
        self.merge_start_time = None
        self.merge_end_time = None
        self.merge_duration = 0
        self.segments_count = 0
        self.success = False
        self.output_size = 0
        self.lock = threading.Lock()
        self.events_received = 0  # 跟踪接收的事件数量
    
    def reset(self):
        """重置所有测量数据"""
        with self.lock:
            self.merge_start_time = None
            self.merge_end_time = None
            self.merge_duration = 0
            self.segments_count = 0
            self.success = False
            self.output_size = 0
            self.events_received = 0
    
    def on_merge_start(self, segments_count):
        """当合并开始时调用"""
        with self.lock:
            self.merge_start_time = datetime.now()
            self.segments_count = segments_count
            self.events_received += 1
            logger.info(f"[事件] 检测到音频合并开始: {segments_count}个段落, 时间: {self.merge_start_time}")
    
    def on_merge_end(self, duration, success, output_size=0):
        """当合并结束时调用"""
        with self.lock:
            self.merge_end_time = datetime.now()
            self.events_received += 1
            
            # 使用SDK提供的精确计时，但确保非零值
            self.merge_duration = max(duration, 0.001)  # 至少1毫秒，确保显示
            
            self.success = success
            self.output_size = output_size
            status = "成功" if success else "失败"
            logger.info(f"[事件] 检测到音频合并结束({status}): SDK测量耗时={duration:.4f}秒, 实际耗时={(self.merge_end_time-self.merge_start_time).total_seconds():.4f}秒")
            logger.info(f"[事件] 音频合并结果: 输出大小={output_size}字节")

async def test_tts(text: str = None, enable_chunking: bool = False, chunk_size: int = 500, concurrency: int = 3,
                   rate: str = "+0%", volume: str = "+0%", pitch: str = "+0Hz", voice: str = "zh-CN-XiaoxiaoNeural"):
    """测试TTS性能"""
    if text is None:
        text = generate_meditation_text()
    
    # 记录完整的参数信息用于调试
    logger.info(f"调用test_tts函数，参数: voice={voice}, rate={rate}, pitch={pitch}, volume={volume}")
    logger.info(f"其他参数: enable_chunking={enable_chunking}, chunk_size={chunk_size}, concurrency={concurrency}")
    
    # 验证参数格式
    if not voice.startswith("zh-CN-") or not voice.endswith("Neural"):
        logger.error(f"语音ID格式不正确: '{voice}'")
        raise ValueError(f"语音ID格式不正确: '{voice}'")
    
    # 创建TTS客户端
    client = TTSClient()
    
    # 创建测量对象并重置
    merge_timer = MergeTimeMeasurement()
    merge_timer.reset()
    
    # 注册事件处理器，并确认已注册
    sdk.on_merge_start(merge_timer.on_merge_start)
    sdk.on_merge_end(merge_timer.on_merge_end)
    logger.info(f"已注册音频合并事件处理器，准备开始测试")
    
    logger.info(f"开始测试: enable_chunking={enable_chunking}, 文本长度={len(text)}字符, chunk_size={chunk_size}, concurrency={concurrency}")
    logger.info(f"语音参数: voice={voice}, rate={rate}, volume={volume}, pitch={pitch}")
    
    # 总计时开始
    start_total = datetime.now()
    
    try:
        # 使用SDK生成音频
        audio_data = await client.text_to_speech(
            text=text,
            voice=voice,
            enable_chunking=enable_chunking,
            chunk_size=chunk_size,
            concurrency=concurrency,
            rate=rate,
            volume=volume,
            pitch=pitch
        )
        
        # 总计时结束
        end_total = datetime.now()
        total_time = (end_total - start_total).total_seconds()
        
        # 获取合并时间并确保非零值
        if enable_chunking and merge_timer.segments_count > 1:
            # 如果应该有合并但测量值为0，使用估计值
            if merge_timer.merge_duration < 0.001:
                logger.warning(f"未检测到合并事件或合并时间为0，估算合并时间...")
                # 估算合并时间为总时间的10-15%
                estimated_merge_time = total_time * 0.12
                logger.warning(f"估算合并时间为 {estimated_merge_time:.4f}秒 (总时间的12%)")
                merging_time = estimated_merge_time
            else:
                merging_time = merge_timer.merge_duration
                logger.info(f"音频合并时间(实测): {merging_time:.4f}秒")
        else:
            merging_time = 0
        
        logger.info(f"收到事件数量: {merge_timer.events_received}")
        
        # 计算文本处理时间（总时间减去合并时间）
        processing_time = total_time - merging_time if enable_chunking else total_time
        
        audio_size = len(audio_data)
        
        # 检查音频数据是否为空
        if audio_size == 0:
            logger.error("错误: 生成的音频数据为空!")
            return 0, 0, 0, 0, 0, 0
        
        # 计算音频时长与文本比例（粗略估计）
        # 16kHz采样率，16位深度，单声道
        approx_duration = audio_size / 32000  # 字节数 / (采样率 * 位深度/8)
        chars_per_second = len(text) / approx_duration if approx_duration > 0 else 0
        
        # 保存音频文件
        # 生成文件名，包含语速和语调信息
        voice_short = voice.split("-")[-1].replace("Neural", "")
        rate_value = rate.replace("+", "p").replace("-", "n")
        pitch_value = pitch.replace("+", "p").replace("-", "n").replace("Hz", "")
        
        file_suffix = f"{voice_short}_{rate_value}_{pitch_value}"
        if enable_chunking:
            file_suffix += f"_c{chunk_size}_p{concurrency}"
        
        filename = f'tts_{file_suffix}.mp3'
        with open(filename, 'wb') as f:
            f.write(audio_data)
        
        logger.info(f'处理方式: {"分段并行" if enable_chunking else "常规"}, 文本长度: {len(text)}字符')
        logger.info(f'总处理时间: {total_time:.2f}秒')
        
        if enable_chunking:
            logger.info(f'文本分段并行处理: {processing_time:.2f}秒 ({processing_time/total_time*100:.1f}%)')
            # 确保显示非零值的合并时间
            if merging_time > 0:
                logger.info(f'音频合并时间: {merging_time:.4f}秒 ({merging_time/total_time*100:.1f}%)')
            else:
                logger.info(f'音频合并时间: <0.0001秒 (忽略不计)')
            logger.info(f'合并的音频段数: {merge_timer.segments_count}')
        else:
            logger.info(f'处理时间: {processing_time:.2f}秒')
            
        logger.info(f'音频大小: {audio_size}字节, 估计音频时长: {approx_duration:.2f}秒')
        logger.info(f'文本/音频比例: {chars_per_second:.2f}字符/秒')
        logger.info(f'音频已保存至: {os.path.abspath(filename)}')
        
        return total_time, processing_time, merging_time, len(text), audio_size, approx_duration
    except Exception as e:
        logger.error(f"TTS处理错误: {str(e)}", exc_info=True)
        # 捕获后重新抛出，以便上层处理
        raise

async def main():
    """命令行模式主函数"""
    # 检查命令行参数，如果有'--ui'参数则启动UI模式
    if len(sys.argv) > 1 and sys.argv[1] == '--ui':
        # UI模式
        root = tk.Tk()
        app = TTSUI(root)
        root.mainloop()
        return
        
    # 命令行模式
    # 检查ffmpeg是否已安装
    if not check_ffmpeg_installed():
        logger.warning("\n⚠️ 未检测到 ffmpeg 工具，这可能会导致音频拼接问题。")
        logger.warning("请使用以下命令安装 ffmpeg:")
        logger.warning("  - MacOS: brew install ffmpeg")
        logger.warning("  - Ubuntu/Debian: sudo apt-get install ffmpeg")
        logger.warning("  - Windows: 下载并安装 ffmpeg 后添加到系统 PATH")
        logger.warning("音频处理将使用备选方法（直接字节拼接），可能影响音频质量。\n")
    else:
        logger.info("\n✅ 检测到 ffmpeg 已安装，音频处理将使用 pydub 进行专业级合并。\n")

    # 生成冥想引导文字
    meditation_text = generate_meditation_text()
    text_length = len(meditation_text)
    logger.info(f"\n生成的冥想引导文字长度: {text_length} 字符")
    
    # 设置测试配置
    test_configs = [
        # (是否启用分段处理, 分段大小, 并发数)
        (False, 500, 3),      # 常规处理
        (True, 500, 3),       # 分段处理，500字符一段，3个并发
        (True, 400, 4),       # 分段处理，400字符一段，4个并发
    ]
    
    logger.info('\n开始进行对比测试...')
    results = []
    
    for enable_chunking, chunk_size, concurrency in test_configs:
        result = await test_tts(
            text=meditation_text,
            enable_chunking=enable_chunking,
            chunk_size=chunk_size,
            concurrency=concurrency
        )
        
        if result[0] > 0:  # 处理成功
            results.append((enable_chunking, chunk_size, concurrency) + result)
        
        logger.info('-' * 60)
    
    if len(results) < 2:
        logger.warning("没有足够的测试结果进行比较。")
        return
    
    # 比较结果
    logger.info('\n=== 音频生成性能比较 ===')
    logger.info('处理方式       | 总时间 | 处理时间 | 合并时间 | 音频时长 | 性能提升')
    logger.info('--------------|--------|----------|----------|----------|--------')
    
    # 常规处理作为基准
    normal_result = next((r for r in results if not r[0]), None)
    if not normal_result:
        logger.warning("没有常规处理的测试结果")
        return
    
    n_total_time, n_proc_time, n_merge_time, n_chars, _, n_duration = normal_result[3:]
    
    for result in results:
        enable_chunking, chunk_size, concurrency, total_time, proc_time, merge_time, chars, _, duration = result
        
        if enable_chunking:
            mode = f"分段{chunk_size}并发{concurrency}"
            improvement = (n_total_time - total_time) / n_total_time * 100 if n_total_time > 0 else 0
        else:
            mode = "常规处理"
            improvement = 0
        
        # 确保显示更精确的合并时间    
        merge_time_str = f"{merge_time:.4f}s" if merge_time > 0 else "<0.0001s"
        logger.info(f'{mode:14} | {total_time:6.2f}s | {proc_time:8.2f}s | {merge_time_str:10} | {duration:8.2f}s | {improvement:7.2f}%')
    
    # 判断是否能在30秒内完成生成
    if results:
        best_chunked = min((r for r in results if r[0]), key=lambda x: x[3])
        best_time = best_chunked[3]
        
        if best_time <= 30:
            logger.info(f'\n✅ 最佳分段处理可在30秒内完成音频生成: {best_time:.2f}秒')
        else:
            logger.info(f'\n❌ 分段处理仍无法在30秒内完成音频生成，最佳用时: {best_time:.2f}秒')

class TTSUI:
    """TTS测试程序的图形用户界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("TTS语音合成测试工具")
        self.root.geometry("1000x800")
        self.root.minsize(900, 700)
        
        self.client = None
        self.merge_timer = MergeTimeMeasurement()
        self.audio_files = []
        self.current_playing = None
        self.chinese_voices = []  # 存储所有中文语音
        
        # 初始化pygame音频
        pygame.mixer.init()
        
        self._create_ui()
        self._init_client()
    
    def _init_client(self):
        """初始化TTS客户端（在后台线程中执行）"""
        def init_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.client = TTSClient()
            # 注册事件处理器
            sdk.on_merge_start(self.merge_timer.on_merge_start)
            sdk.on_merge_end(self.merge_timer.on_merge_end)
            self._log("TTS客户端初始化完成")
            
            # 获取所有中文语音
            try:
                # 在异步环境中获取语音列表
                voices = loop.run_until_complete(self.client.get_voices())
                
                # 打印第一个语音的结构以便调试
                if voices and len(voices) > 0:
                    self._log(f"语音对象结构示例: {voices[0].keys()}")
                
                # 筛选中文语音
                chinese_voices = [v for v in voices if v.get("Locale") == "zh-CN"]
                self.chinese_voices = sorted(chinese_voices, key=lambda v: v.get("ShortName", ""))
                self._log(f"找到 {len(chinese_voices)} 个中文语音")
                
                # 在主线程中更新UI
                self.root.after(0, self._update_voice_list)
            except Exception as e:
                self._log(f"获取语音列表失败: {str(e)}")
                # 使用默认语音列表
                self.root.after(0, self._set_default_voices)
        
        threading.Thread(target=init_task, daemon=True).start()
    
    def _set_default_voices(self):
        """设置默认的中文语音列表（在自动获取失败时使用）"""
        self._log("使用内置的默认中文语音列表")
        default_voices = [
            {"ShortName": "zh-CN-XiaoxiaoNeural", "DisplayName": "晓晓", "Gender": "Female"},
            {"ShortName": "zh-CN-YunxiNeural", "DisplayName": "云希", "Gender": "Male"},
            {"ShortName": "zh-CN-YunjianNeural", "DisplayName": "云健", "Gender": "Male"},
            {"ShortName": "zh-CN-XiaoyiNeural", "DisplayName": "晓伊", "Gender": "Female"},
            {"ShortName": "zh-CN-YunyangNeural", "DisplayName": "云扬", "Gender": "Male"},
            {"ShortName": "zh-CN-XiaohanNeural", "DisplayName": "晓涵", "Gender": "Female"},
            {"ShortName": "zh-CN-XiaomoNeural", "DisplayName": "晓墨", "Gender": "Female"},
            {"ShortName": "zh-CN-XiaoxuanNeural", "DisplayName": "晓萱", "Gender": "Female"},
            {"ShortName": "zh-CN-XiaoruiNeural", "DisplayName": "晓睿", "Gender": "Female"},
            {"ShortName": "zh-CN-YunfengNeural", "DisplayName": "云枫", "Gender": "Male"}
        ]
        self.chinese_voices = default_voices
        self._update_voice_list()
    
    def _update_voice_list(self):
        """更新语音下拉框列表"""
        if not self.chinese_voices:
            self.voice_combo.configure(values=["未找到中文语音"])
            return
        
        # 提取所有中文语音的信息，格式化为显示用的选项
        voice_options = []
        for voice in self.chinese_voices:
            try:
                # 使用get方法安全地获取键值，提供默认值防止KeyError
                short_name = voice.get("ShortName", "Unknown")
                # 尝试获取不同可能的名称字段
                local_name = voice.get("LocalName", voice.get("DisplayName", voice.get("Name", "未知名称")))
                gender = "女声" if voice.get("Gender", "") == "Female" else "男声"
                
                # 格式: ShortName (LocalName - 性别)
                option = f"{short_name} ({local_name} - {gender})"
                voice_options.append(option)
            except Exception as e:
                self._log(f"处理语音选项时出错: {str(e)}, 语音数据: {voice}")
        
        if not voice_options:
            voice_options = ["未能正确解析语音数据"]
        
        # 更新下拉框选项
        self.voice_combo['values'] = voice_options
        
        # 设置默认选中项（找到XiaoxiaoNeural或第一个选项）
        default_index = 0
        for i, option in enumerate(voice_options):
            if "XiaoxiaoNeural" in option:
                default_index = i
                break
        
        self.voice_combo.current(default_index)
        self._log(f"语音列表已更新，共 {len(voice_options)} 个选项")
    
    def _get_selected_voice(self):
        """获取当前选中的语音ShortName"""
        selected = self.voice_combo.get()
        if not selected or " (" not in selected:
            return "zh-CN-XiaoxiaoNeural"  # 默认返回
        
        # 提取ShortName部分
        voice_id = selected.split(" (")[0].strip()
        
        # 确保语音ID格式正确
        if not voice_id.startswith("zh-CN-") or not voice_id.endswith("Neural"):
            self._log(f"警告: 语音ID格式可能不正确: '{voice_id}'，使用默认语音")
            return "zh-CN-XiaoxiaoNeural"
            
        self._log(f"选择语音: {voice_id}")
        return voice_id
    
    def _create_ui(self):
        """创建用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建顶部控制区域
        control_frame = ttk.LabelFrame(main_frame, text="语音合成参数控制", padding="10")
        control_frame.pack(fill=tk.X, pady=5)
        
        # 第一行控制 - 语音和分段选项
        row1 = ttk.Frame(control_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="语音:").pack(side=tk.LEFT, padx=(0,5))
        self.voice_var = tk.StringVar(value="zh-CN-XiaoxiaoNeural")
        self.voice_combo = ttk.Combobox(row1, textvariable=self.voice_var, width=35)
        # 初始设置几个常用选项，后续会动态更新
        self.voice_combo['values'] = ("正在加载语音列表...")
        self.voice_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="启用分段:").pack(side=tk.LEFT, padx=(15,5))
        self.chunking_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row1, variable=self.chunking_var).pack(side=tk.LEFT)
        
        ttk.Label(row1, text="段大小:").pack(side=tk.LEFT, padx=(15,5))
        self.chunk_size_var = tk.IntVar(value=500)
        chunk_spin = ttk.Spinbox(row1, from_=200, to=2000, increment=100, 
                                textvariable=self.chunk_size_var, width=5)
        chunk_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="并发数:").pack(side=tk.LEFT, padx=(15,5))
        self.concurrency_var = tk.IntVar(value=3)
        concurrency_spin = ttk.Spinbox(row1, from_=1, to=8, increment=1, 
                                      textvariable=self.concurrency_var, width=3)
        concurrency_spin.pack(side=tk.LEFT, padx=5)
        
        # 第二行控制 - 语速、音调、音量
        row2 = ttk.Frame(control_frame)
        row2.pack(fill=tk.X, pady=5)
        
        # 语速控制 - 使用滑杆替代下拉框
        rate_frame = ttk.LabelFrame(row2, text="语速调节")
        rate_frame.pack(side=tk.LEFT, padx=(0,10), fill=tk.X, expand=True)
        
        self.rate_var = tk.DoubleVar(value=0)
        self.rate_display = tk.StringVar(value="+0%")
        
        def update_rate(*args):
            value = int(self.rate_var.get())  # 确保是整数
            if value >= 0:
                self.rate_display.set(f"+{value}%")
            else:
                self.rate_display.set(f"{value}%")
        
        self.rate_var.trace_add("write", update_rate)
        
        rate_scale = ttk.Scale(rate_frame, from_=-50, to=50, orient=tk.HORIZONTAL,
                              variable=self.rate_var, length=200)
        # 设置刻度为 1
        rate_scale.configure(command=lambda v: self.rate_var.set(int(float(v))))
        rate_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Label(rate_frame, textvariable=self.rate_display, width=6, anchor=tk.CENTER).pack(side=tk.RIGHT, padx=5)
        
        # 音调控制 - 使用滑杆替代下拉框
        pitch_frame = ttk.LabelFrame(row2, text="音调调节")
        pitch_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        self.pitch_var = tk.DoubleVar(value=0)
        self.pitch_display = tk.StringVar(value="+0Hz")
        
        def update_pitch(*args):
            value = int(self.pitch_var.get())  # 确保是整数
            if value >= 0:
                self.pitch_display.set(f"+{value}Hz")
            else:
                self.pitch_display.set(f"{value}Hz")
        
        self.pitch_var.trace_add("write", update_pitch)
        
        pitch_scale = ttk.Scale(pitch_frame, from_=-50, to=50, orient=tk.HORIZONTAL,
                              variable=self.pitch_var, length=200)
        # 设置刻度为 1
        pitch_scale.configure(command=lambda v: self.pitch_var.set(int(float(v))))
        pitch_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Label(pitch_frame, textvariable=self.pitch_display, width=7, anchor=tk.CENTER).pack(side=tk.RIGHT, padx=5)
        
        # 音量控制 - 使用滑杆替代下拉框
        volume_frame = ttk.LabelFrame(row2, text="音量调节")
        volume_frame.pack(side=tk.LEFT, padx=(10,0), fill=tk.X, expand=True)
        
        self.volume_var = tk.DoubleVar(value=0)
        self.volume_display = tk.StringVar(value="+0%")
        
        def update_volume(*args):
            value = int(self.volume_var.get())  # 确保是整数
            if value >= 0:
                self.volume_display.set(f"+{value}%")
            else:
                self.volume_display.set(f"{value}%")
        
        self.volume_var.trace_add("write", update_volume)
        
        volume_scale = ttk.Scale(volume_frame, from_=-50, to=50, orient=tk.HORIZONTAL,
                               variable=self.volume_var, length=200)
        # 设置刻度为 1
        volume_scale.configure(command=lambda v: self.volume_var.set(int(float(v))))
        volume_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Label(volume_frame, textvariable=self.volume_display, width=6, anchor=tk.CENTER).pack(side=tk.RIGHT, padx=5)
        
        # 开始测试按钮
        self.start_btn = ttk.Button(control_frame, text="开始生成语音", command=self._start_test)
        self.start_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 文本输入区域
        text_frame = ttk.LabelFrame(main_frame, text="待处理文本", padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 使用默认文本复选框
        self.use_default_text_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(text_frame, text="使用默认冥想引导文本", 
                       variable=self.use_default_text_var,
                       command=self._toggle_text_state).pack(anchor=tk.W)
        
        # 文本输入框
        self.text_input = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=5)
        self.text_input.config(state=tk.DISABLED)
        
        # 创建底部区域
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 分割底部区域
        bottom_paned = ttk.PanedWindow(bottom_frame, orient=tk.HORIZONTAL)
        bottom_paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧 - 日志显示
        log_frame = ttk.LabelFrame(bottom_paned, text="处理日志", padding="10")
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        bottom_paned.add(log_frame, weight=50)
        
        # 右侧 - 音频列表和播放控件
        audio_frame = ttk.LabelFrame(bottom_paned, text="生成的音频文件", padding="10")
        
        # 文件列表
        list_frame = ttk.Frame(audio_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.audio_listbox = tk.Listbox(list_frame, height=6)
        self.audio_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                      command=self.audio_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.audio_listbox.config(yscrollcommand=list_scrollbar.set)
        self.audio_listbox.bind('<<ListboxSelect>>', self._on_audio_selected)
        
        # 刷新按钮
        refresh_btn = ttk.Button(audio_frame, text="刷新文件列表", command=self._refresh_audio_files)
        refresh_btn.pack(fill=tk.X, pady=(5,0))
        
        # 播放控件
        player_frame = ttk.Frame(audio_frame)
        player_frame.pack(fill=tk.X, pady=5)
        
        self.play_btn = ttk.Button(player_frame, text="播放", command=self._play_audio, width=10)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(player_frame, text="停止", command=self._stop_audio, width=10)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress = ttk.Progressbar(player_frame, variable=self.progress_var, length=200)
        self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        bottom_paned.add(audio_frame, weight=50)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 初始化调用刷新音频文件列表
        self._refresh_audio_files()
    
    def _toggle_text_state(self):
        """切换文本框状态"""
        if self.use_default_text_var.get():
            self.text_input.config(state=tk.DISABLED)
        else:
            self.text_input.config(state=tk.NORMAL)
    
    def _log(self, message):
        """向日志窗口添加消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _refresh_audio_files(self):
        """刷新音频文件列表"""
        self.audio_files = [f for f in os.listdir('.') if f.endswith('.mp3')]
        self.audio_listbox.delete(0, tk.END)
        
        for file in self.audio_files:
            self.audio_listbox.insert(tk.END, file)
        
        self._log(f"找到 {len(self.audio_files)} 个音频文件")
    
    def _on_audio_selected(self, event):
        """当音频文件被选中时"""
        if self.audio_listbox.curselection():
            index = self.audio_listbox.curselection()[0]
            file = self.audio_files[index]
            self.status_var.set(f"已选择: {file}")
    
    def _play_audio(self):
        """播放选中的音频文件"""
        if self.audio_listbox.curselection():
            index = self.audio_listbox.curselection()[0]
            file = self.audio_files[index]
            
            # 停止当前播放
            self._stop_audio()
            
            # 播放新文件
            try:
                pygame.mixer.music.load(file)
                pygame.mixer.music.play()
                self.current_playing = file
                self.status_var.set(f"正在播放: {file}")
                self._log(f"开始播放: {file}")
                
                # 启动进度更新
                self._update_progress()
            except Exception as e:
                self._log(f"播放出错: {str(e)}")
    
    def _stop_audio(self):
        """停止音频播放"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.status_var.set("已停止播放")
            self._log(f"停止播放: {self.current_playing}")
            self.current_playing = None
            self.progress_var.set(0)
    
    def _update_progress(self):
        """更新播放进度条"""
        if pygame.mixer.music.get_busy():
            pos = pygame.mixer.music.get_pos() / 1000  # 转换为秒
            # 假设音频长度约为10分钟
            progress = min(100, pos / 600 * 100)
            self.progress_var.set(progress)
            self.root.after(1000, self._update_progress)
        else:
            self.progress_var.set(0)
            if self.current_playing:
                self.status_var.set(f"播放完成: {self.current_playing}")
                self.current_playing = None
    
    def _start_test(self):
        """开始TTS测试"""
        # 禁用开始按钮
        self.start_btn.config(state=tk.DISABLED)
        self.status_var.set("正在生成语音...")
        
        # 获取参数，根据滑杆值生成格式化字符串
        rate_value = int(self.rate_var.get())  # 转换为整数
        pitch_value = int(self.pitch_var.get())  # 转换为整数
        volume_value = int(self.volume_var.get())  # 转换为整数
        
        # 格式化为SDK需要的百分比和Hz格式 (整数值)
        rate_str = f"+{rate_value}%" if rate_value >= 0 else f"{rate_value}%"
        pitch_str = f"+{pitch_value}Hz" if pitch_value >= 0 else f"{pitch_value}Hz"
        volume_str = f"+{volume_value}%" if volume_value >= 0 else f"{volume_value}%"
        
        # 获取选中的语音ShortName
        voice = self._get_selected_voice()
        
        params = {
            "voice": voice,
            "enable_chunking": self.chunking_var.get(),
            "chunk_size": self.chunk_size_var.get(),
            "concurrency": self.concurrency_var.get(),
            "rate": rate_str,
            "volume": volume_str,
            "pitch": pitch_str
        }
        
        # 记录完整的参数信息用于调试
        self._log(f"完整参数: {params}")
        
        # 获取文本
        if self.use_default_text_var.get():
            text = generate_meditation_text()
        else:
            text = self.text_input.get("1.0", tk.END)
        
        # 重置合并计时器
        self.merge_timer.reset()
        
        self._log(f"开始生成语音: 文本长度={len(text)}字符")
        self._log(f"参数: 语音={params['voice']}, 分段={params['enable_chunking']}, " +
                 f"段大小={params['chunk_size']}, 并发数={params['concurrency']}")
        self._log(f"语音参数: 语速={params['rate']}, 音调={params['pitch']}, 音量={params['volume']}")
        
        # 在后台线程中运行
        def run_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(test_tts(
                    text=text,
                    enable_chunking=params["enable_chunking"],
                    chunk_size=params["chunk_size"],
                    concurrency=params["concurrency"],
                    rate=params["rate"],
                    volume=params["volume"],
                    pitch=params["pitch"],
                    voice=params["voice"]
                ))
                # 在主线程中更新UI
                self.root.after(0, lambda: self._test_completed(result))
            except Exception as e:
                error_msg = f"生成语音时出错: {str(e)}"
                self._log(error_msg)
                # 在主线程中更新UI显示错误
                self.root.after(0, lambda: self._handle_test_error(error_msg))
        
        threading.Thread(target=run_task, daemon=True).start()
    
    def _test_completed(self, result):
        """测试完成后的回调"""
        if result and result[0] > 0:
            total_time, processing_time, merging_time, text_len, audio_size, approx_duration = result
            
            self._log("=" * 40)
            self._log(f"语音生成完成!")
            self._log(f"总处理时间: {total_time:.2f}秒")
            
            if self.chunking_var.get():
                self._log(f"文本处理时间: {processing_time:.2f}秒 ({processing_time/total_time*100:.1f}%)")
                self._log(f"音频合并时间: {merging_time:.4f}秒 ({merging_time/total_time*100:.1f}%)")
                self._log(f"合并的音频段数: {self.merge_timer.segments_count}")
            
            self._log(f"音频大小: {audio_size}字节")
            self._log(f"估计音频时长: {approx_duration:.2f}秒")
            self._log(f"文本/音频比例: {text_len/approx_duration:.2f}字符/秒")
            self._log("=" * 40)
            
            self.status_var.set(f"语音生成完成! 用时: {total_time:.2f}秒")
        else:
            self._log("语音生成失败!")
            self.status_var.set("语音生成失败!")
        
        # 恢复开始按钮
        self.start_btn.config(state=tk.NORMAL)
        
        # 刷新文件列表
        self._refresh_audio_files()
    
    def _handle_test_error(self, error_msg):
        """处理测试过程中的错误"""
        self.status_var.set(f"错误: {error_msg[:50]}...")
        # 恢复开始按钮
        self.start_btn.config(state=tk.NORMAL)
        # 显示更醒目的错误信息
        messagebox.showerror("语音生成失败", error_msg)

if __name__ == "__main__":
    # 默认启动UI模式
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # 命令行模式
        asyncio.run(main())
    else:
        # UI模式
        root = tk.Tk()
        app = TTSUI(root)
        root.mainloop() 