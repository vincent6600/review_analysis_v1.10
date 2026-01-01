// Shopee竞品评价分析系统 - 前端JavaScript

// DOM元素
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const analyzeBtn = document.getElementById('analyzeBtn');
const exportBtn = document.getElementById('exportBtn');
const logContent = document.getElementById('logContent');
const clearLogBtn = document.getElementById('clearLogBtn');
const reportContainer = document.getElementById('reportContainer');

// 当前分析结果
let currentAnalysisResult = null;

// 初始化事件监听
initEventListeners();

function initEventListeners() {
    // 文件上传区域点击
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // 文件选择
    fileInput.addEventListener('change', handleFileSelect);
    
    // 拖拽上传
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
    
    // 执行分析按钮
    analyzeBtn.addEventListener('click', handleAnalyze);
    
    // 导出PDF按钮
    exportBtn.addEventListener('click', handleExportPDF);
    
    // 清空日志按钮
    clearLogBtn.addEventListener('click', () => {
        logContent.innerHTML = '<div class="log-item info">日志已清空</div>';
    });
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    // 验证文件类型
    if (!file.name.endsWith('.xlsx')) {
        addLog('文件格式不正确，请上传.xlsx格式文件', 'error');
        return;
    }
    
    // 验证文件大小（100MB）
    if (file.size > 100 * 1024 * 1024) {
        addLog('文件大小超过100MB限制，请上传较小的文件', 'error');
        return;
    }
    
    // 显示文件信息
    showFileInfo(file);
    
    addLog(`已选择文件: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`, 'success');
    analyzeBtn.disabled = false;
}

// 显示文件信息（v1.10新增：让用户更清楚地知道已上传文件）
function showFileInfo(file) {
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const uploadArea = document.getElementById('uploadArea');
    
    // 显示文件信息区域
    fileInfo.style.display = 'block';
    fileName.textContent = file.name;
    fileSize.textContent = `文件大小: ${(file.size / 1024 / 1024).toFixed(2)} MB`;
    
    // 只改变上传区域样式（不改变显示内容，保持原有的"点击或拖拽文件到此处上传"显示）
    uploadArea.classList.add('file-selected');
    // 不修改 uploadIcon、uploadText、uploadHint 的内容，保持原有显示
}

// 清除文件信息（当重新选择文件或清空时）
function clearFileInfo() {
    const fileInfo = document.getElementById('fileInfo');
    const uploadArea = document.getElementById('uploadArea');
    const uploadIcon = document.getElementById('uploadIcon');
    const uploadText = document.getElementById('uploadText');
    const uploadHint = document.getElementById('uploadHint');
    
    fileInfo.style.display = 'none';
    uploadArea.classList.remove('file-selected');
    uploadIcon.textContent = '📁';
    uploadText.textContent = '点击或拖拽文件到此处上传';
    uploadText.style.color = '#666';
    uploadText.style.fontWeight = 'normal';
    uploadHint.textContent = '支持 .xlsx 格式，最大 100MB';
}

