"""
Flask主应用 - v1.10版本
Shopee竞品评价分析系统Web应用入口
v1.10更新：
1. 切换到ECharts交互式图表方案（简约商务风格）
   - 替换Plotly为ECharts，解决交互体验差的问题
   - 简约商务配色方案（参考v1.9风格）
   - 优化悬停效果：显示完整数值，无多余动画
   - 使用pyecharts生成ECharts配置
   - 前端使用ECharts.js渲染交互式图表
2. UI现代化改进（卡片式设计、动画效果、现代化配色）
3. 优化图表交互体验（简约商务风格）
   - 禁用多余动画，显示完整数值
   - 简约配色：主蓝色#1890ff，灰色系辅助色
   - 优化工具提示样式（白色背景、灰色边框）
4. 添加ECharts.js CDN支持
5. 改进按钮和卡片样式（渐变效果、悬停动画）
优化历史：
1. 统一文件上传和分析报告栏高度
2. 简约风格，移除渐变色
3. 热销变体显示图片（缩略图，限定显示区域）
4. 图表左右布局优化
5. 平滑曲线，固定纵轴
6. 变体表格字段调整
7. 增加带文字评论维度
8. HTML报告保存功能
9. 星级分布改为漏斗图
10. 变体表格支持图片预览
11. 媒体分析合并显示
12. 媒体覆盖率饼图包含文字评论
13. 修复有效评论中的星级分布（只统计有效评论）
14. 修复变体价格取值（按时间取最新价格）
15. 修复图片链接处理（多个链接只取第一个）
16. 修复各变体平均星级图表排序（高的在上面）
17. 修复漏斗图排序（按星级顺序，不按数量）
18. 修复图表显示问题（确保matplotlib图表正确显示）
19. 修复热销变体图片显示（缩略图样式）
20. 改进变体评论数量时间趋势图表（更清晰的图例）
21. 修复变体价格显示（确保不显示变体名称，简化获取逻辑）
22. 修改各变体平均星级图表横轴限制（3-5.5，固定坐标轴区间）
23. 移除表格排序功能（v1.8放弃此功能）
24. 修复变体价格获取问题（v1.9修复列映射逻辑，确保正确提取价格）
"""

from flask import Flask, send_from_directory
from pathlib import Path
import os

# 导入API路由
from backend.api.routes import create_routes

# 创建Flask应用
app = Flask(__name__, 
            static_folder='frontend',
            template_folder='frontend')

# 配置
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB文件大小限制
app.config['UPLOAD_FOLDER'] = None  # 不使用文件上传，所有处理在内存中

# 注册路由
create_routes(app)


@app.route('/')
def index():
    """首页"""
    frontend_path = Path(__file__).parent / 'frontend' / 'index.html'
    if frontend_path.exists():
        with open(frontend_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "前端文件未找到", 404


@app.route('/<path:path>')
def serve_static(path):
    """提供静态文件服务"""
    frontend_dir = Path(__file__).parent / 'frontend'
    file_path = frontend_dir / path
    
    if file_path.exists() and file_path.is_file():
        return send_from_directory(str(frontend_dir), path)
    
    return "文件未找到", 404


if __name__ == '__main__':
    # 开发模式运行
    import socket
    
    # 检查端口是否被占用，如果被占用则使用其他端口
    def find_free_port(start_port=5000):
        for port in range(start_port, start_port + 10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        return start_port
    
    port = find_free_port(5000)
    
    print("=" * 60)
    print("Shopee竞品评价分析系统 v1.10")
    print("=" * 60)
    print("✨ 新功能：Plotly交互式图表 + 现代化UI设计")
    print("=" * 60)
    print("服务器启动中...")
    print(f"访问地址: http://localhost:{port}")
    print(f"访问地址: http://127.0.0.1:{port}")
    if port != 5000:
        print(f"注意: 端口5000被占用，已自动切换到端口{port}")
    print("=" * 60)
    print("提示: 如果无法访问，请使用 http://127.0.0.1:{port}")
    print("=" * 60)
    
    # 禁用自动重载，避免端口混乱
    app.run(debug=True, host='127.0.0.1', port=port, use_reloader=False)
