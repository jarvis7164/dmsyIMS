#!/bin/bash
# ===========================================
# 大麦摄影管理系统 - 自动部署脚本
# 通过 Gitee Webhook 调用
# ===========================================

set -e

# 配置
APP_DIR="/opt/dmsyIMS"
LOG_FILE="$APP_DIR/webhook/deploy.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 进入项目目录
cd $APP_DIR

# 记录开始时间
log "==========================================="
log "🚀 开始自动部署..."
log "==========================================="

# 保存当前版本（用于回滚）
CURRENT_COMMIT=$(git rev-parse HEAD)
log "当前版本: $CURRENT_COMMIT"

# 停止当前服务
log "📦 停止当前服务..."
docker-compose down || true

# 拉取最新代码
log "📥 正在拉取最新代码..."
git pull origin main

# 获取新版本
NEW_COMMIT=$(git rev-parse HEAD)
log "新版本: $NEW_COMMIT"

# 重新构建并启动
log "🔨 正在重新构建 Docker 容器..."
docker-compose up -d --build

# 等待服务启动
log "⏳ 等待服务启动..."
sleep 20

# 检查服务状态
log "📊 检查服务状态..."
docker-compose ps

# 健康检查
log "🏥 执行健康检查..."
MAX_RETRIES=5
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f -s http://localhost:8080/login > /dev/null 2>&1; then
        log "✅ 健康检查通过！"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        log "⏳ 健康检查中... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 5
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    log "❌ 健康检查失败！"
    log "📋 最近日志："
    docker-compose logs --tail=20 | tee -a "$LOG_FILE"
    log "尝试回滚..."
    git checkout $CURRENT_COMMIT
    docker-compose up -d --build
    exit 1
fi

# 查看日志
log "📋 最近日志："
docker-compose logs --tail=10 | tee -a "$LOG_FILE"

log "==========================================="
log "✅ 部署完成！"
log "==========================================="
log "访问地址: http://localhost:8080"
log ""
