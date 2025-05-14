from typing import Optional, Dict, Any, List
import asyncio
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page
import re
from bs4 import BeautifulSoup
import html2text
import logging

class BrowserConfig:
    def __init__(
        self,
        headless: bool = True,
        verbose: bool = False,
        user_agent: Optional[str] = None,
        cookies: Optional[List[Dict[str, Any]]] = None,
        proxy: Optional[str] = None,
        extra_args: Optional[List[str]] = None
    ):
        self.headless = headless
        self.verbose = verbose
        self.user_agent = user_agent
        self.cookies = cookies
        self.proxy = proxy
        self.extra_args = extra_args or []

class AsyncWebCrawler:
    def __init__(self, config: BrowserConfig = None):
        self.config = config or BrowserConfig()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.html2text_converter = html2text.HTML2Text()
        self.html2text_converter.ignore_links = False
        self.html2text_converter.ignore_images = False
        self.html2text_converter.ignore_emphasis = False
        self.html2text_converter.body_width = 0
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        await self.init_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def init_browser(self):
        """初始化浏览器"""
        launch_args = {
            'headless': self.config.headless,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--allow-running-insecure-content',
                '--lang=zh-CN,zh'
            ] + self.config.extra_args
        }

        if self.config.proxy:
            launch_args['args'].append(f'--proxy-server={self.config.proxy}')

        self.browser = await launch(**launch_args)
        self.page = await self.browser.newPage()

        # 设置页面编码
        await self.page.setExtraHTTPHeaders({
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        })
        
        # 设置默认超时时间
        await self.page.setDefaultNavigationTimeout(30000)
        
        if self.config.user_agent:
            await self.page.setUserAgent(self.config.user_agent)

        if self.config.cookies:
            await self.page.setCookie(*self.config.cookies)

    async def close(self):
        """关闭浏览器"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()

    async def get_page_content(self) -> Optional[str]:
        """获取页面内容的多种尝试"""
        try:
            # 方法1：直接获取innerHTML
            content = await self.page.evaluate('''() => {
                return document.documentElement.innerHTML;
            }''')
            if content:
                return content
        except Exception as e:
            self.logger.warning(f"方法1获取内容失败: {str(e)}")

        try:
            # 方法2：使用outerHTML
            content = await self.page.evaluate('''() => {
                return document.documentElement.outerHTML;
            }''')
            if content:
                return content
        except Exception as e:
            self.logger.warning(f"方法2获取内容失败: {str(e)}")

        try:
            # 方法3：使用content()方法
            return await self.page.content()
        except Exception as e:
            self.logger.warning(f"方法3获取内容失败: {str(e)}")
            return None

    def clean_html(self, html_content: str) -> str:
        """清理HTML内容"""
        try:
            # 使用BeautifulSoup清理HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style", "iframe", "noscript"]):
                script.decompose()
            
            # 移除注释
            for comment in soup.find_all(text=lambda text: isinstance(text, str) and '<!--' in text):
                comment.extract()
            
            # 移除空白标签
            for tag in soup.find_all():
                if len(tag.get_text(strip=True)) == 0:
                    tag.decompose()
            
            return str(soup)
        except Exception as e:
            self.logger.error(f"清理HTML失败: {str(e)}")
            return html_content

    def html_to_markdown(self, html_content: str, title: str = "") -> str:
        """将HTML转换为Markdown格式"""
        try:
            # 清理HTML
            cleaned_html = self.clean_html(html_content)
            
            # 转换为Markdown
            markdown = self.html2text_converter.handle(cleaned_html)
            
            # 添加标题
            if title:
                markdown = f"# {title}\n\n{markdown}"
            
            # 清理Markdown
            markdown = re.sub(r'\n{3,}', '\n\n', markdown)  # 移除多余的空行
            markdown = re.sub(r'!\[.*?\]\(data:image.*?\)', '', markdown)  # 移除base64图片
            
            return markdown.strip()
        except Exception as e:
            self.logger.error(f"转换Markdown失败: {str(e)}")
            return f"# {title}\n\n{html_content}"

    async def arun(self, url: str, headers: Optional[Dict[str, str]] = None, wait_time: float = 5.0) -> Dict[str, Any]:
        """运行爬虫并返回结果"""
        try:
            if headers:
                await self.page.setExtraHTTPHeaders(headers)

            # 设置请求拦截
            await self.page.setRequestInterception(True)
            
            async def intercept_request(request):
                if request.resourceType in ['image', 'media', 'font']:
                    await request.abort()
                else:
                    await request.continue_()
            
            self.page.on('request', lambda req: asyncio.ensure_future(intercept_request(req)))

            # 导航到页面
            response = await self.page.goto(url, waitUntil=['domcontentloaded', 'networkidle0'])
            
            if not response:
                return {'error': '页面加载失败'}
            
            if response.status != 200:
                return {'error': f'HTTP状态码错误: {response.status}'}

            # 等待页面加载完成
            await asyncio.sleep(wait_time)

            # 获取页面标题
            title = await self.page.title()
            
            # 获取页面内容
            content = await self.get_page_content()
            if not content:
                return {'error': '无法获取页面内容'}
            
            # 转换为Markdown格式
            try:
                markdown_content = self.html_to_markdown(content, title)
                if not markdown_content:
                    return {'error': '内容转换失败'}
                    
                return {
                    'success': True,
                    'markdown_content': markdown_content,
                    'url': url,
                    'title': title
                }
            except Exception as convert_error:
                self.logger.error(f"内容转换失败: {str(convert_error)}")
                return {'error': f'内容转换失败: {str(convert_error)}'}

        except Exception as e:
            self.logger.error(f"爬取过程发生错误: {str(e)}")
            return {'error': str(e)} 