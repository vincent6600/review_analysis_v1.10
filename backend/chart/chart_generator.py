"""
图表生成模块
生成各种类型的图表，支持中文显示
"""

import matplotlib
# 设置matplotlib使用非交互式后端（必须在导入pyplot之前）
# 这样可以避免在非主线程中使用GUI后端的问题
matplotlib.use('Agg')
import os
# 设置matplotlib缓存目录到项目目录
cache_dir = os.path.join(os.path.dirname(__file__), '../../.matplotlib_cache')
os.makedirs(cache_dir, exist_ok=True)
os.environ['MPLCONFIGDIR'] = cache_dir

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
import io
import base64
import json

# 导入ECharts（用于交互式图表，v1.10切换到ECharts方案）
try:
    from pyecharts.charts import Pie, Bar, Line, Funnel, Radar, Scatter
    from pyecharts import options as opts
    from pyecharts.globals import ThemeType
    ECHARTS_AVAILABLE = True
except ImportError:
    ECHARTS_AVAILABLE = False
    Pie = None
    Bar = None
    Line = None
    Funnel = None
    Radar = None
    Scatter = None
    opts = None
    ThemeType = None

# 保留Plotly导入（作为降级方案）
try:
    import plotly.graph_objects as go
    import plotly.express as px
    try:
        from plotly.utils import PlotlyJSONEncoder
    except ImportError:
        from json import JSONEncoder
        class PlotlyJSONEncoder(JSONEncoder):
            def default(self, obj):
                try:
                    return obj.to_dict()
                except:
                    return super().default(obj)
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = None
    px = None

# 配置matplotlib支持中文
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 设置图表样式（简洁现代、浅色主题）
try:
    sns.set_style("whitegrid")
    plt.style.use('seaborn-v0_8-whitegrid')
except:
    sns.set_style("whitegrid")
    plt.style.use('default')


def configure_chinese_font():
    """
    配置中文字体
    尝试使用系统可用的中文字体
    """
    import platform
    
    system = platform.system()
    chinese_fonts = []
    
    if system == 'Darwin':  # macOS
        chinese_fonts = ['Arial Unicode MS', 'PingFang SC', 'STHeiti']
    elif system == 'Windows':
        chinese_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun']
    else:  # Linux
        chinese_fonts = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC']
    
    # 尝试设置字体
    for font in chinese_fonts:
        try:
            plt.rcParams['font.sans-serif'] = [font] + plt.rcParams['font.sans-serif']
            # 测试字体是否可用
            fig, ax = plt.subplots(figsize=(1, 1))
            ax.text(0.5, 0.5, '测试', fontsize=10)
            plt.close(fig)
            break
        except:
            continue


# 初始化中文字体配置
configure_chinese_font()


def save_chart_to_base64(fig) -> str:
    """
    将图表保存为base64编码的字符串
    
    Args:
        fig: matplotlib figure对象
        
    Returns:
        base64编码的图片字符串
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_base64


def generate_pie_chart(data: Dict[str, int], title: str, colors: Optional[List[str]] = None) -> str:
    """
    生成饼图
    
    Args:
        data: 数据字典，{标签: 数值}
        title: 图表标题
        colors: 颜色列表（可选）
        
    Returns:
        base64编码的图片字符串
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    
    labels = list(data.keys())
    values = list(data.values())
    
    if colors is None:
        colors = sns.color_palette("pastel", len(labels))
    
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 12}
    )
    
    # 设置标题
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # 美化文字
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')
    
    return save_chart_to_base64(fig)


def generate_bar_chart(categories: List[str], values: List[float], title: str, 
                      xlabel: str = '', ylabel: str = '', horizontal: bool = False,
                      xlim: tuple = None) -> str:
    """
    生成直方图（柱状图）
    
    Args:
        categories: 类别列表
        values: 数值列表
        title: 图表标题
        xlabel: X轴标签
        ylabel: Y轴标签
        horizontal: 是否横向显示
        xlim: X轴范围 (min, max)，仅当horizontal=True时有效
        
    Returns:
        base64编码的图片字符串
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if horizontal:
        bars = ax.barh(categories, values, color=sns.color_palette("muted", len(categories)))
        ax.set_xlabel(xlabel or '数值', fontsize=12)
        ax.set_ylabel(ylabel or '类别', fontsize=12)
        # 设置X轴范围（仅当horizontal=True时，固定坐标轴区间）
        if xlim:
            ax.set_xlim(xlim[0], xlim[1])
            # 固定坐标轴，不允许自动调整
            ax.set_autoscalex_on(False)
    else:
        bars = ax.bar(categories, values, color=sns.color_palette("muted", len(categories)))
        ax.set_xlabel(xlabel or '类别', fontsize=12)
        ax.set_ylabel(ylabel or '数值', fontsize=12)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # 添加数值标签
    for i, (bar, val) in enumerate(zip(bars, values)):
        if horizontal:
            ax.text(val, i, f' {val}', va='center', fontsize=10)
        else:
            ax.text(i, val, f'{val}', ha='center', va='bottom', fontsize=10)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return save_chart_to_base64(fig)


def generate_line_chart(x_data: List[str], y_data: List[float], title: str,
                       xlabel: str = '', ylabel: str = '', marker: bool = True,
                       smooth: bool = False, ylim: tuple = None) -> str:
    """
    生成曲线图
    
    Args:
        x_data: X轴数据（时间等）
        y_data: Y轴数据
        title: 图表标题
        xlabel: X轴标签
        ylabel: Y轴标签
        marker: 是否显示标记点
        smooth: 是否使用平滑曲线
        ylim: Y轴范围 (min, max)
        
    Returns:
        base64编码的图片字符串
    """
    import numpy as np
    
    # 检查scipy是否可用
    scipy_available = False
    make_interp_spline = None
    try:
        from scipy.interpolate import make_interp_spline
        scipy_available = True
    except ImportError:
        scipy_available = False
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    if smooth and len(x_data) > 2 and scipy_available:
        # 使用样条插值生成平滑曲线
        x_numeric = np.arange(len(x_data))
        x_smooth = np.linspace(0, len(x_data) - 1, 300)
        spl = make_interp_spline(x_numeric, y_data, k=min(3, len(x_data) - 1))
        y_smooth = spl(x_smooth)
        ax.plot(x_smooth, y_smooth, linewidth=2.5, color=sns.color_palette("deep")[0])
        if marker:
            ax.plot(x_numeric, y_data, marker='o', markersize=6, 
                   linestyle='None', color=sns.color_palette("deep")[0])
    else:
        if marker:
            ax.plot(x_data, y_data, marker='o', linewidth=2, markersize=6, 
                    color=sns.color_palette("deep")[0])
        else:
            ax.plot(x_data, y_data, linewidth=2, color=sns.color_palette("deep")[0])
    
    # 设置Y轴范围
    if ylim:
        ax.set_ylim(ylim[0], ylim[1])
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(xlabel or '时间', fontsize=12)
    ax.set_ylabel(ylabel or '数值', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # 设置X轴标签
    ax.set_xticks(range(len(x_data)))
    ax.set_xticklabels(x_data, rotation=45, ha='right')
    
    plt.tight_layout()
    
    return save_chart_to_base64(fig)


def generate_funnel_chart(categories: List[str], values: List[float], title: str) -> str:
    """
    生成漏斗图（用于星级分布等场景）
    从上到下显示，适合展示层级结构
    
    Args:
        categories: 类别列表（从上到下）
        values: 数值列表
        title: 图表标题
        
    Returns:
        base64编码的图片字符串
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # 保持categories和values的原有顺序（不按数值排序）
    # 这样可以让调用者控制排序方式（比如按星级顺序：5星、4星、3星、2星、1星）
    
    # 计算最大宽度（用于归一化）
    max_value = max(values) if values else 1
    
    # 设置漏斗图的参数
    num_categories = len(categories)
    bar_height = 0.8 / num_categories  # 每个条的高度
    y_positions = [0.9 - i * (0.8 / num_categories) for i in range(num_categories)]
    
    # 生成颜色（从深到浅，适合漏斗效果）
    colors = sns.color_palette("Blues", num_categories)[::-1]  # 反转，让顶部更深
    
    # 绘制漏斗条
    for i, (cat, val) in enumerate(zip(categories, values)):
        # 计算宽度（相对于最大值）
        width = val / max_value * 0.6  # 最大宽度为0.6
        x_center = 0.5
        x_left = x_center - width / 2
        x_right = x_center + width / 2
        
        # 绘制矩形
        rect = plt.Rectangle((x_left, y_positions[i] - bar_height/2), 
                            width, bar_height, 
                            facecolor=colors[i], 
                            edgecolor='white', 
                            linewidth=1.5)
        ax.add_patch(rect)
        
        # 添加标签（左侧）
        ax.text(x_left - 0.02, y_positions[i], cat, 
               ha='right', va='center', fontsize=12, fontweight='bold')
        
        # 添加数值（右侧）
        ax.text(x_right + 0.02, y_positions[i], f'{int(val)}', 
               ha='left', va='center', fontsize=11)
    
    # 设置标题
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # 隐藏坐标轴
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    
    return save_chart_to_base64(fig)


