import asyncio
import sys
from crawler import WebCrawler, create_browser
from logger import add_log_message
import os
from datetime import datetime

# 替代login.py中的函数，避免导入有问题的模块
async def get_chrome_path():
    """获取Chrome可执行文件路径的简化版本"""
    import platform
    import os
    from pathlib import Path
    
    system = platform.system()
    
    # 常见的Chrome路径
    if system == 'Windows':
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Google\Chrome\Application\chrome.exe"),
        ]
    elif system == 'Darwin':  # macOS
        paths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        ]
    else:  # Linux
        paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
        ]
    
    # 检查路径是否存在
    for path in paths:
        if os.path.exists(path) and os.path.isfile(path):
            print(f"找到Chrome路径: {path}")
            return path
    
    print("未找到Chrome浏览器")
    return None

async def test_crawler(url):
    """测试爬虫功能"""
    try:
        print(f"开始测试爬取: {url}")
        
        # 实例化爬虫
        crawler = WebCrawler()
        
        # 确保浏览器实例可用
        browser_ok = await crawler._ensure_browser()
        if not browser_ok:
            print("浏览器初始化失败")
            return False
            
        # 执行爬取
        result = await crawler.crawl(
            url=url,
            need_login=False,
            recursive=False,
            include_images=False,
            max_depth=1,
            timeout=120,
            retry_count=3
        )
        
        # 检查结果
        if result and result.get('success'):
            content = result.get('content', {})
            
            # 显示统计信息
            html_len = len(content.get('html_content', ''))
            md_len = len(content.get('markdown_content', ''))
            text_len = len(content.get('text_content', ''))
            
            print("爬取成功!")
            print(f"HTML内容长度: {html_len}")
            print(f"Markdown内容长度: {md_len}")
            print(f"文本内容长度: {text_len}")
            
            # 创建downloads目录（如果不存在）
            os.makedirs('downloads', exist_ok=True)
            
            # 保存结果到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"downloads/test_crawler_{timestamp}.md"
            
            # 从content中提取markdown内容
            markdown_content = content.get('markdown_content', '')
            if markdown_content:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    print(f"爬取结果已保存到: {filename}")
                except Exception as e:
                    print(f"保存文件时出错: {str(e)}")
            
            return True
        else:
            error = result.get('error', '未知错误') if result else '爬取结果为空'
            print(f"爬取失败: {error}")
            return False
    except Exception as e:
        print(f"测试爬虫时出错: {str(e)}")
        return False
    finally:
        # 确保资源被释放
        if 'crawler' in locals() and crawler:
            await crawler.cleanup()

# 重写crawler.py中的get_executable_path函数
import sys
import importlib.util
spec = importlib.util.find_spec('crawler')
module = importlib.util.module_from_spec(spec)
sys.modules['crawler'] = module
spec.loader.exec_module(module)

# 替换get_executable_path函数
async def patched_get_executable_path():
    return await get_chrome_path()

# 应用补丁
module.get_executable_path = patched_get_executable_path

if __name__ == "__main__":
    # 获取URL参数
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.example.com"
    
    print("使用简化版爬虫测试脚本，避开login.py中的缩进错误")
    print(f"测试URL: {url}")
    
    # 运行测试
    asyncio.run(test_crawler(url)) 