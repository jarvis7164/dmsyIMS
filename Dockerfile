# 使用官方 Python 运行时作为父镜像
FROM python:3.8-slim-buster

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器的 /app 中
COPY . /app

# 使用阿里云的 PyPI 镜像源
RUN echo "[global]" > /etc/pip.conf \
    && echo "index-url = http://mirrors.aliyun.com/pypi/simple/" >> /etc/pip.conf \
    && echo "trusted-host = mirrors.aliyun.com" >> /etc/pip.conf

# 安装 sqlite3 工具
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 安装所需的包
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8081

# 运行 gunicorn 作为容器的默认命令
CMD ["gunicorn", "-w", "4", "--bind", "0.0.0.0:8081", "app:app"]