# ==================== ECharts交互式图表函数（v1.10切换到ECharts方案）====================

def generate_echarts_chart_html(option_dict: Dict[str, Any]) -> str:
    """
    生成ECharts交互式图表的HTML字符串（v1.10新增：使用ECharts替代Plotly）
    
    Args:
        option_dict: ECharts图表配置字典
        
    Returns:
        HTML字符串（包含div标签，使用data属性存储图表配置）
    """
    if not ECHARTS_AVAILABLE or not option_dict:
        return ""
    
    # 将图表配置转换为JSON
    chart_json = json.dumps(option_dict, ensure_ascii=False)
    # 转义HTML特殊字符，用于HTML属性
    # 注意：使用HTML实体编码转义，确保JSON在HTML属性中正确解析
    import html
    chart_json_escaped = html.escape(chart_json, quote=True)
    
    # 生成唯一的div ID
    import uuid
    div_id = f"echarts-chart-{uuid.uuid4().hex[:8]}"
    
    # 返回HTML字符串（使用data属性存储图表配置，前端JavaScript会读取并渲染）
    # 使用双引号包裹data属性值，HTML实体编码已处理所有特殊字符
    html = f"""
    <div id="{div_id}" class="echarts-chart-container" data-echarts-chart="{chart_json_escaped}" style="width:100%;height:400px;"></div>
    """
    return html


def generate_echarts_pie_chart(labels: List[str], values: List[float], title: str) -> Optional[Dict[str, Any]]:
    """
    生成ECharts饼图配置（简约商务风格）
    
    Args:
        labels: 标签列表
        values: 数值列表
        title: 图表标题
        
    Returns:
        ECharts图表配置字典
    """
    if not ECHARTS_AVAILABLE:
        return None
    
    # 简约商务配色方案
    business_colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96', '#fa8c16']
    
    pie = (
        Pie(init_opts=opts.InitOpts(theme=None))  # 简约商务风格，不使用主题
        .add(
            "",
            [list(z) for z in zip(labels, values)],
            radius=["40%", "70%"],
            center=["50%", "50%"]
        )
        .set_global_opts(
            # 去除图表标题（模块标题保留）
            legend_opts=opts.LegendOpts(
                pos_left="right",
                orient="vertical",
                textstyle_opts=opts.TextStyleOpts(font_size=12)
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter="{b}: {c} ({d}%)",
                background_color="rgba(255, 255, 255, 0.98)",
                border_color="#d9d9d9",
                border_width=1,
                textstyle_opts=opts.TextStyleOpts(color="#333", font_size=12),
                is_confine=True
            )
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(
                formatter="{b}\n{c} ({d}%)",  # 标签换行显示，改善显示不全的问题
                font_size=11,  # 稍微减小字体
                position="outside",  # 标签显示在外部
                # 注意：distance_to_label_line 不是 pyecharts LabelOpts 的有效参数，已移除
                # 使用富文本样式，确保标签完整显示
                rich={  # 使用富文本样式，确保标签完整显示
                    'name': {
                        'fontSize': 11,
                        'lineHeight': 16
                    },
                    'value': {
                        'fontSize': 11,
                        'lineHeight': 16
                    }
                }
            ),
            itemstyle_opts=opts.ItemStyleOpts(
                border_color="#fff",
                border_width=2
            )
        )
    )
    
    # 应用商务配色
    option = pie.dump_options_with_quotes()
    option_dict = json.loads(option)
    if 'color' not in option_dict:
        option_dict['color'] = business_colors[:len(labels)]
    
    return option_dict


def generate_echarts_funnel_chart(categories: List[str], values: List[float], title: str) -> Optional[Dict[str, Any]]:
    """
    生成ECharts漏斗图配置（从上到下：5星、4星、3星、2星、1星）
    
    Args:
        categories: 类别列表（按顺序，不排序）
        values: 数值列表
        title: 图表标题
        
    Returns:
        ECharts图表配置字典
    """
    if not ECHARTS_AVAILABLE:
        return None
    
    # 简约商务配色方案
    business_colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1']
    
    funnel = (
        Funnel(init_opts=opts.InitOpts(theme=None))  # 不使用主题，使用自定义简约商务风格
        .add(
            "",
            [list(z) for z in zip(categories, values)],
            gap=2,
            label_opts=opts.LabelOpts(is_show=False)  # 不显示标签，避免重复
        )
        .set_global_opts(
            # 去除图表标题（模块标题保留）
            legend_opts=opts.LegendOpts(
                pos_left="right",  # 图例在右侧
                orient="vertical",  # 垂直排列
                textstyle_opts=opts.TextStyleOpts(font_size=11),  # 稍微减小字体，改善显示不全的问题
                item_width=14,  # 图例标记宽度
                item_height=14,  # 图例标记高度
                item_gap=8,  # 图例项之间的间距
                # 注意：图例数据从series自动获取，不需要手动指定data参数
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter="{b}: {c} ({d}%)",
                background_color="rgba(255, 255, 255, 0.98)",
                border_color="#d9d9d9",
                border_width=1,
                textstyle_opts=opts.TextStyleOpts(color="#333", font_size=12),
                is_confine=True
            )
        )
        .set_series_opts(
            itemstyle_opts=opts.ItemStyleOpts(
                border_color="#fff",
                border_width=2
            )
        )
    )
    
    option = funnel.dump_options_with_quotes()
    option_dict = json.loads(option)
    if 'color' not in option_dict:
        option_dict['color'] = business_colors[:len(categories)]
    
    # 确保图例顺序：5星、4星、3星、2星、1星（从下到上显示）
    if 'legend' in option_dict and 'data' in option_dict['legend']:
        # 反转图例顺序，使其从5星到1星（从下到上）
        option_dict['legend']['data'] = list(reversed(categories))
    
    return option_dict


