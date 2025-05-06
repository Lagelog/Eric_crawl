import os
import asyncio
import platform
import tempfile
from flask import Flask, render_template, request, jsonify, send_file, Response, stream_with_context
from threading import Thread
from pathlib import Path
import time
import random

# 导入爬虫功能
from login import AsyncWebCrawler, BrowserConfig, get_random_user_agent, get_random_headers, manual_login

app = Flask(__name__)

# 创建templates和static目录如果不存在
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# 创建HTML模板
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eric爬虫助手</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap">
    <style>
        body {
            font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            background-color: #f8f9fa;
            color: #202124;
        }
        .header {
            background-color: #fff;
            box-shadow: 0 1px 2px 0 rgba(60, 64, 67, 0.3);
            padding: 16px 24px;
            display: flex;
            align-items: center;
        }
        .logo {
            font-size: 22px;
            font-weight: 500;
            color: #4285f4;
        }
        .container {
            flex: 1;
            padding: 32px;
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
            box-sizing: border-box;
        }
        .search-card {
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 1px 2px 0 rgba(60, 64, 67, 0.3);
            padding: 24px;
            margin-bottom: 24px;
        }
        .search-form {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .input-wrapper {
            position: relative;
        }
        .url-input {
            width: 100%;
            padding: 12px 16px;
            font-size: 16px;
            border: 1px solid #dadce0;
            border-radius: 24px;
            box-sizing: border-box;
            outline: none;
            transition: border-color 0.2s;
        }
        .url-input:focus {
            border-color: #4285f4;
            box-shadow: 0 0 0 1px #4285f4;
        }
        .search-btn {
            align-self: center;
            background-color: #4285f4;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .search-btn:hover {
            background-color: #3b78e7;
        }
        .search-btn:disabled {
            background-color: #dadce0;
            cursor: not-allowed;
        }
        .options-container {
            margin-top: 16px;
        }
        .checkbox-label {
            display: flex;
            align-items: center;
            font-size: 14px;
            color: #5f6368;
            cursor: pointer;
        }
        .checkbox-label input {
            margin-right: 8px;
        }
        .login-notice {
            margin-top: 8px;
            padding: 12px;
            background-color: #e8f0fe;
            border-radius: 4px;
            font-size: 14px;
            color: #1a73e8;
            display: none;
        }
        .result-card {
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 1px 2px 0 rgba(60, 64, 67, 0.3);
            padding: 24px;
            max-height: 60vh;
            overflow-y: auto;
            display: none;
        }
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #dadce0;
        }
        .result-title {
            font-size: 18px;
            font-weight: 500;
            color: #202124;
            margin: 0;
        }
        .download-btn {
            background-color: #0f9d58;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.2s;
            text-decoration: none;
            display: inline-block;
        }
        .download-btn:hover {
            background-color: #0b8043;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #4285f4;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 16px;
        }
        .log-messages {
            margin-top: 16px;
            padding: 12px;
            background-color: #f8f9fa;
            border-radius: 4px;
            font-family: monospace;
            font-size: 14px;
            max-height: 150px;
            overflow-y: auto;
            color: #5f6368;
        }
        .log-message {
            margin: 4px 0;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        /* Markdown 样式 */
        .markdown-content {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            font-size: 16px;
            line-height: 1.5;
            word-wrap: break-word;
        }
        .markdown-content h1, .markdown-content h2, .markdown-content h3, 
        .markdown-content h4, .markdown-content h5, .markdown-content h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }
        .markdown-content h1 { font-size: 2em; padding-bottom: .3em; border-bottom: 1px solid #eaecef; }
        .markdown-content h2 { font-size: 1.5em; padding-bottom: .3em; border-bottom: 1px solid #eaecef; }
        .markdown-content p { margin-top: 0; margin-bottom: 16px; }
        .markdown-content code { padding: .2em .4em; background-color: rgba(27,31,35,.05); border-radius: 3px; }
        .markdown-content pre { padding: 16px; overflow: auto; background-color: #f6f8fa; border-radius: 3px; }
        .markdown-content blockquote { padding: 0 1em; color: #6a737d; border-left: .25em solid #dfe2e5; }
        .markdown-content img { max-width: 100%; box-sizing: content-box; }
        .markdown-content a { color: #0366d6; text-decoration: none; }
        .markdown-content a:hover { text-decoration: underline; }
        .markdown-content table { border-spacing: 0; border-collapse: collapse; }
        .markdown-content table th, .markdown-content table td { padding: 6px 13px; border: 1px solid #dfe2e5; }
        .markdown-content table tr { background-color: #fff; border-top: 1px solid #c6cbd1; }
        .markdown-content table tr:nth-child(2n) { background-color: #f6f8fa; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">欢迎使用Eric爬虫助手</div>
    </div>
    <div class="container">
        <div class="search-card">
            <form class="search-form" id="crawlForm">
                <div class="input-wrapper">
                    <input type="url" id="urlInput" class="url-input" placeholder="请输入要爬取的网址 (例如: https://www.example.com)" required>
                </div>
                <div class="options-container">
                    <label class="checkbox-label">
                        <input type="checkbox" id="needLoginCheck"> 需要登录(淘宝、京东等)
                    </label>
                    <div class="login-notice" id="loginNotice">
                        勾选此选项后，将会打开浏览器供您手动登录。完成登录后，请回到控制台按回车键继续爬取过程。
                    </div>
                </div>
                <button type="submit" class="search-btn" id="searchBtn">开始爬取</button>
            </form>
        </div>
        
        <div class="loading" id="loadingSection">
            <div class="loading-spinner"></div>
            <div>正在爬取数据，请稍候...</div>
            <div class="log-messages" id="logMessages"></div>
        </div>
        
        <div class="result-card" id="resultCard">
            <div class="result-header">
                <h2 class="result-title">爬取结果</h2>
                <a href="#" class="download-btn" id="downloadBtn">下载 Markdown</a>
            </div>
            <div class="markdown-content" id="resultContent"></div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('crawlForm');
            const urlInput = document.getElementById('urlInput');
            const needLoginCheck = document.getElementById('needLoginCheck');
            const loginNotice = document.getElementById('loginNotice');
            const searchBtn = document.getElementById('searchBtn');
            const loadingSection = document.getElementById('loadingSection');
            const resultCard = document.getElementById('resultCard');
            const resultContent = document.getElementById('resultContent');
            const downloadBtn = document.getElementById('downloadBtn');
            const logMessages = document.getElementById('logMessages');
            
            let logEventSource = null;
            
            // 显示/隐藏登录提示
            needLoginCheck.addEventListener('change', function() {
                loginNotice.style.display = this.checked ? 'block' : 'none';
            });
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const url = urlInput.value.trim();
                const needLogin = needLoginCheck.checked;
                
                if (!url) return;
                
                // 重置界面
                resultCard.style.display = 'none';
                resultContent.innerHTML = '';
                logMessages.innerHTML = '';
                
                // 显示加载状态
                searchBtn.disabled = true;
                loadingSection.style.display = 'block';
                
                // 连接日志流
                if (logEventSource) {
                    logEventSource.close();
                }
                
                logEventSource = new EventSource('/log-stream');
                logEventSource.onmessage = function(event) {
                    const message = document.createElement('div');
                    message.className = 'log-message';
                    message.textContent = event.data;
                    logMessages.appendChild(message);
                    logMessages.scrollTop = logMessages.scrollHeight;
                };
                
                // 发送爬取请求
                fetch('/crawl', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        url: url,
                        need_login: needLogin
                    })
                })
                .then(response => response.json())
                .then(data => {
                    // 关闭日志流
                    if (logEventSource) {
                        logEventSource.close();
                        logEventSource = null;
                    }
                    
                    // 隐藏加载状态
                    searchBtn.disabled = false;
                    loadingSection.style.display = 'none';
                    
                    if (data.success) {
                        // 显示结果
                        resultContent.innerHTML = data.html;
                        resultCard.style.display = 'block';
                        
                        // 更新下载链接
                        downloadBtn.href = `/download/${data.filename}`;
                    } else {
                        alert('爬取失败: ' + data.error);
                    }
                })
                .catch(error => {
                    // 关闭日志流
                    if (logEventSource) {
                        logEventSource.close();
                        logEventSource = null;
                    }
                    
                    searchBtn.disabled = false;
                    loadingSection.style.display = 'none';
                    alert('请求出错: ' + error);
                });
            });
        });
    </script>
</body>
</html>
''')

# 创建CSS文件
with open('static/style.css', 'w', encoding='utf-8') as f:
    f.write('''/* 额外样式如果需要 */''')

# 全局变量存储日志消息
log_messages = []
log_subscribers = set()

# 目录设置
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 简单的日志队列实现
def add_log_message(message):
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    formatted_message = f"[{timestamp}] {message}"
    log_messages.append(formatted_message)
    # 通知所有订阅者
    for queue in log_subscribers:
        queue.put(formatted_message)

# 异步延迟函数
async def async_delay(seconds):
    add_log_message(f"延迟 {seconds} 秒...")
    await asyncio.sleep(seconds)

# 转换Markdown为HTML的函数
def markdown_to_html(markdown_text):
    # 这里可以使用更复杂的Markdown转HTML库
    # 简单实现：替换常见Markdown语法
    import re
    
    # 转义HTML特殊字符
    html = markdown_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # 标题
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    
    # 段落
    html = re.sub(r'^(?!<h[1-6]|<ul|<ol|<li|<blockquote|<pre)(.*?)$', r'<p>\1</p>', html, flags=re.MULTILINE)
    
    # 粗体和斜体
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # 链接
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
    
    # 列表
    html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\g<0></ul>', html, flags=re.DOTALL)
    
    # 代码块
    html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    
    # 行内代码
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    return html

# 网页爬取核心功能
async def crawl_website(url, need_login=False):
    try:
        add_log_message(f"准备爬取网址: {url}")
        
        session_data = None
        
        # 如果需要登录，启动手动登录流程
        if need_login:
            add_log_message("需要登录，即将打开浏览器供您手动登录...")
            session_data = await manual_login(url)
            
            if not session_data:
                add_log_message("登录失败或被用户取消")
                return {"success": False, "error": "登录失败或被用户取消"}
                
            add_log_message("登录成功，获取到cookies和浏览器指纹")
        
        # 浏览器配置
        user_agent = get_random_user_agent()
        add_log_message(f"使用User-Agent: {user_agent[:30]}...")
        
        # 设置浏览器配置
        browser_config_args = {
            'headless': True,
            'verbose': True,
            'user_agent': session_data.get('fingerprint', {}).get('user_agent', user_agent) if session_data else user_agent,
            'extra_args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                f'--window-size={random.randint(1024, 1920)},{random.randint(768, 1080)}'
            ]
        }
        
        # 如果有cookies，添加到配置
        if session_data and 'cookies' in session_data:
            browser_config_args['cookies'] = session_data['cookies']
            
        browser_config = BrowserConfig(**browser_config_args)
        
        add_log_message("初始化爬虫...")
        async with AsyncWebCrawler(config=browser_config) as crawler:
            # 添加延迟
            await async_delay(5.0)
            
            # 设置自定义请求头
            headers = session_data.get('fingerprint', {}).get('headers') if session_data else get_random_headers()
            
            add_log_message(f"开始爬取: {url}")
            result = await crawler.arun(
                url=url, 
                headers=headers,
                wait_time=random.uniform(3, 8)  # 随机等待时间，模拟人类阅读行为
            )
            
            if hasattr(result, 'success') and result.success:
                add_log_message("爬取成功!")
                
                # 检查markdown属性是否存在
                if hasattr(result, 'markdown') and result.markdown:
                    # 生成文件名
                    from urllib.parse import urlparse
                    parsed_url = urlparse(url)
                    domain = parsed_url.netloc.replace('.', '_')
                    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
                    filename = f"{domain}_{timestamp}.md"
                    filepath = os.path.join(DOWNLOAD_DIR, filename)
                    
                    # 保存文件
                    with open(filepath, "w", encoding="utf-8") as file:
                        file.write(result.markdown)
                    
                    add_log_message(f"保存到文件: {filename}")
                    
                    # 转换为HTML并返回结果
                    html_content = markdown_to_html(result.markdown)
                    return {
                        "success": True, 
                        "markdown": result.markdown,
                        "html": html_content,
                        "filename": filename
                    }
                else:
                    add_log_message("爬取结果中没有Markdown内容")
                    return {"success": False, "error": "爬取结果中没有Markdown内容"}
            else:
                # 安全获取错误信息
                error_msg = getattr(result, 'error', None) or "未知错误"
                if isinstance(error_msg, Exception):
                    error_msg = str(error_msg)
                add_log_message(f"爬取失败: {error_msg}")
                return {"success": False, "error": error_msg}
                
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        add_log_message(f"爬取过程中发生错误: {str(e)}")
        add_log_message(error_details)
        return {"success": False, "error": str(e)}

# Flask路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crawl', methods=['POST'])
def crawl():
    data = request.json
    url = data.get('url')
    need_login = data.get('need_login', False)
    
    if not url:
        return jsonify({"success": False, "error": "URL不能为空"})
    
    try:
        # 清空之前的日志
        log_messages.clear()
        
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 运行爬虫
        result = loop.run_until_complete(crawl_website(url, need_login))
        
        # 关闭循环
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        add_log_message(f"处理请求时出错: {str(e)}")
        add_log_message(error_details)
        return jsonify({"success": False, "error": str(e)})

@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return "文件不存在", 404

@app.route('/log-stream')
def log_stream():
    def generate():
        from queue import Queue
        import time
        
        # 创建队列，并添加到订阅列表
        queue = Queue()
        log_subscribers.add(queue)
        
        try:
            # 发送现有日志
            for message in log_messages:
                yield f"data: {message}\n\n"
            
            # 监听新的日志消息
            while True:
                try:
                    message = queue.get(timeout=1)
                    yield f"data: {message}\n\n"
                except:
                    # 发送保持连接的消息
                    yield f"data: {time.time()}\n\n"
        finally:
            # 移除订阅
            log_subscribers.remove(queue)
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True) 