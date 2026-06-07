# 🆓 免费 CI/CD 自动化部署指南

## 📋 方案概述

使用 **Gitee Webhooks + Python Webhook 服务**，实现完全免费的自动化部署。

**工作原理**：
```
本地代码 → git push → Gitee Webhook → 服务器接收 → 自动执行部署脚本
```

**优点**：
- ✅ 完全免费（无需 Gitee 流水线）
- ✅ 无需第三方服务
- ✅ 代码推送后自动部署
- ✅ 配置简单

---

## 🔧 快速配置（5 分钟完成）

### 第一步：上传代码到 Gitee

```bash
# 进入项目目录
cd D:\pythonProject\python\dmsyIMS

# 初始化 Git（如果还没有）
git init
git add .
git commit -m "初始提交"

# 添加 Gitee 远程仓库
git remote add origin https://gitee.com/你的用户名/dmsyIMS.git

# 推送代码
git push -u origin main
```

### 第二步：SSH 登录服务器，执行一键安装

SSH 登录到腾讯云服务器：

```bash
# 1. 克隆项目到服务器
cd /opt
git clone https://gitee.com/你的用户名/dmsyIMS.git

# 2. 进入项目目录
cd dmsyIMS

# 3. 运行一键安装脚本
chmod +x webhook/setup.sh
./webhook/setup.sh
```

### 第三步：在 Gitee 配置 Webhook

1. 进入 Gitee 仓库
2. 点击 **设置** → **WebHooks** → **添加 WebHook**
3. 填写信息：

| 配置项 | 值 |
|--------|-----|
| **请求 URL** | `http://你的服务器IP:8081/webhook` |
| **密钥** | `dmsy123456` |
| **请求方式** | `POST` |
| **触发事件** | ☑️ Push（推送） |
| **内容格式** | `application/json` |

4. 点击 **添加**
5. 点击 **测试** 验证配置

### 第四步：开放服务器端口

在腾讯云控制台 → 安全组，开放以下端口：

| 端口 | 用途 |
|------|------|
| 8080 | 应用访问 |
| 8081 | Webhook 接收 |
| 22 | SSH |

---

## ✅ 完成！测试一下

```bash
# 在本地修改代码
git add .
git commit -m "测试 CI/CD"
git push origin main

# 然后访问 http://服务器IP:8080 查看效果
```

---

## 📂 项目文件说明

```
webhook/
├── deploy.sh      # 部署脚本（拉取代码 + 重启容器）
├── server.py      # Webhook 接收服务（Python Flask）
├── requirements.txt # Python 依赖
├── setup.sh       # 一键安装脚本
└── webhook.log    # 运行日志（自动生成）
```

---

## 🛠️ 常用命令

### 服务器上查看日志

```bash
# Webhook 请求日志
tail -f /opt/dmsyIMS/webhook/webhook.log

# 应用日志
docker-compose -f /opt/dmsyIMS/docker-compose.yml logs -f

# 查看容器状态
docker-compose -f /opt/dmsyIMS/docker-compose.yml ps
```

### 重启服务

```bash
# 重启 Webhook 服务
systemctl restart dmsy-webhook

# 重启应用
cd /opt/dmsyIMS
docker-compose restart
```

### 手动部署

```bash
cd /opt/dmsyIMS
./webhook/deploy.sh
```

---

## 🔍 故障排查

### 1. Webhook 没有触发
- ✅ 检查 Gitee Webhook 配置是否正确
- ✅ 确保服务器 8081 端口已开放
- ✅ 查看 Gitee Webhook 发送记录

### 2. 部署失败
```bash
# 查看详细日志
cat /opt/dmsyIMS/webhook/webhook.log

# 手动执行部署
bash /opt/dmsyIMS/webhook/deploy.sh
```

### 3. 服务无法启动
```bash
# 查看 Webhook 服务状态
systemctl status dmsy-webhook

# 查看错误日志
journalctl -u dmsy-webhook -n 50
```

---

## 🔐 安全建议

### 1. 修改默认密钥

编辑 `server.py`，修改默认密钥：

```python
CONFIG = {
    'SECRET_TOKEN': os.getenv('WEBHOOK_SECRET', '你的自定义密钥'),
    # ...
}
```

然后在 Gitee Webhook 设置中更新密钥。

### 2. 使用 HTTPS（推荐）

生产环境建议使用 HTTPS，可以使用 Nginx 反向代理：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /webhook {
        proxy_pass http://127.0.0.1:8081;
    }
}
```

### 3. 限制 IP 访问

在 Gitee Webhook 设置中添加 IP 白名单。

---

## 🎯 进阶功能

### 钉钉/企业微信通知

在 `deploy.sh` 末尾添加通知：

```bash
# 钉钉通知
curl -X POST "https://oapi.dingtalk.com/robot/send?access_token=你的token" \
  -H 'Content-Type: application/json' \
  -d '{
    "msgtype": "text",
    "text": {
      "content": "🎉 部署成功！\n项目：dmsyIMS\n时间：'"$(date)"'"
    }
  }'
```

### 添加部署锁定

防止多人同时部署，在 `deploy.sh` 开头添加：

```bash
LOCK_FILE="/tmp/dmsy_deploy.lock"
if [ -f "$LOCK_FILE" ]; then
    echo "部署正在进行中..."
    exit 1
fi
trap "rm -f $LOCK_FILE" EXIT
touch "$LOCK_FILE"
```

---

## 📞 帮助

如有问题，请检查：

1. **Webhook 日志**：`/opt/dmsyIMS/webhook/webhook.log`
2. **应用日志**：`docker-compose logs -f`
3. **服务状态**：`systemctl status dmsy-webhook`

---

**配置完成！每次推送代码，部署自动完成！** 🚀