async function handleAnalyze() {
    const file = fileInput.files[0];
    if (!file) {
        addLog('请先选择文件', 'error');
        return;
    }
    
    // 禁用按钮
    analyzeBtn.disabled = true;
    exportBtn.disabled = true;
    
    // 清空报告
    reportContainer.innerHTML = '<div class="empty-state"><div class="empty-icon">⏳</div><div class="empty-text">正在分析，请稍候...</div></div>';
    
    // 禁用文件选择（分析过程中）
    fileInput.disabled = true;
    
    addLog('开始上传文件...', 'info');
    
    try {
        // 创建FormData
        const formData = new FormData();
        formData.append('file', file);
        
        // 发送请求
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        // 检查响应状态
        if (!response.ok) {
            let errorMessage = '分析失败';
            try {
                const errorResult = await response.json();
                errorMessage = errorResult.message || errorResult.error || errorMessage;
                // 如果有详细错误信息，也显示
                if (errorResult.detail) {
                    console.error('详细错误信息:', errorResult.detail);
                }
            } catch (e) {
                errorMessage = `服务器错误 (${response.status}): ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }
        
        const result = await response.json();
        
        addLog('文件上传成功', 'success');
        addLog('正在分析数据...', 'info');
        
        // 保存分析结果
        currentAnalysisResult = result;
        
        addLog('分析完成！', 'success');
        addLog(`总评论数: ${result.analysis.rating.total_reviews}`, 'info');
        addLog(`平均星级: ${result.analysis.rating.average_rating}`, 'info');
        
        // 显示报告
        displayReport(result.html_report);
        
        // 启用导出按钮
        exportBtn.disabled = false;
        
    } catch (error) {
        addLog(`分析失败: ${error.message}`, 'error');
        reportContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">❌</div>
                <div class="empty-text">分析失败: ${error.message}</div>
            </div>
        `;
    } finally {
        analyzeBtn.disabled = false;
        fileInput.disabled = false;
    }
}

function displayReport(htmlContent) {
    // 创建报告容器
    const reportDiv = document.createElement('div');
    reportDiv.className = 'report-content';
    reportDiv.innerHTML = htmlContent;
    
    reportContainer.innerHTML = '';
    reportContainer.appendChild(reportDiv);
    
    // v1.10新增：渲染ECharts交互式图表（简约商务风格）
    renderEChartsCharts();
}

// v1.10新增：渲染ECharts交互式图表（简约商务风格）
function renderEChartsCharts() {
    // 等待ECharts.js加载完成
    if (typeof echarts === 'undefined') {
        // 如果ECharts.js未加载，等待一段时间后重试
        setTimeout(function() {
            if (typeof echarts !== 'undefined') {
                renderEChartsCharts();
            } else {
                console.warn('ECharts.js未加载，图表将无法显示');
            }
        }, 100);
        return;
    }
    
    // 查找所有ECharts图表容器
    const chartContainers = document.querySelectorAll('.echarts-chart-container');
    
    if (chartContainers.length === 0) {
        return; // 没有ECharts图表，直接返回
    }
    
    chartContainers.forEach(function(container) {
        const chartDataStr = container.getAttribute('data-echarts-chart');
        if (chartDataStr) {
            try {
                // 解析HTML实体编码（如果存在）
                // 关键修复：需要解码所有HTML实体，包括<、>、:等
                let decodedStr = chartDataStr;
                // 如果包含HTML实体，进行解码
                if (chartDataStr.includes('&quot;') || chartDataStr.includes('&#39;') || 
                    chartDataStr.includes('&lt;') || chartDataStr.includes('&gt;') || 
                    chartDataStr.includes('&amp;')) {
                    // 使用DOM元素解码HTML实体（最可靠的方法）
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = chartDataStr;
                    decodedStr = tempDiv.textContent || tempDiv.innerText || chartDataStr;
                    
                    // 如果DOM解码失败，使用手动替换（备用方案）
                    if (decodedStr === chartDataStr) {
                        decodedStr = chartDataStr
                            .replace(/&quot;/g, '"')
                            .replace(/&#39;/g, "'")
                            .replace(/&amp;/g, '&')
                            .replace(/&lt;/g, '<')
                            .replace(/&gt;/g, '>');
                    }
                }
                const chartOption = JSON.parse(decodedStr);
                
                // 处理tooltip formatter：如果是字符串形式的函数，需要转换为函数对象
                // 这对于散点图和雷达图特别重要，因为formatter在JSON序列化时变成了字符串
                if (chartOption.tooltip && typeof chartOption.tooltip.formatter === 'string') {
                    try {
                        // 检查是否是雷达图（通过检查series类型）
                        var isRadarChart = chartOption.series && chartOption.series.some(function(s) { return s.type === 'radar'; });
                        
                        // 将字符串形式的函数转换为真正的函数
                        // 注意：formatter字符串可能包含HTML转义字符和JSON转义字符，需要先解码
                        var formatterStr = chartOption.tooltip.formatter;
                        
                        // 关键修复：先解码所有HTML实体
                        // 使用DOM元素解码（最可靠的方法）
                        var tempDiv2 = document.createElement('div');
                        tempDiv2.innerHTML = formatterStr;
                        var decodedFormatterStr = tempDiv2.textContent || tempDiv2.innerText || formatterStr;
                        
                        // 如果DOM解码失败，使用手动替换（备用方案）
                        if (decodedFormatterStr === formatterStr) {
                            decodedFormatterStr = formatterStr
                                .replace(/&quot;/g, '"')
                                .replace(/&#39;/g, "'")
                                .replace(/&amp;/g, '&')
                                .replace(/&lt;/g, '<')
                                .replace(/&gt;/g, '>');
                        }
                        
                        // 关键修复：formatter字符串在JSON中已经被正确解析
                        // JSON.parse已经将\n、\t等转义字符转换为实际字符
                        // 所以decodedFormatterStr应该已经是正确的格式，不需要再次解析
                        // 但是，如果字符串中仍然包含字面的\n（两个字符），需要转换
                        if (decodedFormatterStr.includes('\\n') && !decodedFormatterStr.includes('\n')) {
                            // 如果包含字面的\n但没有实际的换行符，说明需要转换
                            decodedFormatterStr = decodedFormatterStr
                                .replace(/\\n/g, '\n')
                                .replace(/\\t/g, '\t')
                                .replace(/\\r/g, '\r')
                                .replace(/\\"/g, '"')
                                .replace(/\\'/g, "'")
                                .replace(/\\\\/g, '\\');
                        }
                        
                        // 尝试使用eval解析formatter函数
                        // 关键：formatter字符串应该是一个完整的JavaScript函数
                        var originalFormatter = null;
                        var trimmedStr = decodedFormatterStr.trim();
                        
                        try {
                            // 方法1：直接使用eval（最可靠的方法）
                            // 确保字符串是完整的函数
                            if (trimmedStr.startsWith('function')) {
                                // 使用eval解析函数（需要用括号包裹）
                                originalFormatter = eval('(' + decodedFormatterStr + ')');
                            } else {
                                // 如果不是以function开头，尝试用Function构造函数
                                // 但首先检查是否是有效的JavaScript代码
                                if (trimmedStr.length > 0 && (trimmedStr.startsWith('(') || trimmedStr.startsWith('{'))) {
                                    // 可能是被包裹的函数，尝试直接eval
                                    originalFormatter = eval(decodedFormatterStr);
                                } else {
                                    // 使用Function构造函数
                                    originalFormatter = new Function('return ' + decodedFormatterStr)();
                                }
                            }
                        } catch (e1) {
                            // 如果方法1失败，尝试修复可能的格式问题
                            try {
                                // 方法2：尝试修复转义字符
                                var cleanedStr = decodedFormatterStr;
                                
                                // 如果包含字面的转义序列，转换为实际字符
                                if (cleanedStr.includes('\\n') && !cleanedStr.includes('\n')) {
                                    cleanedStr = cleanedStr
                                        .replace(/\\n/g, '\n')
                                        .replace(/\\t/g, '\t')
                                        .replace(/\\r/g, '\r')
                                        .replace(/\\"/g, '"')
                                        .replace(/\\'/g, "'")
                                        .replace(/\\\\/g, '\\');
                                }
                                
                                // 再次尝试eval
                                if (cleanedStr.trim().startsWith('function')) {
                                    originalFormatter = eval('(' + cleanedStr + ')');
                                } else {
                                    originalFormatter = new Function('return ' + cleanedStr)();
                                }
                            } catch (e2) {
                                // 如果所有方法都失败，记录详细信息用于调试
                                console.error('Formatter解析失败');
                                console.error('原始字符串长度:', formatterStr.length);
                                console.error('解码后字符串长度:', decodedFormatterStr.length);
                                console.error('字符串前200个字符:', decodedFormatterStr.substring(0, 200));
                                console.error('字符串后200个字符:', decodedFormatterStr.substring(Math.max(0, decodedFormatterStr.length - 200)));
                                console.error('错误1:', e1.message);
                                console.error('错误2:', e2.message);
                                throw new Error('无法解析formatter: ' + e1.message + ', ' + e2.message);
                            }
                        }
                        
                        // 如果是雷达图，包装formatter以确保只处理第一个数据点
                        if (isRadarChart) {
                            chartOption.tooltip.formatter = function(params) {
                                // 关键修复：如果params是数组，只处理第一个元素
                                var param = Array.isArray(params) ? params[0] : params;
                                // 调用原始formatter，但只传递单个参数
                                try {
                                    return originalFormatter.call(this, param);
                                } catch (e) {
                                    console.warn('雷达图formatter执行错误:', e);
                                    return '';
                                }
                            };
                        } else {
                            chartOption.tooltip.formatter = originalFormatter;
                        }
                    } catch (e) {
                        console.warn('无法解析tooltip formatter，使用默认formatter:', e);
                        // 如果解析失败，使用默认formatter（针对散点图和雷达图）
                        chartOption.tooltip.formatter = function(params) {
                            // 散点图的默认formatter
                            if (params.seriesType === 'scatter' && params.data && Array.isArray(params.data) && params.data.length >= 2) {
                                var x = params.data[0] || 'N/A';
                                var y = params.data[1] || 'N/A';
                                return '变体：' + params.seriesName + '<br/>价格：' + x + '<br/>评论数：' + y;
                            }
                            // 雷达图的默认formatter
                            if (params.seriesType === 'radar') {
                                var param = Array.isArray(params) ? params[0] : params;
                                if (param && param.name) {
                                    return param.name + ': ' + (param.value || 'N/A');
                                }
                            }
                            return '';
                        };
                    }
                }
                
                // 初始化ECharts实例
                const chart = echarts.init(container, null, {
                    renderer: 'canvas',
                    width: 'auto',
                    height: 'auto'
                });
                
                // 设置图表配置（简约商务风格已在后端配置）
                chart.setOption(chartOption);
                
                // 特殊处理：雷达图的tooltip只显示单个数据点
                // 彻底修复：ECharts雷达图在有多个系列时，tooltip默认会显示所有系列的数据
                // 解决方案：完全重写formatter，确保只处理第一个参数，并使用事件系统作为额外保护
                if (chartOption.series && chartOption.series.some(function(s) { return s.type === 'radar'; })) {
                    // 保存原始formatter（如果存在）
                    var originalFormatter = chartOption.tooltip && typeof chartOption.tooltip.formatter === 'function' 
                        ? chartOption.tooltip.formatter 
                        : null;
                    
                    // 完全重写tooltip的formatter，确保只显示第一个数据点
                    if (chartOption.tooltip) {
                        chartOption.tooltip.trigger = 'item';
                        
                        // 关键修复：完全重写formatter，确保即使ECharts传递数组，也只处理第一个元素
                        chartOption.tooltip.formatter = function(params) {
                            // 关键修复：如果params是数组，只处理第一个元素
                            // 这是最关键的修复：即使ECharts传递了所有系列的数据，我们也只显示第一个
                            var param = null;
                            if (Array.isArray(params)) {
                                // 如果是数组，只取第一个元素（当前悬停的点）
                                param = params.length > 0 ? params[0] : null;
                            } else {
                                param = params;
                            }
                            
                            // 如果没有有效参数，返回空字符串
                            if (!param || param.seriesType !== 'radar') {
                                return '';
                            }
                            
                            // 如果有原始formatter，调用它（只传递单个参数）
                            if (originalFormatter) {
                                try {
                                    return originalFormatter.call(this, param);
                                } catch (e) {
                                    console.warn('雷达图formatter执行错误:', e);
                                    return '';
                                }
                            }
                            
                            // 如果没有原始formatter，使用默认格式
                            if (param && param.name) {
                                return param.name + ': ' + (param.value || 'N/A');
                            }
                            
                            return '';
                        };
                        
                        // 重新设置option以确保formatter生效
                        chart.setOption(chartOption, { notMerge: false });
                    }
                    
                    // 额外保护：使用事件系统拦截tooltip显示
                    // 如果ECharts仍然显示了多个系列的数据，强制隐藏并重新显示只包含第一个数据点的tooltip
                    var tooltipShown = false;
                    chart.on('showTip', function(params) {
                        // 如果params是数组且包含多个元素，说明显示了多个系列的数据
                        if (Array.isArray(params) && params.length > 1 && !tooltipShown) {
                            tooltipShown = true;
                            
                            // 隐藏当前tooltip
                            chart.dispatchAction({
                                type: 'hideTip'
                            });
                            
                            // 获取第一个数据点
                            var firstParam = params[0];
                            if (firstParam && firstParam.seriesType === 'radar') {
                                // 重新触发tooltip，但只传递第一个数据点
                                setTimeout(function() {
                                    chart.dispatchAction({
                                        type: 'showTip',
                                        seriesIndex: firstParam.seriesIndex,
                                        dataIndex: firstParam.dataIndex,
                                        name: firstParam.name
                                    });
                                    tooltipShown = false;
                                }, 50);
                            } else {
                                tooltipShown = false;
                            }
                        } else {
                            tooltipShown = false;
                        }
                    });
                    
                    // 监听tooltip隐藏事件，重置标志
                    chart.on('hideTip', function() {
                        tooltipShown = false;
                    });
                }
                
                // 响应式调整
                window.addEventListener('resize', function() {
                    chart.resize();
                });
                
            } catch (error) {
                console.error('ECharts图表渲染失败:', error, container);
                container.innerHTML = '<div style="color: #999; padding: 20px; text-align: center;">图表加载失败</div>';
            }
        }
    });
}

async function handleExportPDF() {
    if (!currentAnalysisResult || !currentAnalysisResult.html_report) {
        addLog('没有可导出的报告', 'error');
        return;
    }
    
    // 尝试PDF导出，如果失败则使用HTML保存
    addLog('正在生成PDF...', 'info');
    
    try {
        const response = await fetch('/api/export/pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                html_content: currentAnalysisResult.html_report
            })
        });
        
        if (!response.ok) {
            throw new Error('PDF功能不可用');
        }
        
        // 下载PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        // 生成文件名
        const fileInfo = currentAnalysisResult.file_info;
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        a.download = `${fileInfo.site}_产品ID_${fileInfo.product_id}_分析报告_${timestamp}.pdf`;
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        addLog('PDF导出成功', 'success');
        
    } catch (error) {
        // PDF导出失败，使用HTML保存方式
        addLog('PDF功能不可用，使用HTML保存方式', 'info');
        saveReportAsHTML();
    }
}

function saveReportAsHTML() {
    if (!currentAnalysisResult || !currentAnalysisResult.html_report) {
        addLog('没有可导出的报告', 'error');
        return;
    }
    
    try {
        // 创建完整的HTML文档
        const fullHTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shopee竞品评价分析报告</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', 'SimHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .report-wrapper {
            max-width: 1200px;
            margin: 0 auto;
            background-color: #fff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    ${currentAnalysisResult.html_report}
</body>
</html>`;
        
        // 创建下载链接
        const blob = new Blob([fullHTML], { type: 'text/html;charset=utf-8' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        // 生成文件名
        const fileInfo = currentAnalysisResult.file_info;
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        a.download = `${fileInfo.site}_产品ID_${fileInfo.product_id}_分析报告_${timestamp}.html`;
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        addLog('HTML报告保存成功', 'success');
        addLog('提示：可以在浏览器中打开HTML文件查看，或打印为PDF', 'info');
        
    } catch (error) {
        addLog(`保存失败: ${error.message}`, 'error');
    }
}

function addLog(message, type = 'info') {
    const logItem = document.createElement('div');
    logItem.className = `log-item ${type}`;
    
    const timestamp = new Date().toLocaleTimeString();
    logItem.textContent = `[${timestamp}] ${message}`;
    
    logContent.appendChild(logItem);
    logContent.scrollTop = logContent.scrollHeight;
}