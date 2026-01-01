"""
Excel文件解析模块
智能识别表头，读取Excel数据
"""

import pandas as pd
from typing import Dict, List, Optional, Any
import io


# 定义列名映射表（支持多种可能的列名变体）
COLUMN_MAPPING = {
    '评论人': ['评论人', 'reviewer', 'reviewer_name', '用户', '用户名'],
    '评论内容': ['评论内容', 'review', 'review_content', '内容', '评价内容'],
    '星级': ['星级', 'rating', 'star', 'stars', '评分', 'star_rating'],
    '变体': ['变体', 'variant', 'sku', '规格', '产品变体'],
    '变体价格': ['变体价格', 'price', 'variant_price', '价格', 'product_price'],
    '图片链接': ['图片链接', 'image', 'image_url', '图片', 'image_link'],
    '视频链接': ['视频链接', 'video', 'video_url', '视频', 'video_link', '视频链接链接'],
    '评论时间': ['评论时间', 'review_time', 'time', '时间', '评论日期', 'date']
}


def find_column_index(header_row: List[str], target_columns: List[str]) -> Optional[int]:
    """
    在表头行中查找目标列的索引
    
    Args:
        header_row: 表头行（列名列表）
        target_columns: 目标列名的可能变体列表
        
    Returns:
        找到的列索引，如果未找到返回None
    """
    header_lower = [str(col).strip().lower() if col else '' for col in header_row]
    
    # 第一轮：优先精确匹配
    for target in target_columns:
        target_lower = target.lower().strip()
        for idx, header in enumerate(header_lower):
            # 精确匹配优先
            if target_lower == header:
                return idx
    
    # 第二轮：部分匹配（当目标字符串包含在表头中时）
    # 但要避免短字符串匹配到长字符串（如"变体"匹配到"变体价格"）
    for target in target_columns:
        target_lower = target.lower().strip()
        for idx, header in enumerate(header_lower):
            # 只有当目标字符串是表头字符串的子串，且长度差异不超过2个字符时，才匹配
            # 这样可以避免"变体"匹配到"变体价格"
            if target_lower in header and target_lower != header:
                # 如果目标字符串太短，且表头字符串太长，则不匹配
                # 例如："变体"（2字符）不应该匹配"变体价格"（4字符）
                if len(target_lower) <= 2 and len(header) - len(target_lower) > 2:
                    continue
                return idx
    
    # 第三轮：反向匹配（当表头字符串包含在目标中时）
    # 用于处理"价格"匹配"变体价格"的情况
    for target in target_columns:
        target_lower = target.lower().strip()
        for idx, header in enumerate(header_lower):
            if header in target_lower and header != target_lower:
                # 只有当表头字符串是目标字符串的前缀时，才匹配
                # 例如："价格"可以匹配"变体价格"，因为"价格"是"变体价格"的后缀
                if target_lower.endswith(header) or target_lower.startswith(header):
                    return idx
    
    return None


def map_columns(df: pd.DataFrame) -> Dict[str, Optional[int]]:
    """
    智能映射Excel列到标准列名
    
    Args:
        df: pandas DataFrame
        
    Returns:
        列名到索引的映射字典
    """
    column_mapping = {}
    header_row = list(df.columns)
    
    for standard_name, possible_names in COLUMN_MAPPING.items():
        idx = find_column_index(header_row, possible_names)
        column_mapping[standard_name] = idx
    
    return column_mapping


