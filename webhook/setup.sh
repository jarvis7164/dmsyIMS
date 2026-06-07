#!/bin/bash
# ===========================================
# 一键安装 Webhook 部署服务
# 大麦摄影管理系统
# ===========================================

set -e

# 配置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的信息
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "=========================================="
echo "  大麦摄影管理系统 - Webhook 安装脚本"
echo "=========================================="
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    log_warn "请使用 root 用户运行此脚本"
    exit 1
fi

# 1. 安装依赖
log_info "安装 Python3 和 Flask..."
if command -v yum &> /dev/null; then
    yum install -y python3 python3-pip
elif command -v apt-get &> /dev/null; then
    apt-get update
    apt-get install -y python3 python3-pip
fi

# 2. 安装 Docker（如果没有）
log_info "检查 Docker..."
if ! command -v docker &> /dev/null; then
    log_info "安装 Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
else
    log_info "Docker 已安装"
fi

# 3. 安装 Docker Compose
log_info "检查 Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    log_info "安装 Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    log_info "Docker Compose 已安装"
fi

# 4. 创建项目目录
log_info "创建项目目录..."
APP_DIR="/opt/dmsyIMS"
mkdir -p $APP_DIR/webhook/logs
mkdir -p $APP_DIR/instance
mkdir -p $APP_DIR/logs

# 5. 复制 Webhook 文件
log_info "复制 Webhook 文件..."
cp webhook/deploy.sh $APP_DIR/webhook/
cp webhook/server.py $APP_DIR/webhook/
chmod +x $APP_DIR/webhook/deploy.sh

# 6. 安装 Python 依赖
log_info "安装 Python 依赖..."
cd $APP_DIR/webhook
pip3 install -r requirements.txt

# 7. 创建 systemd 服务
log_info "创建 systemd 服务..."
cat > /etc/systemd/system/dmsy-webhook.service << 'EOF'
[Unit]
Description=Gitee Webhook Service for dmsyIMS
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/dmsyIMS/webhook
ExecStart=/usr/bin/python3 /opt/dmsyIMS/webhook/server.py
Restart=always
RestartSec=10
StandardOutput=append:/opt/dmsyIMS/webhook/webhook.log
StandardError=append:/opt/dmsyIMS/webhook/webhook.log

[Install]
WantedBy=multi-user.target
EOF

# 8. 重新加载 systemd
log_info "重新加载 systemd 配置..."
systemctl daemon-reload

# 9. 启动 Webhook 服务
log_info "启动 Webhook 服务..."
systemctl start dmsy-webhook
systemctl enable dmsy-webhook

# 10. 检查状态
log_info "检查服务状态..."
sleep 2
systemctl status dmsy-webhook --no-pager

echo ""
echo "=========================================="
log_info "Webhook 服务安装完成！"
echo "=========================================="
echo ""
echo "常用命令："
echo "  systemctl start dmsy-webhook    # 启动服务"
echo "  systemctl stop dmsy-webhook     # 停止服务"
echo "  systemctl restart dmsy-webhook # 重启服务"
echo "  systemctl status dmsy-webhook   # 查看状态"
echo "  journalctl -u dmsy-webhook -f   # 查看日志"
echo ""
echo "Webhook 接收地址："
echo "  http://你的服务器IP:8081/webhook"
echo ""
echo "下一步："
echo "  1. 在 Gitee 仓库中添加 Webhook："
echo "     设置 → WebHooks → 添加 WebHook"
echo "     请求 URL: http://你的服务器IP:8081/webhook"
echo "     密钥: dmsy123456"
echo "  2. 确保腾讯云安全组开放 8081 端口"
echo ""
