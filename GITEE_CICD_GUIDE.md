# 🚀 Gitee CI/CD 自动化部署指南

## 📋 概述

本指南帮助你配置 **Gitee（码云）+ 腾讯云服务器** 的 CI/CD 自动化部署。

**工作流程**：
```
本地代码 → git push → Gitee Go 流水线 → 自动测试 → 自动部署到腾讯云服务器
```

---

## 🔧 配置步骤

### 第一步：创建 Gitee 仓库

1. 访问 [Gitee](https://gitee.com)，登录你的账号
2. 点击右上角 **+** → **新建仓库**
3. 填写仓库信息：
   - 仓库名称：`dmsyIMS`
   - 路径：`你的用户名/dmsyIMS`
   - 勾选"使用 README 文件初始化仓库"
4. 点击 **创建**

### 第二步：上传代码到 Gitee

```bash
# 进入项目目录
cd D:\pythonProject\python\dmsyIMS

# 初始化 Git 仓库（如果还没有）
git init

# 添加远程仓库
git remote add origin https://gitee.com/你的用户名/dmsyIMS.git

# 添加所有文件
git add .

# 提交代码
git commit -m "初始提交"

# 推送到 Gitee
git push -u origin main
```

### 第三步：在 Gitee 配置流水线变量

1. 进入你的 Gitee 仓库
2. 点击左侧菜单 **流水线** → **流水线管理**
3. 点击 **变量配置**
4. 添加以下变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `SERVER_HOST` | 你的腾讯云服务器 IP | 例如：`123.456.789.0` |
| `SERVER_USER` | 服务器用户名 | 例如：`root` |
| `SERVER_PORT` | SSH 端口 | 默认 `22` |
| `SSH_PRIVATE_KEY` | SSH 私钥 | 见下方"生成 SSH 密钥" |

### 第四步：生成并配置 SSH 密钥

**在本地电脑生成密钥对**：

```bash
# 生成 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "gitee-actions@dmsyIMS"

# 查看私钥（完整复制）
cat ~/.ssh/id_rsa
```

**在腾讯云服务器上添加公钥**：

```bash
# 查看公钥
cat ~/.ssh/id_rsa.pub

# 将公钥添加到 authorized_keys
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**在 Gitee 流水线变量中添加私钥**：

将私钥完整内容添加到 `SSH_PRIVATE_KEY` 变量。

### 第五步：在服务器上初始化项目

SSH 登录到腾讯云服务器，执行：

```bash
# 1. 安装 Docker（如果没有）
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 2. 创建项目目录
sudo mkdir -p /opt/dmsyIMS
sudo chown $USER:$USER /opt/dmsyIMS

# 3. 克隆 Gitee 仓库到服务器
cd /opt/dmsyIMS
git clone https://gitee.com/你的用户名/dmsyIMS.git .

# 4. 创建必要目录
mkdir -p instance logs

# 5. 生成 SECRET_KEY
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env

# 6. 首次启动
docker-compose up -d --build

# 7. 检查状态
docker-compose ps
```

### 第六步：在 Gitee 创建流水线

1. 进入仓库 → **流水线**
2. 点击 **创建流水线**
3. 选择 **Gitee Go 流水线**
4. 配置文件选择 **gitee-pipeline.yml**
5. 点击 **创建**

### 第七步：测试自动化部署

```bash
# 在本地修改代码
git add .
git commit -m "测试 CI/CD"
git push origin main

# 在 Gitee 查看流水线执行
# 仓库 → 流水线 → 查看执行状态
```

---

## 📊 流水线执行流程

当代码推送到 `main` 分支时，流水线自动执行：

```
1️⃣  代码测试 (test)
    ↓
    - 检出代码
    - 安装 Python 依赖
    - 运行测试

2️⃣  部署到服务器 (deploy)
    ↓
    - 检出代码
    - SSH 连接到腾讯云服务器
    - 拉取最新代码
    - 重新构建并启动 Docker 容器
    - 检查服务状态
```

---

## 🔍 监控与故障排查

### 查看流水线执行状态

1. 进入 Gitee 仓库
2. 点击 **流水线**
3. 查看所有流水线运行记录

### 查看服务器日志

```bash
ssh 你的服务器
cd /opt/dmsyIMS
docker-compose logs -f
```

### 常见问题

#### 1. SSH 连接失败
- ✅ 检查 `SERVER_HOST`、`SERVER_USER`、`SSH_PRIVATE_KEY` 是否正确
- ✅ 确保服务器 SSH 端口（默认 22）已开放
- ✅ 确保私钥格式正确

#### 2. 权限不足
```bash
# 在服务器上给用户添加 Docker 权限
sudo usermod -aG docker $USER
# 重新登录服务器
```

#### 3. 端口冲突
确保腾讯云安全组已开放 **8080** 端口：
- 登录腾讯云控制台
- 进入云服务器 → 安全组
- 添加规则：TCP 8080 端口

---

## 🎯 进阶配置（可选）

### 添加钉钉通知

1. 在 Gitee 流水线配置中启用通知
2. 配置钉钉机器人 Webhook

### 使用镜像加速

在 `docker-compose.yml` 中使用国内镜像加速：

```yaml
services:
  dmsy-ims:
    build:
      context: .
      cache_from:
        - registry.cn-shanghai.aliyuncs.com/你的镜像仓库/dmsyims:latest
    image: registry.cn-shanghai.aliyuncs.com/你的镜像仓库/dmsyims:latest
```

---

## 📝 总结

完成配置后，你的部署流程就是：

```
修改代码
    ↓
git push gitee main
    ↓
Gitee Go 流水线自动执行
    ↓
自动部署到腾讯云服务器
    ↓
访问 http://服务器IP:8080
```

---

## 📚 相关资源

- [Gitee Go 官方文档](https://gitee.com/help/articles/4339)
- [Docker 官方文档](https://docs.docker.com/)
- [腾讯云服务器文档](https://cloud.tencent.com/document/product/213)

---

如有问题，随时告诉我！😊
