#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gitee Webhook 接收服务
大麦摄影管理系统 - dmsyIMS

功能：接收 Gitee Webhook 请求，自动触发部署脚本
"""

from flask import Flask, request, jsonify
import subprocess
import logging
import os
import signal
import sys

app = Flask(__name__)

# ==================== 配置 ====================
CONFIG = {
    # Webhook 密钥（与 Gitee Webhook 设置中的密钥一致）
    'SECRET_TOKEN': os.getenv('WEBHOOK_SECRET', 'dmsy123456'),
    
    # 部署脚本路径
    'DEPLOY_SCRIPT': '/opt/dmsyIMS/webhook/deploy.sh',
    
    # Webhook 日志文件
    'LOG_FILE': '/opt/dmsyIMS/webhook/webhook.log',
    
    # 允许部署的分支
    'ALLOWED_BRANCHES': ['main', 'master'],
}

# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(CONFIG['LOG_FILE'], encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== 信号处理 ====================
def signal_handler(sig, frame):
    """处理 Ctrl+C 信号"""
    logger.info("收到停止信号，正在关闭服务...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ==================== 路由 ====================

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    处理 Gitee Webhook 请求
    """
    logger.info("=" * 60)
    logger.info("📢 收到 Webhook 请求")
    
    # 获取请求数据
    try:
        data = request.json
        if not data:
            logger.error("❌ 无效的请求数据")
            return jsonify({'error': 'Invalid payload'}), 400
    except Exception as e:
        logger.error(f"❌ 解析请求数据失败: {str(e)}")
        return jsonify({'error': 'Invalid JSON'}), 400
    
    # 获取推送信息
    ref = data.get('ref', '')
    branch = ref.replace('refs/heads/', '') if ref else ''
    commits = data.get('commits', [])
    pusher = data.get('pusher', {}).get('name', 'Unknown')
    
    logger.info(f"   分支: {branch}")
    logger.info(f"   推送者: {pusher}")
    logger.info(f"   提交数: {len(commits)}")
    
    # 显示最近 3 个提交
    if commits:
        logger.info("   最近提交:")
        for commit in commits[:3]:
            logger.info(f"     - {commit.get('message', '')[:50]}")
    
    # 验证分支
    if branch not in CONFIG['ALLOWED_BRANCHES']:
        logger.warning(f"⚠️ 分支 '{branch}' 不在允许列表中，跳过部署")
        return jsonify({
            'status': 'skipped',
            'message': f'Branch {branch} not in allowed list'
        }), 200
    
    # 执行部署
    logger.info("🚀 开始执行部署脚本...")
    
    try:
        # 检查部署脚本是否存在
        if not os.path.exists(CONFIG['DEPLOY_SCRIPT']):
            logger.error(f"❌ 部署脚本不存在: {CONFIG['DEPLOY_SCRIPT']}")
            return jsonify({'error': 'Deploy script not found'}), 500
        
        # 设置脚本执行权限
        os.chmod(CONFIG['DEPLOY_SCRIPT'], 0o755)
        
        # 执行部署脚本
        result = subprocess.run(
            ['bash', CONFIG['DEPLOY_SCRIPT']],
            capture_output=True,
            text=True,
            timeout=600  # 10 分钟超时
        )
        
        if result.returncode == 0:
            logger.info("✅ 部署成功！")
            return jsonify({
                'status': 'success',
                'message': 'Deployment completed successfully'
            }), 200
        else:
            logger.error(f"❌ 部署失败！退出码: {result.returncode}")
            logger.error(f"错误输出: {result.stderr}")
            return jsonify({
                'status': 'failed',
                'error': result.stderr
            }), 500
            
    except subprocess.TimeoutExpired:
        logger.error("❌ 部署超时！（超过 10 分钟）")
        return jsonify({
            'status': 'failed',
            'error': 'Deployment timeout'
        }), 500
        
    except Exception as e:
        logger.error(f"❌ 部署过程出错: {str(e)}")
        return jsonify({
            'status': 'failed',
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """
    健康检查端点
    """
    return jsonify({
        'status': 'ok',
        'service': 'dmsyIMS Webhook',
        'version': '1.0.0'
    }), 200


@app.route('/status', methods=['GET'])
def status():
    """
    查看部署状态
    """
    try:
        # 获取 Docker 容器状态
        ps_result = subprocess.run(
            ['docker-compose', '-f', '/opt/dmsyIMS/docker-compose.yml', 'ps'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return jsonify({
            'status': 'ok',
            'containers': ps_result.stdout,
            'webhook_log': '请查看 /opt/dmsyIMS/webhook/webhook.log'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


# ==================== 启动服务 ====================
if __name__ == '__main__':
    logger.info("")
    logger.info("=" * 60)
    logger.info("🚀 Gitee Webhook 部署服务启动")
    logger.info("=" * 60)
    logger.info(f"监听地址: 0.0.0.0:8081")
    logger.info(f"部署脚本: {CONFIG['DEPLOY_SCRIPT']}")
    logger.info(f"日志文件: {CONFIG['LOG_FILE']}")
    logger.info(f"允许分支: {', '.join(CONFIG['ALLOWED_BRANCHES'])}")
    logger.info("")
    logger.info("端点:")
    logger.info("  POST /webhook  - 接收 Webhook 请求")
    logger.info("  GET  /health   - 健康检查")
    logger.info("  GET  /status   - 查看状态")
    logger.info("")
    logger.info("=" * 60)
    logger.info("")
    
    # 启动 Flask 服务
    app.run(
        host='0.0.0.0',
        port=8081,
        debug=False,
        threaded=True
    )
