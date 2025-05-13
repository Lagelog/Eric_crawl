import os
import asyncio
from flask import render_template, request, jsonify, send_file, Response, stream_with_context
from queue import Queue
import time

from config import DOWNLOAD_DIR
from logger import add_log_message, clear_logs, add_subscriber, remove_subscriber, get_all_logs
from utils import markdown_to_html, handle_asyncio_exception, generate_filename
from crawler import WebCrawler

def register_routes(app):
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
            clear_logs()
            
            # 创建事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 设置全局异常处理
            loop.set_exception_handler(handle_asyncio_exception)
            
            # 创建爬虫实例
            crawler = WebCrawler()
            
            # 运行爬虫
            result = loop.run_until_complete(crawler.crawl(url, need_login))
            
            # 关闭循环
            loop.close()
            
            if result['success']:
                # 生成文件名
                filename = generate_filename(url)
                filepath = os.path.join(DOWNLOAD_DIR, filename)
                
                # 保存文件
                with open(filepath, "w", encoding="utf-8") as file:
                    file.write(result['html'])
                
                add_log_message(f"保存到文件: {filename}")
                
                # 转换为HTML
                html_content = markdown_to_html(result['html'])
                
                # 处理iframe内容
                if 'iframe_contents' in result:
                    iframe_html = "<div class='iframe-content'><h2>页面中的Iframe内容</h2>"
                    for iframe in result['iframe_contents']:
                        title = iframe.get('title', f"Iframe {iframe.get('id', '')}")
                        iframe_html += f"<div class='iframe-item'>"
                        iframe_html += f"<h3>{title}</h3>"
                        iframe_html += f"<p>源URL: <a href='{iframe.get('url', '')}' target='_blank'>{iframe.get('url', '')}</a></p>"
                        
                        # 提取iframe内容中的关键部分
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(iframe.get('content', ''), 'html.parser')
                        
                        # 查找主要内容区域
                        content_area = None
                        for selector in ['.article', '.content', '#article', '.main-content', 'article']:
                            content_area = soup.select_one(selector)
                            if content_area:
                                break
                        
                        if content_area:
                            iframe_html += f"<div class='iframe-content-area'>{content_area}</div>"
                        else:
                            # 如果找不到主要内容区域，提取所有可见文本
                            paragraphs = soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                            visible_text = ""
                            for p in paragraphs:
                                if p.get_text().strip():
                                    visible_text += f"<p>{p.get_text().strip()}</p>"
                            
                            iframe_html += f"<div class='iframe-extracted-content'>{visible_text}</div>"
                        
                        iframe_html += "</div>"
                    iframe_html += "</div>"
                    
                    # 添加到结果
                    html_content += iframe_html
                
                return jsonify({
                    "success": True,
                    "html": html_content,
                    "filename": filename
                })
            
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
            queue = Queue()
            add_subscriber(queue)
            
            try:
                # 发送现有日志
                for message in get_all_logs():
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
                remove_subscriber(queue)
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream') 