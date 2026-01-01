# 阿里云部署快速步骤 - v1.10

## 🎯 部署后你会得到什么？

✅ **一个稳定的网页**，可以通过互联网访问  
✅ **功能完全一样**：上传Excel文件 → 点击执行分析 → 查看报告  
✅ **24小时运行**，不需要你的电脑开着  
✅ **同事可以随时访问**，通过网址使用  
✅ **v1.10新特性**：ECharts交互式图表，更好的用户体验

---

## 📋 快速步骤（30-40分钟）

### 第一步：购买服务器（5分钟）

1. 访问：https://www.aliyun.com
2. 登录/注册账号
3. 进入控制台 → **轻量应用服务器**
4. 点击 **创建服务器**
5. 选择：
   - **地域**：华东1（杭州）
   - **镜像**：Ubuntu 22.04
   - **套餐**：2核2G（约24元/月）
6. 设置密码（**一定要记住！**）
7. 购买并支付
8. **记录**：IP地址、用户名（root）、密码

### 第二步：配置防火墙（2分钟）

1. 服务器详情页 → **防火墙**标签
2. 添加规则：
   - 端口`80`，协议`TCP`，源`0.0.0.0/0`
   - 端口`443`，协议`TCP`，源`0.0.0.0/0`（可选）
   - 端口`5000`，协议`TCP`，源`0.0.0.0/0`

### 第三步：连接服务器（2分钟）

在Mac终端执行：

```bash
# 替换为你的服务器IP
ssh root@你的服务器IP

# 首次连接输入 yes
# 然后输入密码（输入时不显示，直接输入后按回车）
```

**连接成功标志**：看到`root@xxx:~#`

### 第四步：安装环境（10分钟）

在服务器上执行（**一条一条执行**）：

```bash
# 1. 更新系统
apt update && apt upgrade -y

# 2. 安装软件
apt install -y python3 python3-pip python3-venv git nginx curl wget vim

# 3. 进入/opt目录
cd /opt

# 4. 从GitHub拉取代码（替换为你的仓库地址）
git clone https://github.com/你的用户名/review_analysis_v1.10.git

# 5. 进入项目目录
cd review_analysis_v1.10

# 6. 重命名主应用文件（v1.10特有）
cp app_v1.10.py app.py

# 7. 创建虚拟环境
python3 -m venv venv

# 8. 激活虚拟环境
source venv/bin/activate

# 9. 升级pip
pip install --upgrade pip

# 10. 安装依赖（需要5-10分钟，包括pyecharts）
pip install -r requirements.txt
```

### 第五步：配置运行（5分钟）

#### 5.1 创建服务文件

```bash
cat > /etc/systemd/system/review-analysis.service << 'EOF'
[Unit]
Description=Shopee Review Analysis System v1.10
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/review_analysis_v1.10
Environment="PATH=/opt/review_analysis_v1.10/venv/bin"
ExecStart=/opt/review_analysis_v1.10/venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 --timeout 120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

#### 5.2 启动服务

```bash
# 重新加载配置
systemctl daemon-reload

# 启动服务
systemctl start review-analysis

# 设置开机自启
systemctl enable review-analysis

# 查看状态（应该看到active (running)）
systemctl status review-analysis
```

#### 5.3 配置Nginx

**先获取你的服务器IP**：
```bash
curl ifconfig.me
```

复制显示的IP，然后执行（**替换IP**）：

```bash
cat > /etc/nginx/sites-available/review-analysis << EOF
server {
    listen 80;
    server_name $(curl -s ifconfig.me);

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

# 启用配置
ln -s /etc/nginx/sites-available/review-analysis /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试配置
nginx -t

# 重启Nginx
systemctl restart nginx
systemctl enable nginx
```

### 第六步：验证（2分钟）

1. **检查服务**
   ```bash
   systemctl status review-analysis
   systemctl status nginx
   ```
   都应该显示`active (running)`

2. **在浏览器访问**
   - 打开浏览器
   - 输入：`http://你的服务器IP`
   - 应该能看到文件上传界面

3. **测试功能**
   - 上传Excel文件
   - 点击"执行分析"
   - 检查是否能生成报告
   - **v1.10新特性**：测试图表交互（鼠标悬停、缩放等）

---

## ✅ 完成！

部署成功后，你的同事可以通过以下方式访问：

```
http://你的服务器IP
```

例如：
```
http://47.123.45.67
```

---

## 🔧 常用命令

### 查看日志
```bash
journalctl -u review-analysis -f
```

### 重启服务
```bash
systemctl restart review-analysis
```

### 更新代码
```bash
cd /opt/review_analysis_v1.10
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl restart review-analysis
```

---

## 🆕 v1.10特有说明

### 主要变化：

1. **新增依赖**：`pyecharts>=2.0.0`（已包含在requirements.txt中）
2. **主应用文件**：使用`app.py`（需要从app_v1.10.py复制）
3. **systemd配置**：使用`app:app`（不是app_v1.10:app）
4. **前端**：自动从CDN加载ECharts.js

### 关键步骤：

- ✅ 步骤4.6：复制app_v1.10.py为app.py
- ✅ 步骤5.1：systemd服务使用`app:app`
- ✅ 步骤4.10：安装依赖时会自动安装pyecharts

---

## ⚠️ 遇到问题？

1. 查看详细指南：`ALIYUN_DEPLOYMENT_GUIDE_v1.10.md`
2. 查看日志：`journalctl -u review-analysis -f`
3. 检查服务状态：`systemctl status review-analysis`

---

**详细说明**：查看 `ALIYUN_DEPLOYMENT_GUIDE_v1.10.md`（包含每一步的详细解释）