def generate_echarts_bar_chart(categories: List[str], values: List[float], title: str,
                               xlabel: str = '', ylabel: str = '', horizontal: bool = False,
                               show_label: bool = False, color_values: List[float] = None,
                               xlim: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
    """
    生成ECharts柱状图配置（简约商务风格）
    
    Args:
        categories: 类别列表
        values: 数值列表
        title: 图表标题
        xlabel: X轴标签
        ylabel: Y轴标签
        horizontal: 是否横向显示
        
    Returns:
        ECharts图表配置字典
    """
    if not ECHARTS_AVAILABLE:
        return None
    
    # 如果提供了color_values，根据值生成颜色渐变（浅蓝到深蓝）
    if color_values and len(color_values) == len(values):
        min_val = min(color_values) if color_values else 0
        max_val = max(color_values) if color_values else 1
        range_val = max_val - min_val if max_val > min_val else 1
        
        # 生成颜色数组：从浅蓝(#e6f7ff)到深蓝(#1890ff)
        colors = []
        for val in color_values:
            # 计算颜色强度（0-1）
            intensity = (val - min_val) / range_val if range_val > 0 else 0
            # 浅蓝 RGB: (230, 247, 255), 深蓝 RGB: (24, 144, 255)
            r = int(230 + (24 - 230) * intensity)
            g = int(247 + (144 - 247) * intensity)
            b = int(255 + (255 - 255) * intensity)
            colors.append(f"rgb({r}, {g}, {b})")
    else:
        # 默认简约商务蓝色
        colors = ['#1890ff'] * len(values)
    
    if horizontal:
        bar = (
            Bar(init_opts=opts.InitOpts(theme=None))  # 简约商务风格，不使用主题
            .add_xaxis(categories)
            .add_yaxis("", values, category_gap="20%")
            .reversal_axis()
            .set_series_opts(
                label_opts=opts.LabelOpts(
                    is_show=show_label, 
                    position="right",  # 横向图显示在右侧（条形末端）
                    formatter="{c}", 
                    font_size=11, 
                    color="#333"
                ),
                # 颜色将在dump_options后手动设置
            )
        )
    else:
        bar = (
            Bar(init_opts=opts.InitOpts(theme=None))  # 简约商务风格，不使用主题
            .add_xaxis(categories)
            .add_yaxis("", values, category_gap="20%")
            .set_series_opts(
                label_opts=opts.LabelOpts(
                    is_show=show_label, 
                    position="top", 
                    formatter="{c}", 
                    font_size=11, 
                    color="#333"
                ),
                # 颜色将在dump_options后手动设置
            )
        )
    
    bar.set_global_opts(
        # 去除图表标题（模块标题保留）
        xaxis_opts=opts.AxisOpts(
            name=xlabel or ("类别" if not horizontal else "数值"),
            name_textstyle_opts=opts.TextStyleOpts(font_size=12, color="#666"),
            axislabel_opts=opts.LabelOpts(color="#666", font_size=11),
            axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#d9d9d9")),
            splitline_opts=opts.SplitLineOpts(is_show=False),  # 简约风格，不显示网格线
            min_=xlim[0] if xlim and not horizontal else None,  # 横坐标轴范围（非横向图）
            max_=xlim[1] if xlim and not horizontal else None
        ),
        yaxis_opts=opts.AxisOpts(
            name=ylabel or ("数值" if not horizontal else "类别"),
            name_textstyle_opts=opts.TextStyleOpts(font_size=12, color="#666"),
            axislabel_opts=opts.LabelOpts(color="#666", font_size=11),
            axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#d9d9d9")),
            splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(color="#f0f0f0", type_="dashed")),
            min_=xlim[0] if xlim and horizontal else None,  # 横坐标轴范围（横向图时在y轴设置）
            max_=xlim[1] if xlim and horizontal else None
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="axis",
            formatter="{b}: {c}",
            background_color="rgba(255, 255, 255, 0.98)",
            border_color="#d9d9d9",
            border_width=1,
            textstyle_opts=opts.TextStyleOpts(color="#333", font_size=12),
            is_confine=True  # 禁用动画
        ),
        datazoom_opts=opts.DataZoomOpts(
            type_="slider",  # 滑块型数据缩放
            xaxis_index=[0],  # 控制x轴
            range_start=0,  # 默认拉满全区间（0%）
            range_end=100  # 默认拉满全区间（100%）
        ) if len(categories) > 5 else None  # 当数据点超过5个时启用缩放
    )
    
    option = bar.dump_options_with_quotes()
    option_dict = json.loads(option)
    # 应用颜色渐变（如果提供了color_values）
    if colors and len(colors) == len(values) and len(colors) > 1:
        # 为每个数据项设置颜色
        if 'series' in option_dict and len(option_dict['series']) > 0:
            if 'data' in option_dict['series'][0]:
                for i, item in enumerate(option_dict['series'][0]['data']):
                    if isinstance(item, (int, float)):
                        option_dict['series'][0]['data'][i] = {
                            'value': item,
                            'itemStyle': {'color': colors[i] if i < len(colors) else colors[0]}
                        }
                    elif isinstance(item, dict):
                        if 'itemStyle' not in item:
                            item['itemStyle'] = {}
                        item['itemStyle']['color'] = colors[i] if i < len(colors) else colors[0]
    elif 'color' not in option_dict:
        option_dict['color'] = ['#1890ff']
    
    return option_dict


def generate_echarts_line_chart(x_data: List[str], y_data: List[float], title: str,
                                xlabel: str = '', ylabel: str = '', ylim: Optional[tuple] = None,
                                xlim: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
    """
    生成ECharts折线图配置（简约商务风格，支持平滑曲线）
    
    Args:
        x_data: X轴数据（时间）
        y_data: Y轴数据（数值）
        title: 图表标题
        xlabel: X轴标签
        ylabel: Y轴标签
        ylim: Y轴范围（可选）
        
    Returns:
        ECharts图表配置字典
    """
    if not ECHARTS_AVAILABLE:
        return None
    
    # 简约商务配色方案
    business_colors = ['#1890ff']
    
    line = (
        Line(init_opts=opts.InitOpts(theme=None))  # 简约商务风格，不使用主题
        .add_xaxis(x_data)
        .add_yaxis(
            "",
            y_data,
            is_smooth=True,
            symbol="circle",
            symbol_size=6,
            linestyle_opts=opts.LineStyleOpts(width=2.5),
            label_opts=opts.LabelOpts(is_show=False)
        )
        .set_global_opts(
            # 去除图表标题（模块标题保留）
            xaxis_opts=opts.AxisOpts(
                name=xlabel or "时间",
                name_textstyle_opts=opts.TextStyleOpts(font_size=12, color="#666"),
                axislabel_opts=opts.LabelOpts(rotate=45, color="#666", font_size=11),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#d9d9d9")),
                splitline_opts=opts.SplitLineOpts(is_show=False)
            ),
            yaxis_opts=opts.AxisOpts(
                name=ylabel or "数值",
                name_textstyle_opts=opts.TextStyleOpts(font_size=12, color="#666"),
                axislabel_opts=opts.LabelOpts(color="#666", font_size=11),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#d9d9d9")),
                splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(color="#f0f0f0", type_="dashed")),
                min_=ylim[0] if ylim else None,
                max_=ylim[1] if ylim else None
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                formatter="{b}: {c}",
                background_color="rgba(255, 255, 255, 0.98)",
                border_color="#d9d9d9",
                border_width=1,
                textstyle_opts=opts.TextStyleOpts(color="#333", font_size=12),
                is_confine=True
            ),
            datazoom_opts=opts.DataZoomOpts(
                type_="slider",  # 滑块型数据缩放
                xaxis_index=[0],  # 控制x轴
                range_start=0,  # 默认拉满全区间（0%）
                range_end=100  # 默认拉满全区间（100%）
            ) if len(x_data) > 5 else None  # 当数据点超过5个时启用缩放
        )
    )
    
    option = line.dump_options_with_quotes()
    option_dict = json.loads(option)
    if 'color' not in option_dict:
        option_dict['color'] = business_colors
    
    return option_dict


def generate_echarts_stacked_area_chart(
    months: List[str], 
    variant_data: Dict[str, List[int]], 
    title: str,
    xlim: Optional[tuple] = None
) -> Optional[Dict[str, Any]]:
    """
    生成ECharts堆叠面积图（简约商务风格）
    
    Args:
        months: 月份列表
        variant_data: 变体数据字典，{变体名: [各月评论数列表]}
        title: 图表标题
        
    Returns:
        ECharts图表配置字典
    """
    if not ECHARTS_AVAILABLE:
        return None
    
    # 简约商务配色方案（无渐变色，纯色）
    business_colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96', '#fa8c16', '#2f54eb', '#a0d911']
    
    line = (
        Line(init_opts=opts.InitOpts(theme=None))
        .add_xaxis(months)
    )
    
    # 为每个变体添加一条线，使用stack堆叠
    variants = list(variant_data.keys())
    for i, variant in enumerate(variants):
        values = variant_data[variant]
        color = business_colors[i % len(business_colors)]
        line.add_yaxis(
            variant,
            values,
            stack="总量",  # 堆叠标识
            areastyle_opts=opts.AreaStyleOpts(opacity=0.7, color=color),  # 面积样式，使用纯色
            linestyle_opts=opts.LineStyleOpts(width=1, color=color),
            symbol="circle",
            symbol_size=4,
            label_opts=opts.LabelOpts(is_show=False)  # 不显示标签
        )
    
    line.set_global_opts(
        # 去除图表标题（模块标题保留）
        legend_opts=opts.LegendOpts(
            pos_left="right",
            orient="vertical",
            textstyle_opts=opts.TextStyleOpts(font_size=11)
        ),
        xaxis_opts=opts.AxisOpts(
            name="时间",
            name_textstyle_opts=opts.TextStyleOpts(font_size=12, color="#666"),
            axislabel_opts=opts.LabelOpts(rotate=45, color="#666", font_size=11),
            axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#d9d9d9")),
            splitline_opts=opts.SplitLineOpts(is_show=False)
        ),
        yaxis_opts=opts.AxisOpts(
            name="评论数量",
            name_textstyle_opts=opts.TextStyleOpts(font_size=12, color="#666"),
            axislabel_opts=opts.LabelOpts(color="#666", font_size=11),
            axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#d9d9d9")),
            splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(color="#f0f0f0", type_="dashed"))
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="axis",
            formatter="{b}<br/>{a}: {c}",
            background_color="rgba(255, 255, 255, 0.98)",
            border_color="#d9d9d9",
            border_width=1,
            textstyle_opts=opts.TextStyleOpts(color="#333", font_size=12),
            is_confine=True
        ),
        datazoom_opts=opts.DataZoomOpts(
            type_="slider",  # 滑块型数据缩放
            xaxis_index=[0],  # 控制x轴
            range_start=0,  # 默认拉满全区间（0%）
            range_end=100  # 默认拉满全区间（100%）
        ) if len(months) > 5 else None  # 当数据点超过5个时启用缩放
    )
    
    option = line.dump_options_with_quotes()
    option_dict = json.loads(option)
    # 应用配色
    if 'color' not in option_dict:
        option_dict['color'] = business_colors[:len(variants)]
    
    return option_dict


