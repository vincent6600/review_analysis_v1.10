"""
文件名解析模块
从文件名中提取站点、产品ID、下载时间等信息
"""

import re
from datetime import datetime
from typing import Dict, Optional


def parse_filename(filename: str) -> Dict[str, Optional[str]]:
    """
    解析文件名，提取站点、产品ID、下载时间
    
    文件名格式：{站点}(产品id={产品ID})评论下载{时间戳}.xlsx
    例如：菲律宾(产品id=29180013510)评论下载20251230080704.xlsx
    
    Args:
        filename: 文件名（可以包含路径）
        
    Returns:
        包含站点、产品ID、下载时间的字典
        {
            'site': '菲律宾',
            'product_id': '29180013510',
            'download_time': '2025-12-30 08:07:04',
            'download_timestamp': '20251230080704'
        }
    """
    # 提取文件名（去除路径）
    import os
    basename = os.path.basename(filename)
    
    # 定义正则表达式模式
    # 匹配格式：{站点}(产品id={产品ID})评论下载{时间戳}.xlsx
    pattern = r'^(.+?)\(产品id=(\d+)\)评论下载(\d{14})\.xlsx$'
    
    match = re.match(pattern, basename)
    
    if not match:
        # 如果匹配失败，返回None值
        return {
            'site': None,
            'product_id': None,
            'download_time': None,
            'download_timestamp': None
        }
    
    site = match.group(1)  # 站点名称
    product_id = match.group(2)  # 产品ID
    timestamp_str = match.group(3)  # 时间戳字符串
    
    # 解析时间戳：格式为 YYYYMMDDHHmmss
    try:
        download_time = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
        download_time_str = download_time.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        download_time_str = None
    
    return {
        'site': site,
        'product_id': product_id,
        'download_time': download_time_str,
        'download_timestamp': timestamp_str
    }


def extract_file_info(file_path: str) -> Dict[str, any]:
    """
    从文件路径提取完整信息（包括文件大小等）
    
    Args:
        file_path: 文件完整路径
        
    Returns:
        包含文件信息的字典
    """
    import os
    
    filename_info = parse_filename(file_path)
    
    # 获取文件大小
    try:
        file_size = os.path.getsize(file_path)
        file_size_mb = round(file_size / (1024 * 1024), 2)
    except OSError:
        file_size = None
        file_size_mb = None
    
    return {
        **filename_info,
        'file_path': file_path,
        'file_name': os.path.basename(file_path),
        'file_size': file_size,
        'file_size_mb': file_size_mb
    }

