# 部署指南

## Docker 部署

### 前置条件

- Docker
- Docker Compose

### 部署步骤

1. 克隆项目
```bash
git clone [项目地址]
cd SPEAK_API
```

2. 构建 Docker 镜像
```bash
docker-compose build
```

3. 启动服务
```bash
docker-compose up -d
```

4. 查看日志
```bash
docker-compose logs -f
```

### 环境变量配置

在 `docker-compose.yml` 中可以配置以下环境变量：

- `SECRET_KEY`: JWT 密钥（必需）
- `PORT`: 服务端口（可选，默认 8000）

### 访问服务

- Web界面：http://localhost:8000
- API文档：http://localhost:8000/docs
- API接口：http://localhost:8000/tts

## 手动部署

### 前置条件

- Python 3.11+
- pip

### 部署步骤

1. 克隆项目
```bash
git clone [项目地址]
cd SPEAK_API
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 启动服务
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 安全配置

1. 修改默认密钥
   - 在 `main.py` 中修改 `SECRET_KEY`
   - 或通过环境变量设置

2. 配置 HTTPS
   - 使用 Nginx 作为反向代理
   - 配置 SSL 证书

3. 设置访问控制
   - 配置防火墙规则
   - 设置 IP 白名单

## 监控和维护

1. 日志查看
```bash
# Docker 部署
docker-compose logs -f

# 手动部署
tail -f nohup.out
```

2. 服务状态检查
```bash
# Docker 部署
docker-compose ps

# 手动部署
ps aux | grep uvicorn
```

3. 重启服务
```bash
# Docker 部署
docker-compose restart

# 手动部署
pkill -f uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 故障排除

1. 服务无法启动
   - 检查端口占用
   - 检查日志输出
   - 验证依赖安装

2. API 访问失败
   - 检查网络连接
   - 验证请求格式
   - 查看错误日志

3. 性能问题
   - 检查系统资源使用
   - 优化并发设置
   - 考虑使用缓存 