def _format_radar_tooltip(params, values: List[float]) -> str:
    """格式化雷达图tooltip，处理评论数量和平均星级的显示"""
    series_name = params.seriesName if hasattr(params, 'seriesName') else ''
    name = params.name if hasattr(params, 'name') else ''
    value = params.value if hasattr(params, 'value') else 0
    
    if series_name == '评论数量':
        return f"{series_name}<br/>{name}: {value}"
    else:
        # 平均星级需要反缩放：从评论数量范围反算回0-5范围
        max_review_count = max(values) * 1.2 if values else 100
        if max_review_count > 0:
            rating = round((value / max_review_count) * 5.0, 2)
        else:
            rating = 0
        return f"{series_name}<br/>{name}: {rating}"


def generate_echarts_radar_chart(
    categories: List[str], 
    values: List[float], 
    title: str,
    avg_ratings: Optional[List[float]] = None
) -> Optional[Dict[str, Any]]:
    """
    生成ECharts雷达图（简约商务风格）
    
    Args:
        categories: 类别列表（变体名称等）
        values: 数值列表
        title: 图表标题
        
    Returns:
        ECharts图表配置字典
    """
    if not ECHARTS_AVAILABLE:
        return None
    
    # 构建雷达图指标（每个类别作为一个指标）
    # 以平均星级为基准（3.5-5.0范围），评论数量需要缩放到这个范围内
    rating_min = 3.5
    rating_max = 5.0
    rating_range = rating_max - rating_min  # 1.5
    
    # 指标范围固定为3.5-5.0（以平均星级为基准）
    indicators = [
        opts.RadarIndicatorItem(name=cat, max_=rating_max, min_=rating_min)
        for cat in categories
    ]
    
    # 将评论数量缩放到3.5-5.0范围
    # 计算评论数量的范围
    if values:
        min_review_count = min(values) if values else 0
        max_review_count = max(values) if values else 1
        review_range = max_review_count - min_review_count if max_review_count > min_review_count else 1
        
        # 将评论数量从原始范围缩放到3.5-5.0范围
        # 公式：scaled = 3.5 + (value - min) / range * 1.5
        scaled_values = []
        for val in values:
            if review_range > 0:
                scaled_val = rating_min + (val - min_review_count) / review_range * rating_range
            else:
                scaled_val = rating_min  # 如果所有值相同，设置为最小值
            scaled_values.append(round(scaled_val, 1))  # 保留小数点后1位
    else:
        scaled_values = [rating_min] * len(categories)
    
    radar = (
        Radar(init_opts=opts.InitOpts(theme=None))
        .add_schema(
            schema=indicators,
            splitarea_opt=opts.SplitAreaOpts(
                is_show=True,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.1)
            ),
            textstyle_opts=opts.TextStyleOpts(color="#666", font_size=11)
        )
        .add(
            "评论数量",
            [scaled_values],  # 使用缩放后的评论数量
            areastyle_opts=opts.AreaStyleOpts(opacity=0.3, color="#1890ff"),  # 纯色，无渐变
            linestyle_opts=opts.LineStyleOpts(width=2, color="#1890ff"),
            label_opts=opts.LabelOpts(is_show=False),  # 默认不显示标签
            emphasis_opts=opts.EmphasisOpts(
                label_opts=opts.LabelOpts(is_show=True, formatter="{b}: {c}")  # 悬停时显示数据标签
            )
        )
    )
    
    # 如果提供了平均星级数据，添加第二个系列（平均星级已经在3.5-5.0范围内，不需要缩放）
    if avg_ratings and len(avg_ratings) == len(values):
        # 平均星级已经在3.5-5.0范围内，直接使用，但需要确保在范围内
        # 确保平均星级在有效范围内（3.5-5.0）
        normalized_ratings = []
        for rating in avg_ratings:
            if rating < rating_min:
                normalized_rating = rating_min
            elif rating > rating_max:
                normalized_rating = rating_max
            else:
                normalized_rating = rating
            normalized_ratings.append(round(normalized_rating, 1))  # 保留小数点后1位
        
        # 保存avg_ratings和values用于formatter（闭包变量）
        _avg_ratings_ref = avg_ratings
        _values_ref = values
        _categories_ref = categories
        
        radar.add(
            "平均星级",
            [normalized_ratings],  # 使用归一化后的平均星级（已在3.5-5.0范围内）
            areastyle_opts=opts.AreaStyleOpts(opacity=0.3, color="#52c41a"),  # 绿色表示平均星级
            linestyle_opts=opts.LineStyleOpts(width=2, color="#52c41a"),
            label_opts=opts.LabelOpts(is_show=False),  # 默认不显示标签
            emphasis_opts=opts.EmphasisOpts(
                label_opts=opts.LabelOpts(
                    is_show=True,
                    # 显示原始平均星级值（不是归一化后的值）
                    formatter=lambda params: f"{params.name}: {_avg_ratings_ref[params.dataIndex]:.1f}" if params.dataIndex < len(_avg_ratings_ref) else f"{params.name}: N/A"
                )
            )
        )
    
    radar.set_global_opts(
        # 去除图表标题（模块标题保留）
        legend_opts=opts.LegendOpts(
            pos_left="right",  # 图例在右侧
            orient="vertical",  # 垂直排列
            textstyle_opts=opts.TextStyleOpts(font_size=12)
            # 注意：图例数据从series自动获取（"评论数量"和"平均星级"），不需要手动指定data参数
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="item",  # 只触发单个数据点
            # 不使用formatter，让ECharts使用默认格式，然后在后处理中修改
            background_color="rgba(255, 255, 255, 0.98)",
            border_color="#d9d9d9",
            border_width=1,
            textstyle_opts=opts.TextStyleOpts(color="#333", font_size=12),
            is_confine=True
        )
    )
    
    option = radar.dump_options_with_quotes()
    option_dict = json.loads(option)
    
    # 确保两个系列默认同时显示（不隐藏任何系列）
    # 关键修复：禁用series级别的tooltip，只在全局tooltip中处理
    # 这样可以确保tooltip只显示一次，不显示所有系列的数据
    if 'series' in option_dict:
        for series in option_dict['series']:
            if 'emphasis' not in series:
                series['emphasis'] = {}
            if 'focus' not in series.get('emphasis', {}):
                series['emphasis']['focus'] = 'none'  # 不自动聚焦，保持两个系列都显示
            # 关键：禁用series级别的tooltip，强制使用全局tooltip
            # 这样可以确保formatter只被调用一次，只显示单个数据点
            series['tooltip'] = {'show': False}  # 禁用series级别的tooltip
    
    # 修复tooltip formatter：显示变体名称、评论数量、平均星级
    # 参照散点图的逻辑，使用JavaScript函数格式化tooltip
    if 'tooltip' in option_dict and avg_ratings and len(avg_ratings) == len(values):
        # 准备数据用于formatter（转换为JSON字符串，嵌入到JavaScript代码中）
        categories_json = json.dumps(categories, ensure_ascii=False)
        values_json = json.dumps([float(v) for v in values], ensure_ascii=False)  # 确保是float类型
        avg_ratings_json = json.dumps([float(r) for r in avg_ratings], ensure_ascii=False)  # 确保是float类型
        
        # 平均星级的坐标范围（用于反缩放）
        rating_min = 3.5
        rating_max = 5.0
        rating_range = rating_max - rating_min
        max_review_count = max(values) * 1.2 if values else 100
        
        # 使用JavaScript函数格式化tooltip
        # 格式：变体名称、评论数量、平均星级
        # 彻底修复：确保只显示单个数据点，不显示所有系列的数据
        formatter_code = f"""function(params) {{
            // 彻底修复：雷达图tooltip只显示当前悬停点的数据
            // 关键：ECharts雷达图在有多个系列时，tooltip默认会显示所有系列的数据
            // 解决方案：强制只处理第一个数据点，忽略其他系列
            
            // 关键修复：如果params是数组，只处理第一个元素（当前悬停的点）
            // 即使ECharts传递了所有系列的数据，我们也只显示第一个
            var param = null;
            if (Array.isArray(params)) {{
                // 如果是数组，只取第一个元素（当前悬停的点）
                param = params.length > 0 ? params[0] : null;
            }} else {{
                param = params;
            }}
            
            // 确保param存在且是雷达图类型
            if (!param || param.seriesType !== 'radar' || !param.name) {{
                return '';
            }}
            
            var categories = {categories_json};
            var values = {values_json};
            var avgRatings = {avg_ratings_json};
            
            // 使用param.name获取当前悬停的指标名称（变体名称）
            var category = param.name || '';
            var dataIndex = categories.indexOf(category);
            
            // 只处理有效的索引，确保只显示当前悬停点的数据
            if (dataIndex >= 0 && dataIndex < values.length && dataIndex < avgRatings.length) {{
                var reviewCount = values[dataIndex];
                var avgRating = avgRatings[dataIndex];  // 直接使用原始的平均星级值
                
                // 确保平均星级在有效范围内（1-5）
                if (avgRating < 1) avgRating = 1;
                if (avgRating > 5) avgRating = 5;
                
                // 返回格式化的tooltip内容：只显示当前悬停点的数据
                // 注意：只返回一次，不重复显示，格式与散点图保持一致
                return '变体名称：' + category + '<br/>评论数量：' + reviewCount + '<br/>平均星级：' + avgRating.toFixed(1);
            }}
            
            // 如果数据无效，返回空字符串，不显示tooltip
            return '';
        }}"""
        
        option_dict['tooltip']['formatter'] = formatter_code
        option_dict['tooltip']['trigger'] = 'item'  # 关键：设置为'item'，只在数据项上触发
        # 彻底修复：禁用多系列tooltip的默认显示行为
        # 关键：设置showContent为false，然后通过formatter完全控制显示内容
        option_dict['tooltip']['showContent'] = True  # 保持为true，但formatter会控制内容
        # 确保tooltip只显示单个数据点，不显示所有系列
        option_dict['tooltip']['confine'] = True
        # 禁用axisPointer，确保只触发单个数据点
        if 'axisPointer' not in option_dict['tooltip']:
            option_dict['tooltip']['axisPointer'] = {}
        option_dict['tooltip']['axisPointer']['type'] = 'none'
        # 设置tooltip文本左对齐（左对称），与散点图保持一致
        if 'textStyle' not in option_dict['tooltip']:
            option_dict['tooltip']['textStyle'] = {}
        option_dict['tooltip']['textStyle']['align'] = 'left'
        # 关键：设置appendToBody为false，确保tooltip只显示一次
        option_dict['tooltip']['appendToBody'] = False
        # 关键：设置enterable为false，确保tooltip不会进入图表内部
        option_dict['tooltip']['enterable'] = False
        # 关键修复：设置extraCssText来确保tooltip样式正确
        if 'extraCssText' not in option_dict['tooltip']:
            option_dict['tooltip']['extraCssText'] = ''
        # 关键：禁用第二个系列的tooltip显示（通过设置series的tooltip配置）
        # 这已经在上面通过series['tooltip'] = {'show': False}完成了
    
    return option_dict


