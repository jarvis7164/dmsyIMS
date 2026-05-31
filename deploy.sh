#!/bin/bash
# 大麦摄影管理系统 - 一键部署脚本

set -e

echo "======================================"
echo "  大麦摄影管理系统 - 一键部署脚本"
echo "======================================"

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
  echo "请使用 sudo 运行此脚本"
  exit 1
fi

# 检测操作系统
if [ -f /etc/os-release ]; then
  . /etc/os-release
  OS=$ID
else
  echo "无法识别操作系统"
  exit 1
fi

# 安装 Docker
echo "[1/5] 安装 Docker..."
case $OS in
  tencentos)
    yum install -y docker
    systemctl enable docker
    systemctl start docker
    ;;
  ubuntu|debian)
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    ;;
  centos|rhel|almalinux|rocky)
    yum install -y yum-utils
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    yum install -y docker-ce docker-ce-cli containerd.io
    systemctl enable docker
    systemctl start docker
    ;;
  *)
    echo "不支持的操作系统：$OS"
    exit 1
    ;;
esac

# 安装 Docker Compose
echo "[2/5] 安装 Docker Compose..."
curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 创建应用目录
echo "[3/5] 创建应用目录..."
APP_DIR="/opt/dmsyIMS"
mkdir -p $APP_DIR
mkdir -p $APP_DIR/instance
mkdir -p $APP_DIR/logs

# 生成随机 SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)
echo "[4/5] 生成配置..."

# 创建 docker-compose.yml
cat > $APP_DIR/docker-compose.yml << EOF
version: '3.8'

services:
  dmsy-ims:
    build: .
    container_name: dmsy-ims
    restart: always
    ports:
      - "8080:8080"
    volumes:
      - ./instance:/app/instance
      - ./logs:/app/logs
    environment:
      - SECRET_KEY=$SECRET_KEY
      - DATABASE_URI=sqlite:///instance/company_data.db
EOF

# 复制项目文件
echo "[5/5] 复制项目文件..."
cp -r ./* $APP_DIR/

cd $APP_DIR

# 启动服务
echo "正在启动服务..."
docker-compose up -d --build

echo ""
echo "======================================"
echo "  部署完成！"
echo "======================================"
echo ""
echo "访问地址：http://$(hostname -I | awk '{print $1}'):8080"
echo ""
echo "常用命令："
echo "  cd $APP_DIR"
echo "  docker-compose logs -f     # 查看日志"
echo "  docker-compose restart     # 重启服务"
echo "  docker-compose down        # 停止服务"
echo ""
