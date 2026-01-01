"""
变体分析模块
分析各变体的评论数量、平均评分、价格分布等
"""

import pandas as pd
from typing import Dict, Any, List


def analyze_variant(df: pd.DataFrame) -> Dict[str, Any]:
    """
    变体分析
    
    Args:
        df: 包含评论数据的DataFrame
        
    Returns:
        分析结果字典
        {
            'variant_stats': 各变体统计信息,
            'variant_list': 变体列表
        }
    """
    result = {}
    
    if '变体' not in df.columns:
        return {
            'variant_stats': {},
            'variant_list': []
        }
    
    # 移除变体为空的行
    df = df[df['变体'].notna()]
    df = df[df['变体'].astype(str).str.strip() != '']
    
    if len(df) == 0:
        return {
            'variant_stats': {},
            'variant_list': []
        }
    
    variant_list = df['变体'].unique().tolist()
    result['variant_list'] = [str(v) for v in variant_list]
    
    variant_stats = {}
    
    for variant in variant_list:
        variant_df = df[df['变体'] == str(variant)]
        
        stats = {
            'count': len(variant_df),  # 评论数量
            'average_rating': 0,  # 平均评分
            'price': None,  # 价格
            'price_numeric': None,  # 价格数值
            'image_url': None  # 图片链接
        }
        
        # 平均评分：星级总和/总评论数量
        # 确保计算逻辑明确：只计算有效星级（1-5范围内），排除NaN和无效值
        if '星级' in variant_df.columns:
            ratings = variant_df['星级']
            # 过滤有效值：排除NaN，只保留1-5范围内的值
            valid_ratings = ratings.dropna()
            valid_ratings = valid_ratings[(valid_ratings >= 1) & (valid_ratings <= 5)]
            
            if len(valid_ratings) > 0:
                # 计算：星级总和 / 总评论数量（使用有效值）
                total_sum = valid_ratings.sum()
                total_count = len(valid_ratings)
                stats['average_rating'] = round(total_sum / total_count, 1)  # 保留1位小数
            else:
                stats['average_rating'] = 0.0
        
        # 价格（从'变体价格'字段获取，文本形式）
        # 当'变体'列的值等于变体名称时，取对应行的'变体价格'字段
        if '变体价格' in variant_df.columns:
            # 获取'变体价格'列的所有值（包括空字符串）
            prices_series = variant_df['变体价格']
            
            # 如果有多个价格，按评论时间排序取最新的
            if len(prices_series) > 1 and '评论时间' in variant_df.columns:
                try:
                    # 创建临时DataFrame用于排序
                    temp_df = variant_df[['变体价格', '评论时间']].copy()
                    temp_df['评论时间'] = pd.to_datetime(temp_df['评论时间'], errors='coerce')
                    # 按时间降序排序（最新的在前）
                    temp_df = temp_df.sort_values('评论时间', ascending=False, na_position='last')
                    prices_series = temp_df['变体价格']
                except:
                    # 如果排序失败，使用原始数据
                    pass
            
            # 过滤空值：包括空字符串和'nan'字符串
            # 先转换为字符串，然后过滤掉空值和无效值
            prices_str = prices_series.astype(str)
            prices_str = prices_str[prices_str.str.strip() != '']  # 过滤空字符串
            prices_str = prices_str[prices_str.str.strip().str.lower() != 'nan']  # 过滤'nan'字符串
            prices_str = prices_str[prices_str.str.strip() != 'None']  # 过滤'None'字符串
            
            # 获取第一个有效价格
            if len(prices_str) > 0:
                # 取第一个价格，已经是字符串形式
                price_str = prices_str.iloc[0].strip()
                
                # 验证：确保不是空值、无效值，并且不等于变体名称
                # 如果价格等于变体名称，说明可能取错了字段，返回None
                if (price_str and 
                    price_str.lower() not in ['nan', 'none', ''] and 
                    price_str != str(variant) and
                    price_str != 'None'):
                    stats['price'] = price_str
                else:
                    stats['price'] = None
            else:
                stats['price'] = None
        else:
            stats['price'] = None
        
        # 价格数值（如果有多个价格，按评论时间排序取最新的）
        if '价格数值' in variant_df.columns:
            prices_numeric_df = variant_df[['价格数值']].copy()
            # 如果有评论时间字段，按时间排序取最新的价格
            if '评论时间' in variant_df.columns:
                try:
                    prices_numeric_df['评论时间'] = pd.to_datetime(variant_df['评论时间'], errors='coerce')
                    prices_numeric_df = prices_numeric_df.sort_values('评论时间', ascending=False, na_position='last')
                except:
                    pass
            prices_numeric = prices_numeric_df['价格数值'].dropna()
            if len(prices_numeric) > 0:
                stats['price_numeric'] = float(prices_numeric.iloc[0])
        
        # 图片链接（如果有多个链接用逗号分隔，只取第一个）
        if '图片链接' in variant_df.columns:
            image_links = variant_df['图片链接'].dropna()
            image_links = image_links[image_links.astype(str).str.strip() != '']
            if len(image_links) > 0:
                # 取第一个图片链接
                first_link = str(image_links.iloc[0])
                # 如果链接中包含逗号，只取第一个（处理多个链接的情况）
                if ',' in first_link:
                    first_link = first_link.split(',')[0].strip()
                stats['image_url'] = first_link
        
        variant_stats[str(variant)] = stats
    
    result['variant_stats'] = variant_stats
    
    return result


def get_variant_data_for_charts(variant_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    将变体数据转换为图表所需格式
    
    Args:
        variant_data: analyze_variant返回的数据
        
    Returns:
        图表数据格式
        {
            'variant_names': 变体名称列表,
            'review_counts': 评论数量列表,
            'avg_ratings': 平均评分列表,
            'prices': 价格列表,
            'price_sales_data': 价格-销量数据（用于气泡图）
        }
    """
    variant_stats = variant_data.get('variant_stats', {})
    
    if not variant_stats:
        return {
            'variant_names': [],
            'review_counts': [],
            'avg_ratings': [],
            'prices': [],
            'price_sales_data': []
        }
    
    # 按评论数量排序
    sorted_variants = sorted(
        variant_stats.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )
    
    variant_names = [v[0] for v in sorted_variants]
    review_counts = [v[1]['count'] for v in sorted_variants]
    avg_ratings = [v[1]['average_rating'] for v in sorted_variants]
    prices = [v[1].get('price', '') for v in sorted_variants]
    
    # 价格-销量数据（用于气泡图）
    price_sales_data = []
    for variant, stats in sorted_variants:
        if stats.get('price_numeric') is not None:
            price_sales_data.append({
                'variant': variant,
                'price': stats['price_numeric'],
                'sales': stats['count'],
                'rating': stats['average_rating']
            })
    
    # 按平均评分排序（用于横向直方图）
    sorted_by_rating = sorted(
        variant_stats.items(),
        key=lambda x: x[1]['average_rating'],
        reverse=True
    )
    
    return {
        'variant_names': variant_names,
        'review_counts': review_counts,
        'avg_ratings': [v[1]['average_rating'] for v in sorted_by_rating],
        'avg_ratings_variants': [v[0] for v in sorted_by_rating],
        'prices': prices,
        'price_sales_data': price_sales_data
    }

