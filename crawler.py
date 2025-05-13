import asyncio
import traceback
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
import random
from pyppeteer import launch

from config import (
    BROWSER_ARGS, DEFAULT_TIMEOUT, DEFAULT_WAIT_TIME,
    PAGE_LOAD_WAIT, IFRAME_LOAD_WAIT, SINA_HEADERS, SINA_USER_AGENT
)
from logger import add_log_message
from utils import async_delay
from login import AsyncWebCrawler, get_random_user_agent, get_random_headers, get_executable_path

class WebCrawler:
    def __init__(self):
        self.browser = None
        self.crawler = None
    
    async def setup_browser(self) -> bool:
        """
        设置并启动浏览器
        
        Returns:
            bool: 是否成功启动浏览器
        """
        try:
            browser_args = {
                'headless': True,
                'args': BROWSER_ARGS,
                'ignoreHTTPSErrors': True,
                'handleSIGINT': False,
                'handleSIGTERM': False,
                'handleSIGHUP': False,
                'dumpio': True,
            }
            
            # 寻找可用的浏览器路径
            executable_path = get_executable_path()
            if executable_path:
                add_log_message(f"找到浏览器路径: {executable_path}")
                browser_args['executablePath'] = executable_path
            else:
                add_log_message("警告: 未找到Chrome/Chromium浏览器路径，尝试使用pyppeteer内置下载")
            
            # 尝试不同模式启动浏览器
            try:
                self.browser = await launch(**browser_args)
                add_log_message("成功以无头模式创建浏览器实例")
                return True
            except Exception as headless_err:
                add_log_message(f"无头模式创建浏览器失败: {str(headless_err)}，尝试有头模式...")
                try:
                    browser_args['headless'] = False
                    self.browser = await launch(**browser_args)
                    add_log_message("成功以有头模式创建浏览器实例")
                    return True
                except Exception as headed_err:
                    add_log_message(f"有头模式创建浏览器也失败: {str(headed_err)}，尝试最小化配置...")
                    try:
                        minimal_args = {
                            'headless': False,
                            'args': ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                        }
                        if 'executablePath' in browser_args:
                            minimal_args['executablePath'] = browser_args['executablePath']
                        
                        self.browser = await launch(**minimal_args)
                        add_log_message("成功以最小配置创建浏览器实例")
                        return True
                    except Exception as minimal_err:
                        add_log_message(f"所有浏览器创建方法都失败: {str(minimal_err)}")
                        return False
        except Exception as e:
            add_log_message(f"设置浏览器时出错: {str(e)}")
            return False

    async def extract_iframe_content(self, page, iframe_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        提取iframe内容
        
        Args:
            page: 页面对象
            iframe_info: iframe信息
            
        Returns:
            提取的iframe内容
        """
        try:
            iframe_url = iframe_info.get('src', '')
            if not iframe_url or not iframe_url.startswith('http'):
                return None
                
            iframe_page = await self.browser.newPage()
            await iframe_page.setUserAgent(get_random_user_agent())
            await iframe_page.setExtraHTTPHeaders(get_random_headers())
            
            await iframe_page.goto(iframe_url, {
                'waitUntil': 'networkidle2',
                'timeout': DEFAULT_TIMEOUT
            })
            
            await async_delay(IFRAME_LOAD_WAIT)
            
            content = await iframe_page.content()
            title = await iframe_page.title()
            
            await iframe_page.close()
            
            return {
                'title': title or f"Iframe {iframe_info.get('id', '')}",
                'content': content,
                'url': iframe_url,
                'id': iframe_info.get('id', ''),
                'name': iframe_info.get('name', '')
            }
        except Exception as e:
            add_log_message(f"提取iframe内容时出错: {str(e)}")
            return None

    async def process_sina_page(self, page) -> List[Dict[str, Any]]:
        """
        Args:
            page: 页面对象
            
        Returns:
            处理结果列表
        """
        await page.setExtraHTTPHeaders(SINA_HEADERS)
        await page.setUserAgent(SINA_USER_AGENT)
        
        iframe_results = []
        
        # 获取所有iframe
        iframes = await page.evaluate('''() => {
            const iframes = document.querySelectorAll('iframe');
            return Array.from(iframes).map(iframe => {
                const rect = iframe.getBoundingClientRect();
                return {
                    src: iframe.src || '',
                    id: iframe.id || '',
                    name: iframe.name || '',
                    className: iframe.className || '',
                    width: iframe.width || rect.width,
                    height: iframe.height || rect.height,
                    visible: rect.width > 0 && rect.height > 0 && 
                            getComputedStyle(iframe).display !== 'none' && 
                            getComputedStyle(iframe).visibility !== 'hidden'
                };
            });
        }''')
        
        if iframes:
            add_log_message(f"发现 {len(iframes)} 个iframe元素")
            for iframe in iframes:
                if content := await self.extract_iframe_content(page, iframe):
                    iframe_results.append(content)
        
        return iframe_results

    async def crawl(self, url: str, need_login: bool = False) -> Dict[str, Any]:
        """
        爬取网页内容
        
        Args:
            url: 目标URL
            need_login: 是否需要登录
            
        Returns:
            爬取结果
        """
        try:
            if not await self.setup_browser():
                return {"success": False, "error": "浏览器启动失败"}
            
            # 创建新页面并访问URL
            page = await self.browser.newPage()
            await page.setUserAgent(get_random_user_agent())
            await page.goto(url, {'timeout': 0})
            
            await async_delay(PAGE_LOAD_WAIT)
            
            # 获取页面内容
            content = await page.content()
            title = await page.title()
            
            result = {
                'success': True,
                'html': content,
                'title': title
            }
            
            # 如果是新浪网站，进行特殊处理
            if "sina" in url or "新浪" in url:
                iframe_contents = await self.process_sina_page(page)
                if iframe_contents:
                    result['iframe_contents'] = iframe_contents
            
            return result
            
        except Exception as e:
            error_details = traceback.format_exc()
            add_log_message(f"爬取过程中发生错误: {str(e)}")
            add_log_message(error_details)
            return {"success": False, "error": str(e)}
        
        finally:
            # 清理资源
            await self.cleanup()
    
    async def cleanup(self):
        """清理浏览器资源"""
        try:
            if self.browser:
                add_log_message("等待所有操作完成，准备关闭浏览器...")
                await asyncio.sleep(2)
                
                try:
                    pages = await self.browser.pages()
                    add_log_message(f"浏览器仍然有 {len(pages)} 个活动页面")
                    
                    for page in pages:
                        try:
                            await page.close()
                        except Exception as page_close_err:
                            add_log_message(f"关闭页面时出错: {str(page_close_err)}")
                except Exception as pages_err:
                    add_log_message(f"获取页面列表时出错: {str(pages_err)}")
                
                try:
                    add_log_message("正在关闭浏览器...")
                    await self.browser.close()
                    add_log_message("浏览器已成功关闭")
                except Exception as browser_close_err:
                    add_log_message(f"关闭浏览器时出错: {str(browser_close_err)}")
                
                self.browser = None
        except Exception as cleanup_err:
            add_log_message(f"清理浏览器资源时出现错误: {str(cleanup_err)}")
        
        if self.crawler:
            add_log_message("清理爬虫资源...")
            self.crawler = None 