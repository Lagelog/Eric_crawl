import asyncio
import markdown
import re
from urllib.parse import urlparse
import time
from typing import Dict, Any

def markdown_to_html(markdown_text: str) -> str:
    """
    将Markdown文本转换为HTML
    
    Args:
        markdown_text: Markdown格式的文本
        
    Returns:
        转换后的HTML文本
    """
    # 使用markdown库处理Markdown文本
    html = markdown.markdown(markdown_text, extensions=['extra', 'tables', 'nl2br'])
    
    # 特殊处理iframe内容，确保iframe能够正确显示
    html = re.sub(r'&lt;iframe(.+?)&gt;(.+?)&lt;/iframe&gt;', 
                 r'<iframe\1>\2</iframe>', 
                 html, 
                 flags=re.DOTALL)
    
    return html

async def async_delay(seconds: float) -> None:
    """
    异步延迟函数
    
    Args:
        seconds: 延迟的秒数
    """
    from logger import add_log_message
    add_log_message(f"延迟 {seconds} 秒...")
    await asyncio.sleep(seconds)

def generate_filename(url: str) -> str:
    """
    根据URL生成文件名
    
    Args:
        url: 网页URL
        
    Returns:
        生成的文件名
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('.', '_')
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    return f"{domain}_{timestamp}.md"

def handle_asyncio_exception(loop: asyncio.AbstractEventLoop, context: Dict[str, Any]) -> None:
    """
    处理异步任务异常
    
    Args:
        loop: 事件循环
        context: 异常上下文
    """
    from logger import add_log_message
    exception = context.get('exception')
    if exception:
        add_log_message(f"异步任务异常: {str(exception)}")
        if "NetworkError" in str(exception) or "Protocol error" in str(exception):
            add_log_message("检测到网络错误，可能是浏览器已关闭或会话已终止") 