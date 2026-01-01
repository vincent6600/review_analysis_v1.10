"""
HTML报告生成模块
生成简洁现代的HTML分析报告
"""

from typing import Dict, Any
from datetime import datetime
from pathlib import Path


def generate_html_report(analysis_results: Dict[str, Any], file_info: Dict[str, Any]) -> str:
    """
    生成HTML报告
    
    Args:
        analysis_results: 分析结果字典，包含rating, trend, variant, media等
        file_info: 文件信息字典，包含site, product_id等
        
    Returns:
        HTML报告字符串
    """
    rating_data = analysis_results.get('rating', {})
    trend_data = analysis_results.get('trend', {})
    variant_data = analysis_results.get('variant', {})
    media_data = analysis_results.get('media', {})
    charts = analysis_results.get('charts', {})
    
    # 报告标题
    site = file_info.get('site', '未知站点')
    product_id = file_info.get('product_id', '未知')
    report_title = f"{site} - 产品ID: {product_id} - 评价分析报告"
    
    # 生成时间
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html = f"""
<div class="report-wrapper">
    <style>
        .report-wrapper {{
            width: 100%;
            min-height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', 'SimHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        
        .report-wrapper * {{
            box-sizing: border-box;
        }}
        
        .report-wrapper .report-container {{
            width: 100%;
            background-color: #fff;
            padding: 40px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            color: #7f8c8d;
            font-size: 14px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 22px;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: #e6f7ff;  /* 浅蓝色背景（高对比度方案） */
            color: #0050b3;  /* 深蓝色文字，确保高对比度 */
            padding: 20px;
            border-radius: 4px;  /* 简约圆角 */
            text-align: center;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);  /* 简约阴影 */
            border: 1px solid #91d5ff;  /* 添加边框增强视觉 */
        }}
        
        .stat-card.blue {{
            background: #e6f7ff;  /* 浅蓝色背景 */
            color: #0050b3;  /* 深蓝色文字 */
            border: 1px solid #91d5ff;
        }}
        
        .stat-card.green {{
            background: #f6ffed;  /* 浅绿色背景 */
            color: #389e0d;  /* 深绿色文字 */
            border: 1px solid #b7eb8f;
        }}
        
        .stat-card.orange {{
            background: #fff7e6;  /* 浅橙色背景 */
            color: #d46b08;  /* 深橙色文字 */
            border: 1px solid #ffd591;
        }}
        
        .stat-card.purple {{
            background: #f9f0ff;  /* 浅紫色背景 */
            color: #531dab;  /* 深紫色文字 */
            border: 1px solid #d3adf7;
        }}
        
        .top-variant-card {{
            position: relative;
        }}
        
        .top-variant-image {{
            margin-top: 10px;
        }}
        
        .top-variant-image img {{
            max-width: 100px;
            max-height: 100px;
            border-radius: 4px;
            object-fit: cover;
        }}
        
        .chart-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 30px 0;
        }}
        
        .chart-row .chart-container {{
            margin: 0;
        }}
        
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 14px;
            opacity: 1.0;  /* 完全不透明，确保清晰可见 */
            font-weight: 500;  /* 增加字重，提高可读性 */
            color: inherit;  /* 继承父元素颜色 */
        }}
        
        .chart-container {{
            margin: 30px 0;
            text-align: center;
            background-color: #ffffff;  /* 简约白色背景 */
            padding: 20px;
            border-radius: 4px;  /* 简约圆角 */
            border: 1px solid #f0f0f0;  /* 简约边框 */
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        
        .chart-title {{
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #2c3e50;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: #fff;
        }}
        
        .data-table th,
        .data-table td {{
            padding: 4px 12px;  /* 缩短行高一半：从8px改为4px */
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
            line-height: 1.3;  /* 进一步缩短行高 */
        }}
        
        .data-table th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .data-table tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #7f8c8d;
            font-size: 12px;
        }}
        
        .warning {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .warning-text {{
            color: #856404;
        }}
    </style>
    <div class="report-container">
        <div class="header">
            <h1>{report_title}</h1>
            <div class="meta">
                生成时间: {current_time} | 数据来源: Shopee平台
            </div>
        </div>
        
        <div class="warning">
            <div class="warning-text">
                <strong>提示：</strong>本报告数据不保留历史记录，请及时下载保存。
            </div>
        </div>
        
        <!-- 整体评分分析 -->
        <div class="section">
            <h2 class="section-title">一、整体评分分析</h2>
            
            <div class="stats-grid">
                <div class="stat-card blue">
                    <div class="stat-value">{rating_data.get('total_reviews', 0)}</div>
                    <div class="stat-label">总评论数</div>
                </div>
                <div class="stat-card green">
                    <div class="stat-value">{rating_data.get('valid_reviews', 0)}</div>
                    <div class="stat-label">有效评论数</div>
                </div>
                <div class="stat-card orange">
                    <div class="stat-value">{rating_data.get('valid_reviews_ratio', 0)}%</div>
                    <div class="stat-label">有效评论比例</div>
                </div>
                <div class="stat-card purple">
                    <div class="stat-value">{rating_data.get('average_rating', 0)}</div>
                    <div class="stat-label">平均星级</div>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card blue">
                    <div class="stat-value">{rating_data.get('positive_rate', 0)}%</div>
                    <div class="stat-label">好评率 (4-5星)</div>
                </div>
                <div class="stat-card green top-variant-card" style="position: relative; padding: 20px;">
                    {f'<div style="position: absolute; left: 15px; top: 50%; transform: translateY(-50%); width: 60px; height: 60px; overflow: hidden; border-radius: 4px; background: #f0f0f0; border: 2px solid rgba(255,255,255,0.3);"><img src="{rating_data.get("top_variant_image")}" alt="热销变体图片" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display=\'none\'"></div>' if rating_data.get('top_variant_image') else ''}
                    <div style="margin-left: {85 if rating_data.get('top_variant_image') else 0}px;">
                        <div class="stat-value">{rating_data.get('top_variant', 'N/A')}</div>
                        <div class="stat-label">热销变体</div>
                    </div>
                </div>
            </div>
            
            <div class="chart-row">
                {_generate_rating_charts(charts)}
            </div>
        </div>
        
        <!-- 时间趋势分析 -->
        <div class="section">
            <h2 class="section-title">二、时间趋势分析</h2>
            {_generate_trend_charts(charts)}
        </div>
        
        <!-- 变体分析 -->
        <div class="section">
            <h2 class="section-title">三、变体分析</h2>
            {_generate_variant_section(variant_data, charts)}
        </div>
        
        <!-- 媒体内容分析 -->
        <div class="section">
            <h2 class="section-title">四、媒体内容分析</h2>
            
            <div class="stats-grid">
                <div class="stat-card blue">
                    <div class="stat-value">{media_data.get('with_text', 0)}</div>
                    <div class="stat-label">带文字评论 ({media_data.get('with_text_ratio', 0)}%)</div>
                </div>
                <div class="stat-card orange">
                    <div class="stat-value">{media_data.get('with_image', 0)}</div>
                    <div class="stat-label">带图片评论 ({media_data.get('with_image_ratio', 0)}%)</div>
                </div>
                <div class="stat-card purple">
                    <div class="stat-value">{media_data.get('with_video', 0)}</div>
                    <div class="stat-label">带视频评论 ({media_data.get('with_video_ratio', 0)}%)</div>
                </div>
            </div>
            
            {_generate_media_charts(charts)}
        </div>
        
        <div class="footer">
            <p>Shopee竞品评价分析系统 v1.5</p>
            <p>报告生成时间: {current_time}</p>
        </div>
    </div>
</div>
"""
    
    return html


