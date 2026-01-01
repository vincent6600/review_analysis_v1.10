"""
PDF报告生成模块
基于HTML生成PDF报告
"""

from typing import Dict, Any
from pathlib import Path
import io

# 延迟导入weasyprint，避免启动时卡住
WEASYPRINT_AVAILABLE = False

def _check_weasyprint():
    """检查weasyprint是否可用（延迟检查）"""
    global WEASYPRINT_AVAILABLE
    if WEASYPRINT_AVAILABLE:
        return True
    try:
        from weasyprint import HTML, CSS
        WEASYPRINT_AVAILABLE = True
        return True
    except (ImportError, OSError):
        WEASYPRINT_AVAILABLE = False
        return False


def generate_pdf_report(html_content: str, output_path: str = None) -> bytes:
    """
    从HTML内容生成PDF
    
    Args:
        html_content: HTML内容字符串
        output_path: 输出文件路径（可选）
        
    Returns:
        PDF文件的字节内容
    """
    # 延迟检查weasyprint
    if not _check_weasyprint():
        raise ImportError("weasyprint未安装或系统依赖缺失，无法生成PDF。请安装weasyprint系统依赖")
    
    # 延迟导入
    from weasyprint import HTML, CSS
    
    # 生成PDF
    html_doc = HTML(string=html_content)
    
    # 添加CSS样式优化
    css = CSS(string=""
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', 'SimHei', Arial, sans-serif;
        }
        .chart-container img {
            max-width: 100%;
            page-break-inside: avoid;
        }
        .section {
            page-break-inside: avoid;
        }
    """)
    
    if output_path:
        html_doc.write_pdf(output_path, stylesheets=[css])
        with open(output_path, 'rb') as f:
            return f.read()
    else:
        # 返回PDF字节内容
        pdf_bytes = html_doc.write_pdf(stylesheets=[css])
        return pdf_bytes


def save_pdf_report(html_content: str, file_info: Dict[str, Any], output_dir: Path) -> Path:
    """
    保存PDF报告到文件
    
    Args:
        html_content: HTML内容
        file_info: 文件信息字典
        output_dir: 输出目录
        
    Returns:
        保存的文件路径
    """
    from datetime import datetime
    
    site = file_info.get('site', '未知站点')
    product_id = file_info.get('product_id', '未知')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # 生成文件名
    filename = f"{site}_产品ID_{product_id}_分析报告_{timestamp}.pdf"
    output_path = output_dir / filename
    
    # 确保目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成PDF
    generate_pdf_report(html_content, str(output_path))
    
    return output_path

