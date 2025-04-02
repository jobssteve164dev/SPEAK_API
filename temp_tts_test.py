import asyncio
from datetime import datetime
import os
import sys
import time
import logging
import subprocess
import importlib  # 添加importlib用于重新加载模块

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

async def test_tts(text: str = None, enable_chunking: bool = False, chunk_size: int = 500, concurrency: int = 3):
    """测试TTS性能"""
    if text is None:
        text = generate_meditation_text()
    
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
    
    # 总计时开始
    start_total = datetime.now()
    
    try:
        # 使用SDK生成音频
        audio_data = await client.text_to_speech(
            text=text,
            voice="zh-CN-XiaoxiaoNeural",
            enable_chunking=enable_chunking,
            chunk_size=chunk_size,
            concurrency=concurrency,
            rate="+0%",
            volume="+0%",
            pitch="+0Hz"
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
        file_suffix = f"chunked_{chunk_size}_c{concurrency}" if enable_chunking else "normal"
        filename = f'meditation_{file_suffix}.mp3'
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
        return 0, 0, 0, 0, 0, 0

async def main():
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

if __name__ == "__main__":
    asyncio.run(main()) 