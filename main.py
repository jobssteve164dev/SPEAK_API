from fastapi import FastAPI, HTTPException, Request, Depends, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
from pydantic import BaseModel
from typing import Optional, List
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import base64
import os
from dotenv import load_dotenv
import logging
import time
from tts_edge_sdk import TTSClient  # 导入新的SDK包

# 加载环境变量
load_dotenv()

# 配置日志
log_level_str = os.getenv("LOG_LEVEL", "INFO")
log_level = getattr(logging, log_level_str.upper(), logging.INFO)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("tts-api")
logger.info(f"日志级别设置为: {log_level_str}")

app = FastAPI(title="实时文字转语音引擎")

# 创建TTS客户端实例
tts_client = TTSClient()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置模板和静态文件
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # 从环境变量获取，如未设置则使用默认值
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 模拟用户数据库
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "disabled": False,
    }
}

class TTSRequest(BaseModel):
    text: str
    voice: str = "zh-CN-XiaoxiaoNeural"
    rate: Optional[str] = "+0%"
    volume: Optional[str] = "+0%"
    pitch: Optional[str] = "+0%"
    enable_chunking: Optional[bool] = False  # 是否启用分段处理
    chunk_size: Optional[int] = 1000  # 默认每段文本字符数
    concurrency: Optional[int] = 3  # 并发处理段数

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return user_dict

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    user = get_user(username)
    return user

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    voices = await tts_client.get_voices()  # 使用SDK获取语音列表
    return templates.TemplateResponse("index.html", {"request": request, "voices": voices})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    user = get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        logger.warning(f"登录失败: 用户 {username} - 密码错误或用户不存在")
        return templates.TemplateResponse(
            "login.html",
            {"request": Request, "error": "用户名或密码错误"}
        )
    logger.info(f"用户 {username} 登录成功")
    access_token = create_access_token(data={"sub": user["username"]})
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=access_token)
    return response

@app.post("/logout")
async def logout(response: Response):
    logger.info("用户登出")
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response

async def process_text_chunk(text: str, voice: str, rate: str, volume: str, pitch: str) -> bytes:
    """处理单个文本段"""
    return await tts_client.text_to_speech(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch
    )

async def process_long_text(text: str, voice: str, rate: str, volume: str, pitch: str, 
                            chunk_size: int = 1000, concurrency: int = 3) -> bytes:
    """分段并行处理长文本"""
    # 按标点符号分段
    chunks = []
    current_chunk = ""
    
    # 常见中文和英文标点符号
    sentence_end_marks = ["。", "！", "？", "；", ".", "!", "?", ";"]
    
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
    
    logger.info(f"长文本被分为 {len(chunks)} 段进行处理，平均段长: {sum(len(c) for c in chunks)/len(chunks):.1f} 字符")
    
    # 创建一个信号量来限制并发任务数
    semaphore = asyncio.Semaphore(concurrency)
    
    async def process_with_semaphore(chunk: str) -> bytes:
        async with semaphore:
            return await process_text_chunk(chunk, voice, rate, volume, pitch)
    
    # 并行处理所有文本段
    start_time = time.time()
    tasks = [process_with_semaphore(chunk) for chunk in chunks]
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start_time
    
    logger.info(f"并行处理完成: {len(chunks)} 段文本, 总时间: {elapsed:.2f}秒, 平均每段: {elapsed/len(chunks):.2f}秒")
    
    # 合并所有音频段落
    combined_audio = b''.join(results)
    return combined_audio

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    try:
        logger.info(f"正在处理TTS请求: 文本长度 {len(request.text)} 字符, 语音 {request.voice}")
        
        start_time = time.time()
        
        # 根据文本长度和用户选项决定是否使用分段处理
        if len(request.text) > 1000 and request.enable_chunking:
            # 使用分段并行处理
            audio_data = await process_long_text(
                text=request.text,
                voice=request.voice,
                rate=request.rate,
                volume=request.volume,
                pitch=request.pitch,
                chunk_size=request.chunk_size,
                concurrency=request.concurrency
            )
        else:
            # 使用普通处理方式
            audio_data = await tts_client.text_to_speech(
                text=request.text,
                voice=request.voice,
                rate=request.rate,
                volume=request.volume,
                pitch=request.pitch
            )
        
        elapsed = time.time() - start_time
        logger.info(f"TTS请求处理成功: 文本长度 {len(request.text)} 字符, 生成音频大小 {len(audio_data)} 字节, 处理时间: {elapsed:.2f}秒")
        return {"audio": base64.b64encode(audio_data).decode()}
    except Exception as e:
        logger.error(f"TTS请求处理失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voices")
async def get_available_voices():
    """获取所有可用的语音列表"""
    voices = await tts_client.get_voices()  # 使用SDK获取语音列表
    return {"voices": voices}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求的中间件"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - 处理时间: {process_time:.2f}s - 状态码: {response.status_code}")
    return response 