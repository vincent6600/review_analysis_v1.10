# 部署配置文件

本目录包含阿里云部署所需的配置文件。

## 文件说明

### systemd/review-analysis.service
- systemd服务配置文件
- 用于让应用在后台运行，服务器重启后自动启动

**使用方法**：
```bash
# 复制到系统目录
cp deploy/systemd/review-analysis.service /etc/systemd/system/

# 重新加载配置
systemctl daemon-reload

# 启动服务
systemctl start review-analysis

# 设置开机自启
systemctl enable review-analysis
```

### nginx/review-analysis.conf
- Nginx反向代理配置文件
- 用于将外部请求转发到Flask应用

**使用方法**：
```bash
# 复制到Nginx配置目录（记得替换IP地址）
cp deploy/nginx/review-analysis.conf /etc/nginx/sites-available/review-analysis

# 编辑文件，替换"你的服务器IP"为实际IP
vim /etc/nginx/sites-available/review-analysis

# 启用配置
ln -s /etc/nginx/sites-available/review-analysis /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试配置
nginx -t

# 重启Nginx
systemctl restart nginx
```

## 注意事项

1. **替换IP地址**：在nginx配置文件中，记得将`你的服务器IP`替换为实际IP
2. **路径检查**：确保配置文件中的路径（`/opt/review_analysis_v1.10`）与实际部署路径一致
3. **权限**：确保服务文件有正确的权限

## 详细部署步骤

请参考：
- `ALIYUN_DEPLOYMENT_GUIDE_v1.10.md` - 完整部署指南（小白版）
- `ALIYUN_DEPLOYMENT_STEPS_v1.10.md` - 快速步骤指南
