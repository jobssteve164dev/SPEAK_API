from fastapi import FastAPI, HTTPException, Request, Depends, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import edge_tts
import asyncio
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import base64
import os
from dotenv import load_dotenv
import logging
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("tts-api")

# 加载环境变量
load_dotenv()

app = FastAPI(title="实时文字转语音引擎")

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
    voices = await edge_tts.list_voices()
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

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    try:
        logger.info(f"正在处理TTS请求: 文本长度 {len(request.text)} 字符, 语音 {request.voice}")
        communicate = edge_tts.Communicate(
            text=request.text,
            voice=request.voice,
            rate=request.rate,
            volume=request.volume,
            pitch=request.pitch
        )
        
        # 生成音频数据
        audio_data = await communicate.get_audio()
        logger.info(f"TTS请求处理成功: 生成音频大小 {len(audio_data)} 字节")
        return {"audio": base64.b64encode(audio_data).decode()}
    except Exception as e:
        logger.error(f"TTS请求处理失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voices")
async def get_available_voices():
    """获取所有可用的语音列表"""
    voices = await edge_tts.list_voices()
    return {"voices": voices}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求的中间件"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - 处理时间: {process_time:.2f}s - 状态码: {response.status_code}")
    return response 