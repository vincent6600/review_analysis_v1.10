"""
时间趋势分析模块
分析评论数量、变体评论数量、平均星级随时间的变化
"""

import pandas as pd
from typing import Dict, Any, List
from datetime import datetime


def analyze_trend(df: pd.DataFrame) -> Dict[str, Any]:
    """
    时间趋势分析（按月统计）
    
    Args:
        df: 包含评论数据的DataFrame
        
    Returns:
        分析结果字典
        {
            'monthly_reviews': 月度评论数量,
            'monthly_rating': 月度平均星级,
            'variant_monthly_reviews': 各变体月度评论数量
        }
    """
    result = {}
    
    # 确保评论时间列存在且为datetime类型
    if '评论时间' not in df.columns:
        return {
            'monthly_reviews': {},
            'monthly_rating': {},
            'variant_monthly_reviews': {}
        }
    
    # 转换为datetime类型（如果还不是）
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['评论时间']):
        df['评论时间'] = pd.to_datetime(df['评论时间'], errors='coerce')
    
    # 移除无效时间
    df = df[df['评论时间'].notna()]
    
    if len(df) == 0:
        return {
            'monthly_reviews': {},
            'monthly_rating': {},
            'variant_monthly_reviews': {}
        }
    
    # 添加年月列
    df['年月'] = df['评论时间'].dt.to_period('M')
    df['年月_str'] = df['年月'].astype(str)
    
    # 1. 月度评论数量
    monthly_counts = df.groupby('年月_str').size().to_dict()
    result['monthly_reviews'] = {k: int(v) for k, v in monthly_counts.items()}
    
    # 2. 月度平均星级
    if '星级' in df.columns:
        monthly_rating = df.groupby('年月_str')['星级'].mean().to_dict()
        result['monthly_rating'] = {k: round(v, 2) for k, v in monthly_rating.items()}
    else:
        result['monthly_rating'] = {}
    
    # 3. 各变体月度评论数量
    if '变体' in df.columns:
        variant_monthly = {}
        for variant in df['变体'].unique():
            if pd.notna(variant):
                variant_df = df[df['变体'] == variant]
                variant_monthly_counts = variant_df.groupby('年月_str').size().to_dict()
                variant_monthly[str(variant)] = {k: int(v) for k, v in variant_monthly_counts.items()}
        result['variant_monthly_reviews'] = variant_monthly
    else:
        result['variant_monthly_reviews'] = {}
    
    return result


def get_monthly_data_for_chart(trend_data: Dict[str, Any]) -> Dict[str, List]:
    """
    将趋势数据转换为图表所需格式
    
    Args:
        trend_data: analyze_trend返回的数据
        
    Returns:
        图表数据格式
        {
            'months': 月份列表,
            'review_counts': 评论数量列表,
            'avg_ratings': 平均星级列表,
            'variant_data': 变体数据字典
        }
    """
    monthly_reviews = trend_data.get('monthly_reviews', {})
    monthly_rating = trend_data.get('monthly_rating', {})
    variant_monthly = trend_data.get('variant_monthly_reviews', {})
    
    # 获取所有月份（排序）
    all_months = sorted(set(list(monthly_reviews.keys()) + list(monthly_rating.keys())))
    
    # 构建数据列表
    review_counts = [monthly_reviews.get(month, 0) for month in all_months]
    avg_ratings = [monthly_rating.get(month, 0) for month in all_months]
    
    # 变体数据
    variant_data = {}
    for variant, monthly_data in variant_monthly.items():
        variant_data[variant] = [monthly_data.get(month, 0) for month in all_months]
    
    return {
        'months': all_months,
        'review_counts': review_counts,
        'avg_ratings': avg_ratings,
        'variant_data': variant_data
    }