def _generate_rating_charts(charts: Dict[str, Any]) -> str:
    """生成评分相关图表HTML（左右布局，支持ECharts交互式图表，v1.10切换到ECharts）"""
    html = ""
    
    # 导入ECharts图表生成函数
    from backend.chart.chart_generator import generate_echarts_chart_html
    
    if 'valid_reviews_pie' in charts:
        chart_data = charts['valid_reviews_pie']
        html += """
        <div class="chart-container">
            <div class="chart-title">有效评论数占比</div>
        """
        # 判断是ECharts图表配置（字典）还是matplotlib图片（字符串）
        if isinstance(chart_data, dict) and chart_data:
            echarts_html = generate_echarts_chart_html(chart_data)
            if echarts_html:
                html += echarts_html
            else:
                # ECharts生成失败，显示提示
                html += '<div style="color: #999; padding: 20px;">图表数据格式错误</div>'
        elif isinstance(chart_data, str) and chart_data:
            # matplotlib生成的base64图片
            html += f'<img src="data:image/png;base64,{chart_data}" alt="有效评论数占比">'
        else:
            html += '<div style="color: #999; padding: 20px;">暂无数据</div>'
        html += "</div>"
    
    if 'rating_distribution_funnel' in charts:
        chart_data = charts['rating_distribution_funnel']
        html += """
        <div class="chart-container">
            <div class="chart-title">有效评论中的星级分布</div>
        """
        # 判断是ECharts图表配置（字典）还是matplotlib图片（字符串）
        if isinstance(chart_data, dict) and chart_data:
            echarts_html = generate_echarts_chart_html(chart_data)
            if echarts_html:
                html += echarts_html
            else:
                # ECharts生成失败，降级为matplotlib（需要重新生成）
                html += '<div style="color: #999;">图表加载中...</div>'
        elif chart_data:
            html += f'<img src="data:image/png;base64,{chart_data}" alt="星级分布">'
        else:
            html += '<div style="color: #999;">暂无数据</div>'
        html += "</div>"
    
    return html


