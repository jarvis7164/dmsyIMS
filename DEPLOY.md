# 大麦摄影管理系统 - 部署指南

## 方案一：Docker 部署（推荐）

### 1. 服务器准备

购买腾讯云轻量应用服务器或 CVM，推荐配置：
- CPU: 2 核
- 内存：2GB
- 系统：TencentOS / Ubuntu 22.04 LTS / CentOS 7+

### 2. 安装 Docker

#### TencentOS 系统（腾讯云默认系统）

```bash
# TencentOS 内置了 Docker，直接安装即可
sudo yum install -y docker

# 启动 Docker
sudo systemctl enable docker
sudo systemctl start docker

# 验证安装
docker --version

# 添加当前用户到 docker 组（避免每次都用 sudo）
sudo usermod -aG docker $USER
# 然后退出重新登录
```

#### Ubuntu/Debian 系统

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl enable docker
sudo systemctl start docker
```

#### CentOS 系统

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker
sudo systemctl start docker
```

### 3. 上传代码

```bash
# 方式 1：使用 git clone
git clone <你的仓库地址> /opt/dmsyIMS
cd /opt/dmsyIMS

# 方式 2：使用 scp 上传
scp -r ./dmsyIMS root@<服务器 IP>:/opt/
```

### 4. 使用 Docker Compose 部署

```bash
# 安装 docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 修改环境变量（重要！）
vi docker-compose.yml
# 将 SECRET_KEY 改为一个随机字符串

# 启动服务
cd /opt/dmsyIMS
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 5. 配置防火墙

在腾讯云控制台配置安全组：
- 开放端口：8080（或你在 docker-compose.yml 中配置的端口）

### 6. 访问系统

```
http://<服务器 IP>:8080
```

---

## 方案二：直接部署（无 Docker）

### 1. 安装 Python 3.10

```bash
# Ubuntu
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip

# CentOS
sudo yum install -y python3 python3-devel gcc
```

### 2. 配置环境

```bash
cd /opt/dmsyIMS

# 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 配置 systemd 服务

```bash
sudo vi /etc/systemd/system/dmsy-ims.service
```

写入以下内容：

```ini
[Unit]
Description=大麦摄影管理系统
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/dmsyIMS
Environment="PATH=/opt/dmsyIMS/venv/bin"
ExecStart=/opt/dmsyIMS/venv/bin/gunicorn -w 4 -b 0.0.0.0:8080 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. 启动服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl enable dmsy-ims
sudo systemctl start dmsy-ims

# 查看状态
sudo systemctl status dmsy-ims

# 查看日志
sudo journalctl -u dmsy-ims -f
```

---

## 方案三：使用宝塔面板（最简单）

### 1. 安装宝塔面板

```bash
# CentOS
yum install -y wget && wget -O install.sh http://download.bt.cn/install/install_6.0.sh && sh install.sh

# Ubuntu/Debian
wget -O install.sh http://download.bt.cn/install/install-ubuntu_6.0.sh && bash install.sh
```

### 2. 在宝塔面板中配置

1. 安装 Python 项目管理器
2. 添加项目，选择 `/opt/dmsyIMS` 目录
3. 启动项目，端口设为 8080
4. 在网站管理中添加反向代理

---

## Nginx 反向代理配置（可选）

如果需要配置域名和 HTTPS：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 安全建议

1. **修改 SECRET_KEY**：在 docker-compose.yml 或环境变量中设置一个随机字符串
2. **配置 HTTPS**：使用腾讯云免费 SSL 证书或 Let's Encrypt
3. **定期备份数据库**：`instance/company_data.db` 文件
4. **限制数据库访问**：确保 SQLite 文件不可通过 Web 访问
5. **创建强密码**：首次登录后立即修改默认密码

---

## 常用命令

```bash
# Docker 方式
docker-compose up -d          # 启动
docker-compose down           # 停止
docker-compose logs -f        # 查看日志
docker-compose restart        # 重启

# 直接部署方式
sudo systemctl restart dmsy-ims    # 重启
sudo systemctl stop dmsy-ims       # 停止
sudo journalctl -u dmsy-ims -f     # 查看日志
```

---

## 数据库备份

```bash
# 备份数据库
cp /opt/dmsyIMS/instance/company_data.db /backup/company_data_$(date +%Y%m%d).db

# 恢复数据库
cp /backup/company_data_20260101.db /opt/dmsyIMS/instance/company_data.db
```