def generate_echarts_scatter_chart(
    data: List[Dict[str, Any]], 
    title: str,
    xlabel: str = '价格', 
    ylabel: str = '评论数'
) -> Optional[Dict[str, Any]]:
    """
    生成ECharts气泡图（变体价格-评论数关系，简约商务风格）
    
    Args:
        data: 数据列表，每个元素包含 {'variant': 变体名, 'price': 价格, 'sales': 评论数, 'rating': 评分}
        title: 图表标题
        xlabel: X轴标签
        ylabel: Y轴标签
        
    Returns:
        ECharts图表配置字典
    """
    if not ECHARTS_AVAILABLE or not data:
        return None
    
    # 准备数据：[[价格, 评论数, 变体名]]，简单散点图（固定大小）
    scatter_data = []
    
    for d in data:
        # ECharts散点图数据格式：[x, y, 变体名]
        scatter_data.append([d['price'], d['sales'], d['variant']])
    
    # 简约商务配色方案
    business_colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96', '#fa8c16', '#2f54eb', '#a0d911']
    
    # ECharts散点图：为每个变体创建一个系列
    # 每个系列包含一个数据点，X轴是价格，Y轴是评论数
    # 注意：pyecharts的Scatter图表，数据格式应该是 [[x, y]]，所有系列共享同一个X轴（数值轴）
    scatter = Scatter(init_opts=opts.InitOpts(theme=None))
    
    # 第一个系列：设置X轴（使用空数组，因为使用数值轴）
    scatter.add_xaxis([])
    
    # 为每个变体创建一个系列
    for i, d in enumerate(data):
        variant_name = d['variant']
        price = float(d['price'])  # 确保是数值类型
        sales = int(d['sales'])  # 确保是整数类型
        color = business_colors[i % len(business_colors)]
        
        # pyecharts Scatter图表：数据格式是 [[x, y]]，其中x是价格，y是评论数
        # 所有系列共享同一个X轴（数值轴），每个系列只包含自己的数据点
        scatter.add_yaxis(
            variant_name,  # 系列名称（变体名），会显示在图例中
            [[price, sales]],  # 数据格式：[[x, y]]，x是价格，y是评论数
            symbol_size=8,  # 固定大小，简单散点图
            label_opts=opts.LabelOpts(is_show=False),  # 默认不显示标签，悬停时显示
            itemstyle_opts=opts.ItemStyleOpts(color=color)  # 设置颜色
        )
    
    # 设置全局选项（在循环外）
    scatter.set_global_opts(
        # 去除图表标题（模块标题保留）
        xaxis_opts=opts.AxisOpts(
            name=xlabel,
            name_textstyle_opts=opts.TextStyleOpts(font_size=12, color="#666"),
            axislabel_opts=opts.LabelOpts(color="#666", font_size=11),
            axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#d9d9d9")),
            splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(color="#f0f0f0", type_="dashed"))
        ),
        yaxis_opts=opts.AxisOpts(
            type_="value",  # 数值轴
            name=ylabel,
            name_textstyle_opts=opts.TextStyleOpts(font_size=12, color="#666"),
            axislabel_opts=opts.LabelOpts(color="#666", font_size=11),
            axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#d9d9d9")),
            splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(color="#f0f0f0", type_="dashed")),
            # 确保Y轴不会与右侧图例重叠
            name_location="middle",  # Y轴名称位置
            name_gap=50  # Y轴名称与轴线的距离
        ),
        legend_opts=opts.LegendOpts(
            pos_left="right",  # 图例在右侧
            pos_top="middle",  # 图例垂直居中
            orient="vertical",  # 垂直排列
            textstyle_opts=opts.TextStyleOpts(font_size=12),
            item_gap=8,  # 图例项之间的间距
            # 确保图例不会与图表重叠
            padding=[10, 10],  # 图例内边距
            # 限制图例宽度，避免占用太多空间
            item_width=25,  # 图例标记宽度
            item_height=14  # 图例标记高度
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="item",  # 只触发单个数据点，不显示其他无关数据
            # 不使用formatter，让ECharts使用默认格式，然后在后处理中修改
            background_color="rgba(255, 255, 255, 0.98)",
            border_color="#d9d9d9",
            border_width=1,
            textstyle_opts=opts.TextStyleOpts(color="#333", font_size=12),
            is_confine=True  # 限制tooltip在图表区域内
        )
    )
    
    option = scatter.dump_options_with_quotes()
    option_dict = json.loads(option)
    
    # 调整图表布局，为右侧图例预留空间，避免图例与图表内容重叠
    if 'grid' not in option_dict:
        option_dict['grid'] = {}
    option_dict['grid']['right'] = '20%'  # 右侧预留20%空间给图例
    option_dict['grid']['left'] = '10%'  # 左侧预留10%空间给Y轴标签
    option_dict['grid']['top'] = '10%'  # 顶部预留空间
    option_dict['grid']['bottom'] = '15%'  # 底部预留空间给X轴标签
    
    # 确保图例固定在右侧，不会与图表内容重叠
    if 'legend' in option_dict:
        if isinstance(option_dict['legend'], dict):
            option_dict['legend']['left'] = 'right'
            option_dict['legend']['top'] = 'middle'
            option_dict['legend']['orient'] = 'vertical'
            # 确保图例不会与图表重叠
            option_dict['legend']['padding'] = [10, 10]
            option_dict['legend']['itemGap'] = 8
    
    # 确保X轴和Y轴都是数值轴（value类型）
    if 'xAxis' in option_dict:
        if isinstance(option_dict['xAxis'], list) and len(option_dict['xAxis']) > 0:
            if isinstance(option_dict['xAxis'][0], dict):
                option_dict['xAxis'][0]['type'] = 'value'
                # 移除data，因为数值轴不需要data
                if 'data' in option_dict['xAxis'][0]:
                    del option_dict['xAxis'][0]['data']
        elif isinstance(option_dict['xAxis'], dict):
            option_dict['xAxis']['type'] = 'value'
            if 'data' in option_dict['xAxis']:
                del option_dict['xAxis']['data']
    
    if 'yAxis' in option_dict:
        if isinstance(option_dict['yAxis'], list) and len(option_dict['yAxis']) > 0:
            if isinstance(option_dict['yAxis'][0], dict):
                option_dict['yAxis'][0]['type'] = 'value'
        elif isinstance(option_dict['yAxis'], dict):
            option_dict['yAxis']['type'] = 'value'
    
    # 修复tooltip formatter：使用JavaScript函数格式化tooltip
    # 在ECharts散点图中，params.data格式是 [x, y]
    # 注意：ECharts的formatter需要是字符串形式的JavaScript代码，前端会eval执行
    # 确保只显示悬停点的数据，不显示其他无关数据
    if 'tooltip' in option_dict:
        # 使用JavaScript函数格式化tooltip
        # 注意：formatter必须是字符串，ECharts会在前端eval执行
        # 标签格式：变体：、价格：、评论数：
        # 使用JSON.stringify确保字符串正确转义
        formatter_code = """function(params) {
            if (params.seriesType === 'scatter' && params.data && Array.isArray(params.data) && params.data.length >= 2) {
                var x = params.data[0] || 'N/A';
                var y = params.data[1] || 'N/A';
                return '变体：' + params.seriesName + '<br/>价格：' + x + '<br/>评论数：' + y;
            }
            return '';
        }"""
        # 将formatter设置为字符串，ECharts会在前端执行
        option_dict['tooltip']['formatter'] = formatter_code
        # 确保trigger是'item'，只显示悬停点的数据
        option_dict['tooltip']['trigger'] = 'item'
        # 确保只显示单个数据点，不显示其他点
        # 注意：在ECharts配置中，使用 'confine' 而不是 'is_confine'
        if 'confine' not in option_dict['tooltip']:
            option_dict['tooltip']['confine'] = True
        # 设置tooltip文本左对齐（左对称）
        if 'textStyle' not in option_dict['tooltip']:
            option_dict['tooltip']['textStyle'] = {}
        option_dict['tooltip']['textStyle']['align'] = 'left'
    
    return option_dict


