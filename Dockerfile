# 大麦摄影管理系统 Dockerfile
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 先复制依赖文件，利用 Docker 缓存层
COPY requirements.txt .

# 使用 PyPI 镜像源加速安装
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . /app

# 创建数据卷目录
RUN mkdir -p /app/instance

# 设置环境变量
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8080

# 使用 gunicorn 启动
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
