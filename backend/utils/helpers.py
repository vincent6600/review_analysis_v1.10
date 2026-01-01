"""
工具函数模块
提供各种辅助功能
"""

from typing import Any, Dict
from datetime import datetime


def format_number(num: float, decimals: int = 2) -> str:
    """
    格式化数字
    
    Args:
        num: 数字
        decimals: 小数位数
        
    Returns:
        格式化后的字符串
    """
    return f"{num:.{decimals}f}"


def format_percentage(num: float, decimals: int = 2) -> str:
    """
    格式化百分比
    
    Args:
        num: 数字（0-100）
        decimals: 小数位数
        
    Returns:
        格式化后的百分比字符串
    """
    return f"{num:.{decimals}f}%"


def get_timestamp() -> str:
    """
    获取当前时间戳字符串
    
    Returns:
        时间戳字符串 (YYYYMMDDHHmmss)
    """
    return datetime.now().strftime('%Y%m%d%H%M%S')


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    安全获取字典值
    
    Args:
        data: 字典
        key: 键
        default: 默认值
        
    Returns:
        值或默认值
    """
    return data.get(key, default)