def parse_excel(file_path: Optional[str] = None, file_content: Optional[bytes] = None) -> Dict[str, Any]:
    """
    解析Excel文件
    
    Args:
        file_path: Excel文件路径（如果提供文件路径）
        file_content: Excel文件内容（字节流，如果从内存读取）
        
    Returns:
        包含解析后数据的字典
        {
            'data': DataFrame,
            'column_mapping': 列映射字典,
            'total_rows': 总行数,
            'columns_found': 找到的列列表
        }
    """
    # 读取Excel文件
    if file_path:
        df = pd.read_excel(file_path)
    elif file_content:
        df = pd.read_excel(io.BytesIO(file_content))
    else:
        raise ValueError("必须提供 file_path 或 file_content 参数")
    
    # 智能识别列
    column_mapping = map_columns(df)
    
    # 重新组织数据，使用标准列名
    standard_data = {}
    columns_found = []
    
    for standard_name, original_idx in column_mapping.items():
        if original_idx is not None:
            original_col_name = df.columns[original_idx]
            standard_data[standard_name] = df[original_col_name].values
            columns_found.append(standard_name)
        else:
            # 如果列未找到，创建空列
            standard_data[standard_name] = [None] * len(df)
    
    # 创建标准化的DataFrame
    result_df = pd.DataFrame(standard_data)
    
    # 数据清洗
    result_df = clean_data(result_df)
    
    return {
        'data': result_df,
        'column_mapping': column_mapping,
        'total_rows': len(result_df),
        'columns_found': columns_found,
        'original_columns': list(df.columns)
    }


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    清洗数据：处理空值、数据类型转换等
    
    Args:
        df: 原始DataFrame
        
    Returns:
        清洗后的DataFrame
    """
    df = df.copy()
    
    # 处理星级：确保是整数，范围1-5
    if '星级' in df.columns:
        df['星级'] = pd.to_numeric(df['星级'], errors='coerce')
        df['星级'] = df['星级'].fillna(0).astype(int)
        # 限制范围在1-5
        df['星级'] = df['星级'].clip(1, 5)
    
    # 处理评论时间：转换为datetime类型
    if '评论时间' in df.columns:
        df['评论时间'] = pd.to_datetime(df['评论时间'], errors='coerce', format='%Y-%m-%d %H:%M:%S')
    
    # 处理变体价格：提取数字部分（去除货币符号）
    if '变体价格' in df.columns:
        # 重要：先处理'变体价格'列的空值，确保后续能正确提取价格
        # 将NaN转换为空字符串，但保留原始价格字符串（用于显示）
        df['变体价格'] = df['变体价格'].fillna('')  # NaN填充为空字符串
        df['变体价格'] = df['变体价格'].astype(str).replace('nan', '')  # 将字符串'nan'替换为空字符串
        
        # 保留原始价格字符串，同时提取数值（用于数值计算）
        df['价格数值'] = df['变体价格'].astype(str).str.extract(r'([\d,]+\.?\d*)')[0]
        # 处理空值和无效值
        df['价格数值'] = df['价格数值'].str.replace(',', '')
        df['价格数值'] = pd.to_numeric(df['价格数值'], errors='coerce')
    
    # 处理图片链接和视频链接：空值处理
    for col in ['图片链接', '视频链接']:
        if col in df.columns:
            df[col] = df[col].fillna('')
            # 将NaN转换为空字符串
            df[col] = df[col].astype(str).replace('nan', '')
    
    # 处理评论内容：空值处理
    if '评论内容' in df.columns:
        df['评论内容'] = df['评论内容'].fillna('')
        df['评论内容'] = df['评论内容'].astype(str).replace('nan', '')
    
    return df


def validate_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    验证数据完整性
    
    Args:
        df: DataFrame
        
    Returns:
        验证结果字典
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }
    
    # 检查必需列是否存在
    required_columns = ['评论人', '星级', '评论时间']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        validation_result['is_valid'] = False
        validation_result['errors'].append(f"缺少必需列: {", ".join(missing_columns)}")
    
    # 检查星级数据
    if '星级' in df.columns:
        invalid_ratings = df[(df['星级'] < 1) | (df['星级'] > 5)]
        if len(invalid_ratings) > 0:
            validation_result['warnings'].append(f"发现 {len(invalid_ratings)} 条无效星级数据")
    
    # 检查数据行数
    if len(df) == 0:
        validation_result['is_valid'] = False
        validation_result['errors'].append("数据文件为空")
    
    return validation_result

