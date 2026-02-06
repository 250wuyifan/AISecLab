FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 初始化数据库
RUN python manage.py migrate --noinput

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