def _generate_trend_charts(charts: Dict[str, Any]) -> str:
    """生成趋势相关图表HTML（支持ECharts交互式图表，v1.10切换到ECharts）"""
    html = ""
    
    # 导入ECharts图表生成函数
    from backend.chart.chart_generator import generate_echarts_chart_html
    
    # 1. 变体评论数量时间趋势（放在上面，单独一行）
    if 'variant_trend_area' in charts:
        chart_data = charts['variant_trend_area']
        html += """
        <div class="chart-container">
            <div class="chart-title">变体评论数量时间趋势</div>
        """
        if isinstance(chart_data, dict) and chart_data:
            echarts_html = generate_echarts_chart_html(chart_data)
            if echarts_html:
                html += echarts_html
            else:
                html += '<div style="color: #999;">图表加载中...</div>'
        elif chart_data:
            html += f'<img src="data:image/png;base64,{chart_data}" alt="变体评论数量时间趋势">'
        else:
            html += '<div style="color: #999;">暂无数据</div>'
        html += "</div>"
    
    # 2. 评论数量时间趋势和平均星级时间趋势（放在同一行，分左右列展示）
    html += """
    <div class="chart-row">
    """
    
    # 2.1 评论数量时间趋势（左侧）
    if 'monthly_reviews_bar' in charts:
        chart_data = charts['monthly_reviews_bar']
        html += """
        <div class="chart-container">
            <div class="chart-title">评论数量时间趋势</div>
        """
        if isinstance(chart_data, dict) and chart_data:
            echarts_html = generate_echarts_chart_html(chart_data)
            if echarts_html:
                html += echarts_html
            else:
                html += '<div style="color: #999; padding: 20px;">图表数据格式错误</div>'
        elif isinstance(chart_data, str) and chart_data:
            html += f'<img src="data:image/png;base64,{chart_data}" alt="评论数量时间趋势">'
        else:
            html += '<div style="color: #999; padding: 20px;">暂无数据</div>'
        html += "</div>"
    
    # 2.2 平均星级时间趋势（右侧）
    if 'rating_trend_line' in charts:
        chart_data = charts['rating_trend_line']
        html += """
        <div class="chart-container">
            <div class="chart-title">平均星级时间趋势</div>
        """
        if isinstance(chart_data, dict) and chart_data:
            echarts_html = generate_echarts_chart_html(chart_data)
            if echarts_html:
                html += echarts_html
            else:
                html += '<div style="color: #999; padding: 20px;">图表数据格式错误</div>'
        elif isinstance(chart_data, str) and chart_data:
            html += f'<img src="data:image/png;base64,{chart_data}" alt="平均星级时间趋势">'
        else:
            html += '<div style="color: #999; padding: 20px;">暂无数据</div>'
        html += "</div>"
    
    html += """
    </div>
    """
    
    return html


