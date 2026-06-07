# 🚀 CI/CD 自动化部署指南

## 📋 概述

这个 CI/CD 流程实现了：
1. **自动测试** - 每次推送代码时自动运行测试
2. **自动部署** - 代码合并到 `main` 分支后自动部署到腾讯云服务器

## 🔧 配置步骤

### 第一步：在 GitHub 配置 Secrets

1. 进入你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**，添加以下 secrets：

| Name | Value | 说明 |
|------|-------|------|
| `SERVER_HOST` | 你的腾讯云服务器 IP 地址 | 例如：`123.456.789.0` |
| `SERVER_USER` | 服务器用户名 | 例如：`root` 或 `ubuntu` |
| `SSH_PRIVATE_KEY` | SSH 私钥（完整内容） | 见下方"生成 SSH 密钥"步骤 |
| `SERVER_PORT` | SSH 端口（可选） | 默认 `22` |

### 第二步：生成 SSH 密钥（如果还没有）

在你的**本地电脑**执行：

```bash
# 生成 SSH 密钥对（如果还没有）
ssh-keygen -t rsa -b 4096 -C "github-actions@dmsyIMS"

# 查看公钥
cat ~/.ssh/id_rsa.pub
```

**在腾讯云服务器上**：

```bash
# 将公钥添加到服务器的 authorized_keys
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**在 GitHub Secrets 中添加私钥**：

```bash
# 查看私钥内容（完整复制，包括 -----BEGIN 和 -----END）
cat ~/.ssh/id_rsa
```

将完整私钥内容添加到 GitHub Secrets 的 `SSH_PRIVATE_KEY`。

### 第三步：在腾讯云服务器上初始化项目

SSH 登录到你的腾讯云服务器，执行：

```bash
# 1. 安装 Docker 和 Docker Compose（如果还没有）
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 2. 克隆项目到服务器
sudo mkdir -p /opt/dmsyIMS
sudo chown $USER:$USER /opt/dmsyIMS
cd /opt/dmsyIMS
git clone https://github.com/你的用户名/dmsyIMS.git .

# 3. 创建必要的目录
mkdir -p instance logs

# 4. 生成 SECRET_KEY
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env

# 5. 首次启动服务
docker-compose up -d --build

# 6. 检查服务状态
docker-compose ps
docker-compose logs -f
```

### 第四步：推送代码触发部署

现在，每次你推送代码到 `main` 分支，GitHub Actions 会自动：

1. ✅ 运行测试
2. ✅ 通过 SSH 连接到腾讯云服务器
3. ✅ 拉取最新代码
4. ✅ 重新构建并启动 Docker 容器

**测试一下**：

```bash
# 在本地项目目录
git add .
git commit -m "添加 CI/CD 自动化部署"
git push origin main

# 然后进入 GitHub 仓库的 Actions 标签页，查看部署进度
```

## 📊 监控部署

- **查看部署进度**：GitHub 仓库 → **Actions** 标签页
- **查看服务器日志**：
  ```bash
  ssh 你的服务器
  cd /opt/dmsyIMS
  docker-compose logs -f
  ```

## 🔍 故障排查

### 部署失败？

1. **检查 GitHub Actions 日志**：
   - 进入 GitHub 仓库 → **Actions**
   - 点击失败的 workflow run
   - 查看详细错误信息

2. **常见错误**：

   **SSH 连接失败**：
   - 检查 `SERVER_HOST`、`SERVER_USER`、`SSH_PRIVATE_KEY` 是否正确
   - 确保服务器的 SSH 端口（默认 22）已开放
   - 确保私钥格式正确（包含 `-----BEGIN OPENSSH PRIVATE KEY-----`）

   **git pull 失败**：
   - 确保服务器上的项目是通过 `git clone` 克隆的
   - 确保服务器有访问 GitHub 仓库的权限（可以配置 deploy key）

   **Docker 构建失败**：
   - SSH 登录服务器，手动执行 `cd /opt/dmsyIMS && docker-compose up -d --build`
   - 查看详细错误日志

### 手动部署（备用方案）

如果自动部署失败，可以手动部署：

```bash
# SSH 登录服务器
ssh your_server

# 进入项目目录
cd /opt/dmsyIMS

# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose down
docker-compose up -d --build

# 检查状态
docker-compose ps
docker-compose logs -f
```

## 🎯 进阶配置（可选）

### 1. 添加钉钉/企业微信通知

在 `.github/workflows/deploy.yml` 中添加通知步骤：

```yaml
- name: 发送钉钉通知
  if: always()
  uses: zcong1993/action-ding@v1.0.0
  with:
    dingtalk-access-token: ${{ secrets.DINGTALK_TOKEN }}
    body: |
      {
        "msgtype": "markdown",
        "markdown": {
          "title": "部署通知",
          "text": "## 部署通知\n- 项目：dmsyIMS\n- 状态：${{ job.status }}\n- 分支：${{ github.ref }}"
        }
      }
```

### 2. 使用 Docker Hub 镜像（推荐生产环境）

构建 Docker 镜像并推送到 Docker Hub，服务器直接拉取镜像：

```yaml
- name: 登录 Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}

- name: 构建并推送镜像
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ${{ secrets.DOCKER_USERNAME }}/dmsyims:latest
```

然后在服务器上修改 `docker-compose.yml`，使用镜像而不是构建。

### 3. 添加健康检查

在 `docker-compose.yml` 中添加健康检查：

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/login"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

在 GitHub Actions 中添加健康检查步骤。

## 📝 总结

完成以上配置后，你的 CI/CD 流程就是：

```
本地代码 → git push → GitHub Actions → 自动测试 → 自动部署到腾讯云服务器
```

**每次修改代码，只需要 `git push`，部署自动完成！** 🎉

---

如有任何问题，请查看：
- GitHub Actions 日志
- 服务器 Docker 日志：`docker-compose logs -f`
