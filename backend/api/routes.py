"""
Flask API路由
提供文件上传、数据分析和PDF导出接口
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
import sys
from pathlib import Path
import io
import traceback

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.parser.excel_parser import parse_excel, validate_data
from backend.parser.filename_parser import parse_filename
from backend.analyzer.rating import analyze_rating
from backend.analyzer.trend import analyze_trend
from backend.analyzer.variant import analyze_variant
from backend.analyzer.media import analyze_media
from backend.chart.chart_generator import generate_all_charts
from backend.report.html_generator import generate_html_report

# 延迟导入PDF模块，避免启动时卡住
WEASYPRINT_AVAILABLE = False
def generate_pdf_report(*args, **kwargs):
    """延迟加载PDF生成功能"""
    try:
        from backend.report.pdf_generator import generate_pdf_report as _generate_pdf
        return _generate_pdf(*args, **kwargs)
    except Exception as e:
        raise ImportError(f"PDF生成功能不可用: {str(e)}")


def create_routes(app: Flask):
    """
    创建API路由
    
    Args:
        app: Flask应用实例
    """
    
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """
        文件上传接口
        接收Excel文件，返回分析结果
        """
        try:
            # 检查文件是否存在
            if 'file' not in request.files:
                return jsonify({'error': '没有上传文件'}), 400
            
            file = request.files['file']
            
            # 检查文件名
            if file.filename == '':
                return jsonify({'error': '文件名为空'}), 400
            
            # 检查文件类型
            if not file.filename.endswith('.xlsx'):
                return jsonify({'error': '文件格式不正确，请上传.xlsx格式文件'}), 400
            
            # 读取文件内容到内存（不保存到磁盘）
            file_content = file.read()
            
            # 检查文件大小（100MB限制）
            if len(file_content) > 100 * 1024 * 1024:
                return jsonify({'error': '文件大小超过100MB限制，请上传较小的文件'}), 400
            
            # 解析文件名
            file_info = parse_filename(file.filename)
            
            # 解析Excel文件
            parse_result = parse_excel(file_content=file_content)
            df = parse_result['data']
            
            # 数据验证
            validation = validate_data(df)
            if not validation['is_valid']:
                return jsonify({
                    'error': '数据验证失败',
                    'errors': validation['errors'],
                    'warnings': validation['warnings']
                }), 400
            
            # 执行所有分析
            rating_result = analyze_rating(df)
            trend_result = analyze_trend(df)
            variant_result = analyze_variant(df)
            media_result = analyze_media(df)
            
            # 生成图表
            analysis_results = {
                'rating': rating_result,
                'trend': trend_result,
                'variant': variant_result,
                'media': media_result
            }
            # v1.10切换到ECharts交互式图表（简约商务风格，更好的交互体验）
            charts = generate_all_charts(analysis_results, use_echarts=True)
            analysis_results['charts'] = charts
            
            # 生成HTML报告
            html_content = generate_html_report(analysis_results, file_info)
            
            # 返回结果
            return jsonify({
                'success': True,
                'file_info': file_info,
                'analysis': {
                    'rating': rating_result,
                    'trend': trend_result,
                    'variant': variant_result,
                    'media': media_result
                },
                'charts': charts,
                'html_report': html_content,
                'warnings': validation.get('warnings', [])
            })
            
        except Exception as e:
            error_msg = str(e)
            error_traceback = traceback.format_exc()
            # 打印详细错误信息到控制台（方便调试）
            print("=" * 60)
            print("文件上传处理失败:")
            print(error_msg)
            print("-" * 60)
            print("详细错误信息:")
            print(error_traceback)
            print("=" * 60)
            app.logger.error(f"文件上传处理失败: {error_msg}\n{error_traceback}")
            return jsonify({
                'error': '处理失败',
                'message': error_msg,
                'detail': error_traceback if app.debug else None
            }), 500
    
    @app.route('/api/export/pdf', methods=['POST'])
    def export_pdf():
        """
        PDF导出接口
        接收HTML内容，返回PDF文件
        """
        try:
            # 动态检查weasyprint是否可用
            try:
                from backend.report.pdf_generator import WEASYPRINT_AVAILABLE as _available
                if not _available:
                    return jsonify({'error': 'PDF生成功能不可用，请安装weasyprint系统依赖'}), 503
            except:
                return jsonify({'error': 'PDF生成功能不可用，请安装weasyprint系统依赖'}), 503
            
            data = request.get_json()
            if not data or 'html_content' not in data:
                return jsonify({'error': '缺少HTML内容'}), 400
            
            html_content = data['html_content']
            
            # 生成PDF
            pdf_bytes = generate_pdf_report(html_content)
            
            # 返回PDF文件
            return send_file(
                io.BytesIO(pdf_bytes),
                mimetype='application/pdf',
                as_attachment=True,
                download_name='analysis_report.pdf'
            )
            
        except Exception as e:
            error_msg = str(e)
            app.logger.error(f"PDF导出失败: {error_msg}\n{traceback.format_exc()}")
            return jsonify({
                'error': 'PDF导出失败',
                'message': error_msg
            }), 500
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        return jsonify({
            'status': 'ok',
            'pdf_available': WEASYPRINT_AVAILABLE
        })