def _generate_variant_section(variant_data: Dict[str, Any], charts: Dict[str, str]) -> str:
    """生成变体分析部分HTML"""
    html = ""
    
    variant_stats = variant_data.get('variant_stats', {})
    
    # 变体图表（支持ECharts交互式图表，v1.10切换到ECharts）
    # 调整图表顺序：各变体评论、变体价格-评论数关系、各变体平均星级、变体明细表
    from backend.chart.chart_generator import generate_echarts_chart_html
    
    # 1. 各变体评论（雷达图）和各变体平均星级（横向柱状图）放在同一行，分左右列展示
    html += """
    <div class="chart-row">
    """
    
    # 1.1 各变体评论（雷达图，左侧）
    if 'variant_radar' in charts:
        chart_data = charts['variant_radar']
        html += """
        <div class="chart-container">
            <div class="chart-title">各变体评论</div>
        """
        if isinstance(chart_data, dict):
            html += generate_echarts_chart_html(chart_data)
        else:
            html += f'<img src="data:image/png;base64,{chart_data}" alt="各变体评论数量">'
        html += "</div>"
    
    # 1.2 各变体平均星级（横向柱状图，右侧）
    if 'variant_rating_bar' in charts:
        chart_data = charts['variant_rating_bar']
        html += """
        <div class="chart-container">
            <div class="chart-title">各变体平均星级</div>
        """
        if isinstance(chart_data, dict) and chart_data:
            echarts_html = generate_echarts_chart_html(chart_data)
            if echarts_html:
                html += echarts_html
            else:
                html += '<div style="color: #999; padding: 20px;">图表数据格式错误</div>'
        elif isinstance(chart_data, str) and chart_data:
            html += f'<img src="data:image/png;base64,{chart_data}" alt="各变体平均星级">'
        else:
            html += '<div style="color: #999; padding: 20px;">暂无数据</div>'
        html += "</div>"
    
    html += """
    </div>
    """
    
    # 2. 变体价格-评论数关系（散点图）
    if 'price_sales_bubble' in charts:
        chart_data = charts['price_sales_bubble']
        html += """
        <div class="chart-container">
            <div class="chart-title">变体价格-评论数关系</div>
        """
        if isinstance(chart_data, dict):
            html += generate_echarts_chart_html(chart_data)
        else:
            html += f'<img src="data:image/png;base64,{chart_data}" alt="价格-销量关系">'
        html += "</div>"
    
    # 3. 各变体平均星级（已移到上面，与雷达图同一行）
    
    # 4. 变体统计表格（列顺序：变体图片、变体名称、变体价格、评论数量、平均评分）
    if variant_stats:
        html += """
        <style>
            .variant-table-wrapper {
                position: relative;
                overflow-x: auto;
            }
            .variant-image-thumb {
                max-width: 60px;
                max-height: 60px;
                object-fit: cover;
                border-radius: 4px;
                cursor: pointer;
                transition: transform 0.2s;
            }
            .variant-image-thumb:hover {
                transform: scale(1.1);
            }
            .image-modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.9);
                cursor: pointer;
            }
            .image-modal-content {
                margin: auto;
                display: block;
                width: 90%;
                max-width: 800px;
                margin-top: 5%;
            }
            .image-modal-close {
                position: absolute;
                top: 15px;
                right: 35px;
                color: #f1f1f1;
                font-size: 40px;
                font-weight: bold;
                cursor: pointer;
            }
            .sortable {{
                cursor: pointer;
                user-select: none;
                position: relative;
                padding: 8px 12px !important;  /* 确保与td一致 */
            }}
            .sortable:hover {{
                background-color: #f5f5f5;
            }}
            .sort-indicator {{
                font-size: 12px;
                color: #999;
                margin-left: 5px;
                display: inline-block;
            }}
            .sortable.asc .sort-indicator::after {{
                content: ' ↑';
                color: #1890ff;
                font-weight: bold;
            }}
            .sortable.desc .sort-indicator::after {{
                content: ' ↓';
                color: #1890ff;
                font-weight: bold;
            }}
        </style>
        <div class="variant-table-wrapper">
            <!-- 去除搜索框，直接显示表格 -->
            <table class="data-table" id="variantTable">
                <thead>
                    <tr>
                        <th>变体图片</th>
                        <th class="sortable" data-sort="name" data-column="1" onclick="sortTableByHeader(this, 'text')">变体名称 <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="price" data-column="2" onclick="sortTableByHeader(this, 'number')">变体价格 <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="count" data-column="3" onclick="sortTableByHeader(this, 'number')">评论数量 <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="rating" data-column="4" onclick="sortTableByHeader(this, 'number')">平均评分 <span class="sort-indicator">↕</span></th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # 按评论数量排序（默认从高到低）
        sorted_variants = sorted(
            variant_stats.items(),
            key=lambda x: x[1].get('count', 0),
            reverse=True
        )
        
        for variant, stats in sorted_variants[:20]:  # 显示前20个
            image_url = stats.get('image_url', '')
            if image_url:
                image_html = f'<img src="{image_url}" alt="{variant}" class="variant-image-thumb" onclick="showImageModal(this.src)" onmouseover="showImagePreview(this, event)" onmouseout="hideImagePreview()">'
            else:
                image_html = '<span style="color: #999;">无图片</span>'
            html += f"""
            <tr>
                <td style="text-align: center;">{image_html}</td>
                <td>{variant}</td>
                <td>{stats.get('price', 'N/A')}</td>
                <td>{stats.get('count', 0)}</td>
                <td>{stats.get('average_rating', 0)}</td>
            </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        <div id="imageModal" class="image-modal" onclick="closeImageModal()">
            <span class="image-modal-close">&times;</span>
            <img class="image-modal-content" id="modalImage">
        </div>
        <script>
            // 图片模态框
            function showImageModal(src) {
                const modal = document.getElementById('imageModal');
                const modalImg = document.getElementById('modalImage');
                modal.style.display = 'block';
                modalImg.src = src;
            }
            function closeImageModal() {
                document.getElementById('imageModal').style.display = 'none';
            }
            
            // 图片悬停预览
            let previewTimeout;
            function showImagePreview(img, event) {
                clearTimeout(previewTimeout);
                const preview = document.createElement('div');
                preview.id = 'imagePreview';
                preview.style.cssText = 'position: fixed; z-index: 999; border: 2px solid #333; background: white; padding: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); pointer-events: none;';
                const previewImg = document.createElement('img');
                previewImg.src = img.src;
                previewImg.style.cssText = 'max-width: 300px; max-height: 300px; display: block;';
                preview.appendChild(previewImg);
                document.body.appendChild(preview);
                preview.style.left = (event.clientX + 20) + 'px';
                preview.style.top = (event.clientY + 20) + 'px';
            }
            function hideImagePreview() {
                previewTimeout = setTimeout(() => {
                    const preview = document.getElementById('imagePreview');
                    if (preview) preview.remove();
                }, 200);
            }
            
            // Excel式表格排序功能（点击表头排序）
            let currentSortColumn = null;
            let currentSortDirection = null;
            
            function sortTableByHeader(headerElement, dataType) {
                const table = document.getElementById('variantTable');
                if (!table) {
                    console.error('表格未找到');
                    return;
                }
                const tbody = table.querySelector('tbody');
                if (!tbody) {
                    console.error('表格tbody未找到');
                    return;
                }
                const rows = Array.from(tbody.querySelectorAll('tr'));
                if (rows.length === 0) {
                    console.warn('没有数据行可排序');
                    return;
                }
                const headers = table.querySelectorAll('th');
                const columnIndex = parseInt(headerElement.getAttribute('data-column'));
                
                if (isNaN(columnIndex)) {
                    console.error('列索引无效:', columnIndex);
                    return;
                }
                
                // 移除所有排序指示器
                headers.forEach(header => {
                    header.classList.remove('asc', 'desc');
                });
                
                // 切换排序方向（Excel式：点击切换升序/降序）
                if (currentSortColumn === columnIndex) {
                    currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    currentSortColumn = columnIndex;
                    currentSortDirection = 'asc';  // 默认升序
                }
                
                // 添加排序指示器
                headerElement.classList.add(currentSortDirection);
                
                // 排序行
                rows.sort((a, b) => {
                    // 确保列索引有效
                    if (columnIndex >= a.cells.length || columnIndex >= b.cells.length) {
                        return 0;
                    }
                    
                    let aValue = a.cells[columnIndex].textContent.trim();
                    let bValue = b.cells[columnIndex].textContent.trim();
                    
                    if (dataType === 'number') {
                        // 处理数字：移除非数字字符，转换为数字
                        aValue = parseFloat(aValue.replace(/[^0-9.]/g, '')) || 0;
                        bValue = parseFloat(bValue.replace(/[^0-9.]/g, '')) || 0;
                    } else {
                        // 文本排序
                        aValue = aValue.toLowerCase();
                        bValue = bValue.toLowerCase();
                    }
                    
                    if (aValue < bValue) return currentSortDirection === 'asc' ? -1 : 1;
                    if (aValue > bValue) return currentSortDirection === 'asc' ? 1 : -1;
                    return 0;
                });
                
                // 重新插入排序后的行
                rows.forEach(row => tbody.appendChild(row));
            }
            
            // 表格筛选功能已移除（按用户要求去除搜索框）
            
        </script>
        """
    
    return html


def _generate_media_charts(charts: Dict[str, Any]) -> str:
    """生成媒体相关图表HTML（支持ECharts交互式图表，v1.10切换到ECharts）"""
    html = ""
    
    from backend.chart.chart_generator import generate_echarts_chart_html
    
    if 'media_coverage_pie' in charts:
        chart_data = charts['media_coverage_pie']
        html += """
        <div class="chart-container">
            <div class="chart-title">媒体覆盖率</div>
        """
        if isinstance(chart_data, dict) and chart_data:
            echarts_html = generate_echarts_chart_html(chart_data)
            if echarts_html:
                html += echarts_html
            else:
                html += '<div style="color: #999; padding: 20px;">图表数据格式错误</div>'
        elif isinstance(chart_data, str) and chart_data:
            html += f'<img src="data:image/png;base64,{chart_data}" alt="媒体覆盖率">'
        else:
            html += '<div style="color: #999; padding: 20px;">暂无数据</div>'
        html += "</div>"
    
    return html