# ==================== Plotly交互式图表函数（保留作为降级方案）===================

def generate_plotly_chart_html(fig_dict: Dict[str, Any]) -> str:
    """
    生成Plotly交互式图表的HTML字符串（v1.10修复版：使用数据属性）
    
    Args:
        fig_dict: Plotly图表配置字典
        
    Returns:
        HTML字符串（包含div标签，使用data属性存储图表数据）
    """
    if not PLOTLY_AVAILABLE or not fig_dict:
        return ""
    
    # 将图表配置转换为JSON（转义单引号，避免HTML属性冲突）
    chart_json = json.dumps(fig_dict, cls=PlotlyJSONEncoder, ensure_ascii=False)
    # 转义单引号和双引号，用于HTML属性
    chart_json_escaped = chart_json.replace("'", "&#39;").replace('"', "&quot;")
    
    # 生成唯一的div ID
    import uuid
    div_id = f"plotly-chart-{uuid.uuid4().hex[:8]}"
    
    # 返回HTML字符串（使用data属性存储图表数据，前端JavaScript会读取并渲染）
    html = f"""
    <div id="{div_id}" class="plotly-chart-container" data-plotly-chart='{chart_json}' style="width:100%;height:400px;"></div>
    """
    return html


def generate_plotly_pie_chart(labels: List[str], values: List[float], title: str) -> Optional[Dict[str, Any]]:
    """
    生成Plotly饼图配置
    
    Args:
        labels: 标签列表
        values: 数值列表
        title: 图表标题
        
    Returns:
        Plotly图表配置字典
    """
    if not PLOTLY_AVAILABLE:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0,
        textinfo='label+percent',
        textposition='outside',
        hovertemplate='<b>%{{label}}</b><br>数值: %{{value}}<br>占比: %{{percent}}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, family='Arial, SimHei, sans-serif')),
        font=dict(family='Arial, SimHei, sans-serif', size=12),
        showlegend=True,
        height=400,
        hovermode='closest',
        # 优化交互体验（参考ShopDora风格）
        margin=dict(l=50, r=50, t=60, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig.to_dict()


def generate_plotly_funnel_chart(categories: List[str], values: List[float], title: str) -> Optional[Dict[str, Any]]:
    """
    生成Plotly漏斗图配置（从上到下：5星、4星、3星、2星、1星）
    
    Args:
        categories: 类别列表（按顺序，不排序）
        values: 数值列表
        title: 图表标题
        
    Returns:
        Plotly图表配置字典
    """
    if not PLOTLY_AVAILABLE:
        return None
    
    # 创建漏斗图数据
    fig = go.Figure(go.Funnel(
        y=categories,
        x=values,
        textposition="inside",
        textinfo="value+percent initial",
        hovertemplate='<b>%{{y}}</b><br>数量: %{{x}}<br>占比: %{{percentInitial}}<extra></extra>',
        marker=dict(color=values, colorscale='Blues', showscale=False)
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, family='Arial, SimHei, sans-serif')),
        font=dict(family='Arial, SimHei, sans-serif', size=12),
        height=500,
        margin=dict(l=100, r=50, t=50, b=50),
        hovermode='closest',
        # 优化交互体验（参考ShopDora风格）
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig.to_dict()


def generate_plotly_bar_chart(categories: List[str], values: List[float], title: str,
                              xlabel: str = '', ylabel: str = '', horizontal: bool = False) -> Optional[Dict[str, Any]]:
    """
    生成Plotly柱状图配置
    
    Args:
        categories: 类别列表
        values: 数值列表
        title: 图表标题
        xlabel: X轴标签
        ylabel: Y轴标签
        horizontal: 是否横向显示
        
    Returns:
        Plotly图表配置字典
    """
    if not PLOTLY_AVAILABLE:
        return None
    
    if horizontal:
        fig = go.Figure(data=[go.Bar(
            y=categories,
            x=values,
            orientation='h',
            text=values,
            textposition='outside',
            hovertemplate='<b>%{{y}}</b><br>数值: %{{x}}<extra></extra>'
        )])
        fig.update_layout(
            xaxis_title=xlabel or '数值',
            yaxis_title=ylabel or '类别'
        )
    else:
        fig = go.Figure(data=[go.Bar(
            x=categories,
            y=values,
            text=values,
            textposition='outside',
            hovertemplate='<b>%{{x}}</b><br>数值: %{{y}}<extra></extra>'
        )])
        fig.update_layout(
            xaxis_title=xlabel or '类别',
            yaxis_title=ylabel or '数值'
        )
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, family='Arial, SimHei, sans-serif')),
        font=dict(family='Arial, SimHei, sans-serif', size=12),
        height=400 if not horizontal else max(300, len(categories) * 30),
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='closest',
        # 优化交互体验（参考ShopDora风格）
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig.to_dict()


