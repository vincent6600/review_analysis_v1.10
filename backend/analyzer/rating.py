"""
整体评分分析模块
分析总评论数、有效评论数、平均星级、好评率等
"""

import pandas as pd
from typing import Dict, Any


def analyze_rating(df: pd.DataFrame) -> Dict[str, Any]:
    """
    整体评分分析
    
    Args:
        df: 包含评论数据的DataFrame
        
    Returns:
        分析结果字典
        {
            'total_reviews': 总评论数,
            'valid_reviews': 有效评论数,
            'valid_reviews_ratio': 有效评论比例,
            'average_rating': 平均星级,
            'rating_distribution': 星级分布,
            'positive_rate': 好评率(4-5星占比),
            'top_variant': 热销变体
        }
    """
    result = {}
    
    # 总评论数
    result['total_reviews'] = len(df)
    
    # 有效评论数（评论内容不为空）
    if '评论内容' in df.columns:
        valid_mask = df['评论内容'].astype(str).str.strip() != ''
        valid_reviews = df[valid_mask]
        result['valid_reviews'] = len(valid_reviews)
        result['valid_reviews_ratio'] = round(result['valid_reviews'] / result['total_reviews'] * 100, 2) if result['total_reviews'] > 0 else 0
    else:
        result['valid_reviews'] = 0
        result['valid_reviews_ratio'] = 0
    
    # 平均星级（基于所有评论）
    if '星级' in df.columns:
        result['average_rating'] = round(df['星级'].mean(), 2)
        
        # 星级分布（基于所有评论）
        rating_dist = df['星级'].value_counts().sort_index().to_dict()
        # 确保所有星级都有值（1-5）
        result['rating_distribution'] = {i: rating_dist.get(i, 0) for i in range(1, 6)}
        
        # 有效评论中的星级分布（只统计有效评论）
        if '评论内容' in df.columns and result['valid_reviews'] > 0:
            valid_reviews_df = df[valid_mask]
            valid_rating_dist = valid_reviews_df['星级'].value_counts().sort_index().to_dict()
            result['valid_rating_distribution'] = {i: valid_rating_dist.get(i, 0) for i in range(1, 6)}
        else:
            result['valid_rating_distribution'] = {i: 0 for i in range(1, 6)}
        
        # 好评率（4-5星占比）
        positive_reviews = df[df['星级'].isin([4, 5])]
        result['positive_rate'] = round(len(positive_reviews) / result['total_reviews'] * 100, 2) if result['total_reviews'] > 0 else 0
    else:
        result['average_rating'] = 0
        result['rating_distribution'] = {i: 0 for i in range(1, 6)}
        result['valid_rating_distribution'] = {i: 0 for i in range(1, 6)}
        result['positive_rate'] = 0
    
    # 热销变体（评论数最高的变体）
    if '变体' in df.columns:
        variant_counts = df['变体'].value_counts()
        if len(variant_counts) > 0:
            top_variant_name = variant_counts.index[0]
            result['top_variant'] = top_variant_name
            result['top_variant_count'] = int(variant_counts.iloc[0])
            
            # 获取热销变体的图片链接（取第一个非空图片链接，如果有多个链接用逗号分隔，只取第一个）
            top_variant_df = df[df['变体'] == top_variant_name]
            if '图片链接' in top_variant_df.columns:
                image_links = top_variant_df['图片链接'].dropna()
                image_links = image_links[image_links.astype(str).str.strip() != '']
                image_links = image_links[image_links.astype(str).str.strip().str.lower() != 'nan']
                if len(image_links) > 0:
                    first_link = str(image_links.iloc[0]).strip()
                    # 如果链接中包含逗号，只取第一个（处理多个链接的情况）
                    if ',' in first_link:
                        first_link = first_link.split(',')[0].strip()
                    result['top_variant_image'] = first_link
                else:
                    result['top_variant_image'] = None
            else:
                result['top_variant_image'] = None
        else:
            result['top_variant'] = None
            result['top_variant_count'] = 0
            result['top_variant_image'] = None
    else:
        result['top_variant'] = None
        result['top_variant_count'] = 0
        result['top_variant_image'] = None
    
    return result

