# TTS API 服务

基于 FastAPI 和 Edge TTS 的实时文字转语音服务。

## 功能特点

- 实时文字转语音
- 多语言支持
- 可调节的语音参数（语速、音量、音调）
- Web管理界面
- RESTful API接口
- Docker支持

## 快速开始

### 使用 Docker

1. 构建镜像
```bash
docker-compose build
```

2. 启动服务
```bash
docker-compose up -d
```

3. 访问服务
- Web界面：http://localhost:8000
- API文档：http://localhost:8000/docs

### 手动部署

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 启动服务
```bash
uvicorn main:app --reload
```

## 文档

- [API文档](docs/API.md)
- [部署指南](docs/DEPLOY.md)

## 默认账号

- 用户名：admin
- 密码：admin123

## 开发

### 目录结构

```
SPEAK_API/
├── docs/           # 文档
├── static/         # 静态文件
├── templates/      # HTML模板
├── main.py         # 主应用
├── requirements.txt # 依赖
├── Dockerfile      # Docker配置
└── docker-compose.yml # Docker编排
```

### 本地开发

1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

2. 安装开发依赖
```bash
pip install -r requirements.txt
```

3. 启动开发服务器
```bash
uvicorn main:app --reload
```

## 许可证

MIT # SPEAK_API