def generate_plotly_line_chart(x_data: List[str], y_data: List[float], title: str,
                                xlabel: str = '', ylabel: str = '', smooth: bool = False,
                                ylim: tuple = None) -> Optional[Dict[str, Any]]:
    """
    生成Plotly折线图配置
    
    Args:
        x_data: X轴数据
        y_data: Y轴数据
        title: 图表标题
        xlabel: X轴标签
        ylabel: Y轴标签
        smooth: 是否平滑曲线
        ylim: Y轴范围
        
    Returns:
        Plotly图表配置字典
    """
    if not PLOTLY_AVAILABLE:
        return None
    
    # 如果smooth为True，使用样条插值
    if smooth and len(x_data) > 2:
        try:
            from scipy.interpolate import make_interp_spline
            x_numeric = np.arange(len(x_data))
            x_smooth = np.linspace(0, len(x_data) - 1, 300)
            spl = make_interp_spline(x_numeric, y_data, k=min(3, len(x_data) - 1))
            y_smooth = spl(x_smooth)
            
            # 创建平滑曲线
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=x_smooth,
                y=y_smooth,
                mode='lines',
                name='平滑曲线',
                line=dict(width=2.5),
                hovertemplate='<b>时间: %{{x:.1f}}</b><br>数值: %{{y:.2f}}<extra></extra>'
            ))
            # 添加原始数据点
            fig.add_trace(go.Scatter(
                x=x_numeric,
                y=y_data,
                mode='markers',
                name='数据点',
                marker=dict(size=8),
                hovertemplate='<b>%{{text}}</b><br>数值: %{{y:.2f}}<extra></extra>',
                text=[x_data[int(i)] if i < len(x_data) else '' for i in x_numeric]
            ))
        except:
            # 如果样条插值失败，使用普通折线
            smooth = False
    
    if not smooth:
        fig = go.Figure(data=[go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines+markers',
            line=dict(width=2),
            marker=dict(size=8),
            hovertemplate='<b>%{{x}}</b><br>数值: %{{y:.2f}}<extra></extra>'
        )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, family='Arial, SimHei, sans-serif')),
        font=dict(family='Arial, SimHei, sans-serif', size=12),
        xaxis_title=xlabel or '时间',
        yaxis_title=ylabel or '数值',
        height=400,
        hovermode='x unified',
        # 优化交互体验（参考ShopDora风格）
        margin=dict(l=50, r=50, t=60, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    if ylim:
        fig.update_layout(yaxis=dict(range=ylim))
    
    return fig.to_dict()


def generate_radar_chart(categories: List[str], values: List[float], title: str) -> str:
    """
    生成雷达图
    
    Args:
        categories: 类别列表（变体名称等）
        values: 数值列表
        title: 图表标题
        
    Returns:
        base64编码的图片字符串
    """
    # 计算角度
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # 闭合图形
    
    # 数据也要闭合
    values_plot = values + values[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # 绘制雷达图
    ax.plot(angles, values_plot, 'o-', linewidth=2, color=sns.color_palette("deep")[0])
    ax.fill(angles, values_plot, alpha=0.25, color=sns.color_palette("deep")[0])
    
    # 设置标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylim(0, max(values) * 1.2 if values else 1)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    return save_chart_to_base64(fig)


def generate_bubble_chart(data: List[Dict[str, Any]], title: str,
                         xlabel: str = '价格', ylabel: str = '销量') -> str:
    """
    生成气泡图（价格-销量关系）
    
    Args:
        data: 数据列表，每个元素包含 {'variant': 变体名, 'price': 价格, 'sales': 销量, 'rating': 评分}
        title: 图表标题
        xlabel: X轴标签
        ylabel: Y轴标签
        
    Returns:
        base64编码的图片字符串
    """
    if not data:
        # 返回空图表
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', fontsize=14)
        ax.set_title(title, fontsize=16, fontweight='bold')
        return save_chart_to_base64(fig)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    prices = [d['price'] for d in data]
    sales = [d['sales'] for d in data]
    sizes = [d['sales'] * 10 for d in data]  # 气泡大小基于销量
    colors = [d.get('rating', 5) for d in data]  # 颜色基于评分
    
    scatter = ax.scatter(prices, sales, s=sizes, c=colors, alpha=0.6, 
                        cmap='viridis', edgecolors='black', linewidth=1)
    
    # 添加变体标签
    for i, d in enumerate(data):
        ax.annotate(d['variant'], (prices[i], sales[i]), 
                   fontsize=8, ha='center', va='bottom')
    
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    
    # 添加颜色条
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('评分', fontsize=10)
    
    plt.tight_layout()
    
    return save_chart_to_base64(fig)


def generate_stacked_area_chart(months: List[str], variant_data: Dict[str, List[int]], 
                               title: str) -> str:
    """
    生成堆叠面积图（变体评论数量时间趋势）
    改进：当变体很多时，使用更大的图例和更好的布局来区分变体
    
    Args:
        months: 月份列表
        variant_data: 变体数据字典，{变体名: [各月评论数列表]}
        title: 图表标题
        
    Returns:
        base64编码的图片字符串
    """
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # 准备数据
    variants = list(variant_data.keys())
    data_array = np.array([variant_data[v] for v in variants])
    
    # 生成颜色（使用更多颜色，确保区分度）
    if len(variants) <= 10:
        colors = sns.color_palette("Set2", len(variants))
    else:
        # 如果变体很多，使用更丰富的颜色调色板
        colors = sns.color_palette("husl", len(variants))
    
    # 绘制堆叠面积图
    ax.stackplot(months, *data_array, labels=variants, colors=colors, alpha=0.7)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('时间', fontsize=12)
    ax.set_ylabel('评论数量', fontsize=12)
    
    # 改进图例显示：更大的字体，更好的布局
    # 如果变体很多，使用多列显示，并放在图表外部
    if len(variants) <= 8:
        # 变体少时，图例放在图表内部
        ax.legend(loc='upper left', fontsize=10, framealpha=0.9, ncol=1)
    elif len(variants) <= 15:
        # 变体中等时，使用2列
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=9, framealpha=0.9, ncol=1)
    else:
        # 变体很多时，使用2列，放在图表外部右侧
        ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=8, framealpha=0.9, ncol=1)
    
    ax.grid(True, alpha=0.3)
    
    # 设置X轴标签
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, rotation=45, ha='right')
    
    # 调整布局，为图例留出空间
    plt.tight_layout(rect=[0, 0, 0.85 if len(variants) > 8 else 1, 1])
    
    return save_chart_to_base64(fig)


