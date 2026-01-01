"""
媒体内容分析模块
分析带图片和视频的评论占比
"""

import pandas as pd
from typing import Dict, Any


def analyze_media(df: pd.DataFrame) -> Dict[str, Any]:
    """
    媒体内容分析
    
    Args:
        df: 包含评论数据的DataFrame
        
    Returns:
        分析结果字典
        {
            'total_reviews': 总评论数,
            'with_image': 带图片评论数,
            'with_image_ratio': 带图片评论占比,
            'with_video': 带视频评论数,
            'with_video_ratio': 带视频评论占比,
            'with_media': 带媒体（图片或视频）评论数,
            'with_media_ratio': 带媒体评论占比
        }
    """
    result = {}
    
    total = len(df)
    result['total_reviews'] = total
    
    if total == 0:
        result['with_text'] = 0
        result['with_text_ratio'] = 0
        result['with_image'] = 0
        result['with_image_ratio'] = 0
        result['with_video'] = 0
        result['with_video_ratio'] = 0
        result['with_media'] = 0
        result['with_media_ratio'] = 0
        return result
    
    # 带文字评论（评论内容不为空）
    if '评论内容' in df.columns:
        text_mask = df['评论内容'].astype(str).str.strip() != ''
        with_text = text_mask.sum()
        result['with_text'] = int(with_text)
        result['with_text_ratio'] = round(with_text / total * 100, 2)
    else:
        result['with_text'] = 0
        result['with_text_ratio'] = 0
    
    # 带图片评论
    if '图片链接' in df.columns:
        # 检查图片链接是否为空（去除空字符串、NaN等）
        image_mask = df['图片链接'].astype(str).str.strip().isin(['', 'nan', 'None'])
        with_image = (~image_mask).sum()
        result['with_image'] = int(with_image)
        result['with_image_ratio'] = round(with_image / total * 100, 2)
    else:
        result['with_image'] = 0
        result['with_image_ratio'] = 0
    
    # 带视频评论
    if '视频链接' in df.columns:
        # 检查视频链接是否为空
        video_mask = df['视频链接'].astype(str).str.strip().isin(['', 'nan', 'None'])
        with_video = (~video_mask).sum()
        result['with_video'] = int(with_video)
        result['with_video_ratio'] = round(with_video / total * 100, 2)
    else:
        result['with_video'] = 0
        result['with_video_ratio'] = 0
    
    # 带媒体（图片或视频）评论
    if '图片链接' in df.columns and '视频链接' in df.columns:
        image_mask = df['图片链接'].astype(str).str.strip().isin(['', 'nan', 'None'])
        video_mask = df['视频链接'].astype(str).str.strip().isin(['', 'nan', 'None'])
        with_media = ((~image_mask) | (~video_mask)).sum()
        result['with_media'] = int(with_media)
        result['with_media_ratio'] = round(with_media / total * 100, 2)
    elif '图片链接' in df.columns:
        result['with_media'] = result['with_image']
        result['with_media_ratio'] = result['with_image_ratio']
    elif '视频链接' in df.columns:
        result['with_media'] = result['with_video']
        result['with_media_ratio'] = result['with_video_ratio']
    else:
        result['with_media'] = 0
        result['with_media_ratio'] = 0
    
    return result

