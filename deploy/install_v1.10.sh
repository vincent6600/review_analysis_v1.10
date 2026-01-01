#!/bin/bash
# 阿里云部署安装脚本 - v1.10版本
# 使用方法：在服务器上执行 bash install_v1.10.sh

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Shopee竞品评价分析系统 v1.10 - 部署脚本"
echo "=========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 错误：请使用root用户运行此脚本"
    echo "使用方法：sudo bash install_v1.10.sh"
    exit 1
fi

# 设置项目路径（v1.10）
PROJECT_DIR="/opt/review_analysis_v1.10"
CURRENT_DIR=$(pwd)

echo "📋 步骤1：更新系统..."
apt update && apt upgrade -y

echo ""
echo "📋 步骤2：安装基础软件..."
apt install -y python3 python3-pip python3-venv git nginx curl wget vim

echo ""
echo "📋 步骤3：检查项目目录..."
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 错误：项目目录不存在：$PROJECT_DIR"
    echo "请先确保代码已部署到 $PROJECT_DIR"
    echo "可以使用以下命令："
    echo "  cd /opt"
    echo "  git clone https://github.com/你的用户名/review_analysis_v1.10.git"
    exit 1
fi

cd $PROJECT_DIR

echo ""
echo "📋 步骤4：重命名主应用文件（v1.10特有）..."
if [ -f "app_v1.10.py" ] && [ ! -f "app.py" ]; then
    cp app_v1.10.py app.py
    echo "✅ app_v1.10.py已复制为app.py"
elif [ -f "app.py" ]; then
    echo "✅ app.py已存在"
else
    echo "⚠️  警告：找不到app_v1.10.py，请确保文件存在"
fi

echo ""
echo "📋 步骤5：创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境已创建"
else
    echo "✅ 虚拟环境已存在"
fi

echo ""
echo "📋 步骤6：激活虚拟环境并安装依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "📋 步骤7：创建systemd服务..."
if [ -f "deploy/systemd/review-analysis.service" ]; then
    cp deploy/systemd/review-analysis.service /etc/systemd/system/
    # 替换路径（如果不同）
    sed -i "s|/opt/review_analysis_v1.9|$PROJECT_DIR|g" /etc/systemd/system/review-analysis.service
    sed -i "s|app_v1.9:app|app:app|g" /etc/systemd/system/review-analysis.service
    sed -i "s|v1.9|v1.10|g" /etc/systemd/system/review-analysis.service
    echo "✅ systemd服务文件已创建"
else
    # 如果文件不存在，直接创建（v1.10版本，使用app:app）
    cat > /etc/systemd/system/review-analysis.service << EOF
[Unit]
Description=Shopee Review Analysis System v1.10
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 --timeout 120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    echo "✅ systemd服务文件已创建"
fi

systemctl daemon-reload
systemctl enable review-analysis
systemctl start review-analysis

echo ""
echo "📋 步骤8：配置Nginx..."
# 获取服务器IP
SERVER_IP=$(curl -s ifconfig.me)

if [ -f "deploy/nginx/review-analysis.conf" ]; then
    cp deploy/nginx/review-analysis.conf /etc/nginx/sites-available/review-analysis
    # 替换IP地址
    sed -i "s/你的服务器IP/$SERVER_IP/g" /etc/nginx/sites-available/review-analysis
else
    # 如果文件不存在，直接创建
    cat > /etc/nginx/sites-available/review-analysis << EOF
server {
    listen 80;
    server_name $SERVER_IP;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF
fi

ln -sf /etc/nginx/sites-available/review-analysis /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx
systemctl enable nginx

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "📋 服务状态："
systemctl status review-analysis --no-pager | head -3
echo ""
systemctl status nginx --no-pager | head -3
echo ""
echo "🌐 访问地址："
echo "   http://$SERVER_IP"
echo ""
echo "📝 常用命令："
echo "   查看日志：journalctl -u review-analysis -f"
echo "   重启服务：systemctl restart review-analysis"
echo "   查看状态：systemctl status review-analysis"
echo ""
echo "🆕 v1.10新特性："
echo "   - ECharts交互式图表"
echo "   - 更好的用户体验"
echo ""
echo "=========================================="