def generate_all_charts(analysis_results: Dict[str, Any], output_dir: Optional[Path] = None, use_echarts: bool = True) -> Dict[str, Any]:
    """
    生成所有图表（v1.10切换到ECharts方案，支持ECharts交互式图表和matplotlib静态图片）
    
    Args:
        analysis_results: 分析结果字典，包含所有分析数据
        output_dir: 输出目录（可选，如果提供则保存文件）
        use_echarts: 是否使用ECharts交互式图表（默认True）
        
    Returns:
        图表字典，{图表名称: ECharts图表配置字典 或 base64编码的图片字符串}
    """
    charts = {}
    
    rating_data = analysis_results.get('rating', {})
    trend_data = analysis_results.get('trend', {})
    variant_data = analysis_results.get('variant', {})
    media_data = analysis_results.get('media', {})
    
    # 1. 饼图：有效评论数占比
    if rating_data:
        valid_data = {
            '有效评论': rating_data.get('valid_reviews', 0),
            '无效评论': rating_data.get('total_reviews', 0) - rating_data.get('valid_reviews', 0)
        }
        if use_echarts and ECHARTS_AVAILABLE:
            echarts_chart = generate_echarts_pie_chart(
                list(valid_data.keys()),
                list(valid_data.values()),
                '有效评论数占比'
            )
            # 如果ECharts图表生成成功，使用ECharts；否则降级为matplotlib
            if echarts_chart:
                charts['valid_reviews_pie'] = echarts_chart
            else:
                charts['valid_reviews_pie'] = generate_pie_chart(
                    valid_data, 
                    '有效评论数占比'
                )
        else:
            charts['valid_reviews_pie'] = generate_pie_chart(
                valid_data, 
                '有效评论数占比'
            )
    
    # 2. 横向条形图：有效评论中的星级分布（从左到右：5星、4星、3星、2星、1星）
    # 只统计有效评论的星级分布，使用横向条形图更直观展示数量集中度
    if rating_data and rating_data.get('valid_rating_distribution'):
        rating_dist = rating_data['valid_rating_distribution']
        # 严格按照5星到1星的顺序排列（不按数量排序）
        categories = []
        values = []
        for star in [5, 4, 3, 2, 1]:  # 固定顺序：5星、4星、3星、2星、1星
            categories.append(f'{star}星')
            values.append(rating_dist.get(star, 0))
        if use_echarts and ECHARTS_AVAILABLE:
            # 改为横向条形图，更直观展示数量集中度
            echarts_chart = generate_echarts_bar_chart(
                categories,
                values,
                '有效评论中的星级分布',
                xlabel='评论数量',
                ylabel='星级',
                horizontal=True,  # 横向显示
                show_label=True  # 显示数值
            )
            # 如果ECharts图表生成成功，使用ECharts；否则降级为matplotlib
            if echarts_chart:
                charts['rating_distribution_funnel'] = echarts_chart
            else:
                charts['rating_distribution_funnel'] = generate_bar_chart(
                    categories,
                    values,
                    '有效评论中的星级分布',
                    xlabel='评论数量',
                    ylabel='星级',
                    horizontal=True
                )
        else:
            charts['rating_distribution_funnel'] = generate_bar_chart(
                categories,
                values,
                '有效评论中的星级分布',
                xlabel='评论数量',
                ylabel='星级',
                horizontal=True
            )
    
    # 3. 直方图：评论数量时间趋势
    trend_chart_data = get_monthly_data_for_chart(trend_data) if trend_data else {}
    if trend_chart_data.get('months'):
        if use_echarts and ECHARTS_AVAILABLE:
            echarts_chart = generate_echarts_bar_chart(
                trend_chart_data['months'],
                trend_chart_data['review_counts'],
                '评论数量时间趋势',
                xlabel='时间',
                ylabel='评论数量',
                horizontal=False,
                show_label=True  # 显示数值
            )
            if echarts_chart:
                charts['monthly_reviews_bar'] = echarts_chart
            else:
                charts['monthly_reviews_bar'] = generate_bar_chart(
                    trend_chart_data['months'],
                    trend_chart_data['review_counts'],
                    '评论数量时间趋势',
                    xlabel='时间',
                    ylabel='评论数量'
                )
        else:
            charts['monthly_reviews_bar'] = generate_bar_chart(
                trend_chart_data['months'],
                trend_chart_data['review_counts'],
                '评论数量时间趋势',
                xlabel='时间',
                ylabel='评论数量'
            )
    
    # 4. 堆叠面积图：变体评论数量时间趋势（使用ECharts）
    if trend_chart_data.get('variant_data'):
        if use_echarts and ECHARTS_AVAILABLE:
            echarts_chart = generate_echarts_stacked_area_chart(
                trend_chart_data['months'],
                trend_chart_data['variant_data'],
                '变体评论数量时间趋势',
                xlim=None  # 可以通过dataZoom调整
            )
            if echarts_chart:
                charts['variant_trend_area'] = echarts_chart
            else:
                # 降级为matplotlib
                charts['variant_trend_area'] = generate_stacked_area_chart(
                    trend_chart_data['months'],
                    trend_chart_data['variant_data'],
                    '变体评论数量时间趋势'
                )
        else:
            charts['variant_trend_area'] = generate_stacked_area_chart(
                trend_chart_data['months'],
                trend_chart_data['variant_data'],
                '变体评论数量时间趋势'
            )
    
    # 5. 曲线图：平均星级时间趋势（平滑曲线，固定纵轴4-5）
    if trend_chart_data.get('months') and trend_chart_data.get('avg_ratings'):
        if use_echarts and ECHARTS_AVAILABLE:
            echarts_chart = generate_echarts_line_chart(
                trend_chart_data['months'],
                trend_chart_data['avg_ratings'],
                '平均星级时间趋势',
                xlabel='时间',
                ylabel='平均星级',
                ylim=(4, 5),
                xlim=None  # 可以通过dataZoom调整
            )
            if echarts_chart:
                charts['rating_trend_line'] = echarts_chart
            else:
                charts['rating_trend_line'] = generate_line_chart(
                    trend_chart_data['months'],
                    trend_chart_data['avg_ratings'],
                    '平均星级时间趋势',
                    xlabel='时间',
                    ylabel='平均星级',
                    smooth=True,
                    ylim=(4, 5)
                )
        else:
            charts['rating_trend_line'] = generate_line_chart(
                trend_chart_data['months'],
                trend_chart_data['avg_ratings'],
                '平均星级时间趋势',
                xlabel='时间',
                ylabel='平均星级',
                smooth=True,
                ylim=(4, 5)
            )
    
    # 6. 雷达图：各变体评论数量（使用ECharts）
    variant_chart_data = get_variant_data_for_charts(variant_data) if variant_data else {}
    if variant_chart_data.get('variant_names') and variant_chart_data.get('review_counts'):
        # 限制变体数量（雷达图太多变体不好看）
        max_variants = 8
        variant_names = variant_chart_data['variant_names'][:max_variants]
        review_counts = variant_chart_data['review_counts'][:max_variants]
        if use_echarts and ECHARTS_AVAILABLE:
            # 获取平均星级数据（用于雷达图双指标显示）
            # 注意：必须按照variant_names的顺序获取，确保数据对应关系正确
            avg_ratings_list = []
            variant_stats = variant_data.get('variant_stats', {}) if variant_data else {}
            for vname in variant_names:
                # 从variant_stats中获取该变体的平均星级
                avg_rating = variant_stats.get(vname, {}).get('average_rating', 0)
                # 确保平均星级在有效范围内（1-5），如果为0或无效，使用默认值
                if avg_rating <= 0 or avg_rating > 5:
                    avg_rating = 0
                avg_ratings_list.append(float(avg_rating))  # 确保是float类型
            
            echarts_chart = generate_echarts_radar_chart(
                variant_names,
                review_counts,
                '各变体评论',  # 标题改为'各变体评论'
                avg_ratings=avg_ratings_list if avg_ratings_list else None  # 传入平均星级数据，支持双维度显示
            )
            if echarts_chart:
                charts['variant_radar'] = echarts_chart
            else:
                charts['variant_radar'] = generate_radar_chart(
                    variant_names,
                    review_counts,
                    '各变体评论数量'
                )
        else:
            charts['variant_radar'] = generate_radar_chart(
                variant_names,
                review_counts,
                '各变体评论数量'
            )
    
    # 7. 横向直方图：各变体平均星级（从高到低，高的在上面）
    if variant_chart_data.get('avg_ratings_variants') and variant_chart_data.get('avg_ratings'):
        # 数据已经按平均评分从高到低排序
        variants = variant_chart_data['avg_ratings_variants']
        ratings = variant_chart_data['avg_ratings']
        
        # 获取每个变体的评论总数（用于颜色渐变）
        variant_stats = variant_data.get('variant_stats', {}) if variant_data else {}
        review_counts_for_color = [variant_stats.get(v, {}).get('count', 0) for v in variants]
        
        if use_echarts and ECHARTS_AVAILABLE:
            # ECharts横向图，高的在上面（不需要反转）
            echarts_chart = generate_echarts_bar_chart(
                variants,
                ratings,
                '各变体平均星级',
                xlabel='平均星级',
                ylabel='变体',
                horizontal=True,
                show_label=True,  # 显示数值在条形末端
                color_values=review_counts_for_color if review_counts_for_color else None  # 根据评论总数设置颜色渐变
            )
            if echarts_chart:
                # 设置X轴范围为4.5-5.1
                if 'xAxis' in echarts_chart:
                    if isinstance(echarts_chart['xAxis'], dict):
                        echarts_chart['xAxis']['min'] = 4.5
                        echarts_chart['xAxis']['max'] = 5.1
                charts['variant_rating_bar'] = echarts_chart
            else:
                # matplotlib横向图需要反转顺序让高的显示在上面
                variants_reversed = list(reversed(variants))
                ratings_reversed = list(reversed(ratings))
                charts['variant_rating_bar'] = generate_bar_chart(
                    variants_reversed,
                    ratings_reversed,
                    '各变体平均星级',  # 修改标题
                    xlabel='平均星级',
                    ylabel='变体',
                    horizontal=True,
                    xlim=(4.5, 5.1)  # 横轴固定为4.5-5.1
                )
        else:
            # matplotlib横向图需要反转顺序让高的显示在上面
            variants_reversed = list(reversed(variants))
            ratings_reversed = list(reversed(ratings))
            charts['variant_rating_bar'] = generate_bar_chart(
                    variants_reversed,
                    ratings_reversed,
                    '各变体平均星级',  # 修改标题
                    xlabel='平均星级',
                    ylabel='变体',
                    horizontal=True,
                    xlim=(4.5, 5.1)  # 横轴固定为4.5-5.1
                )
    
    # 8. 气泡图：变体价格-评论数关系（使用ECharts）
    if variant_chart_data.get('price_sales_data'):
        if use_echarts and ECHARTS_AVAILABLE:
            echarts_chart = generate_echarts_scatter_chart(
                variant_chart_data['price_sales_data'],
                '变体价格-评论数关系',
                xlabel='价格',
                ylabel='评论数'
            )
            if echarts_chart:
                charts['price_sales_bubble'] = echarts_chart
            else:
                charts['price_sales_bubble'] = generate_bubble_chart(
                    variant_chart_data['price_sales_data'],
                    '价格-销量关系',
                    xlabel='价格',
                    ylabel='销量（评论数）'
                )
        else:
            charts['price_sales_bubble'] = generate_bubble_chart(
                variant_chart_data['price_sales_data'],
                '价格-销量关系',
                xlabel='价格',
                ylabel='销量（评论数）'
            )
    
    # 9. 饼图：媒体覆盖率（包含带文字评论）
    if media_data:
        total = media_data.get('total_reviews', 0)
        with_text = media_data.get('with_text', 0)
        with_image = media_data.get('with_image', 0)
        with_video = media_data.get('with_video', 0)
        # 计算无任何媒体的评论数（既无文字、也无图片、也无视频）
        no_media = total - max(with_text, with_image, with_video, 0)
        if no_media < 0:
            no_media = 0
        
        media_pie_data = {
            '带文字评论': with_text,
            '带图片': with_image,
            '带视频': with_video,
            '无媒体': no_media
        }
        if use_echarts and ECHARTS_AVAILABLE:
            echarts_chart = generate_echarts_pie_chart(
                list(media_pie_data.keys()),
                list(media_pie_data.values()),
                '媒体覆盖率'
            )
            if echarts_chart:
                charts['media_coverage_pie'] = echarts_chart
            else:
                charts['media_coverage_pie'] = generate_pie_chart(
                    media_pie_data,
                    '媒体覆盖率'
                )
        else:
            charts['media_coverage_pie'] = generate_pie_chart(
                media_pie_data,
                '媒体覆盖率'
            )
    
    return charts


# 导入辅助函数（避免循环导入）
def get_monthly_data_for_chart(trend_data: Dict[str, Any]) -> Dict[str, List]:
    """从trend模块导入"""
    from backend.analyzer.trend import get_monthly_data_for_chart as _get_monthly_data
    return _get_monthly_data(trend_data)


def get_variant_data_for_charts(variant_data: Dict[str, Any]) -> Dict[str, Any]:
    """从variant模块导入"""
    from backend.analyzer.variant import get_variant_data_for_charts as _get_variant_data
    return _get_variant_data(variant_data)

