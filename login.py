import asyncio
import random
import time
import os
import sys
import platform
from pathlib import Path
from crawl4ai import AsyncWebCrawler, BrowserConfig
from pyppeteer import launch
from pyppeteer.errors import BrowserError

# 全局变量
use_proxy_globally = False

# 添加Chromium路径处理
def get_executable_path():
    """获取Chromium/Chrome可执行文件路径"""
    system = platform.system()
    
    # 用户本地已安装的浏览器优先级列表
    if system == 'Windows':
        # 扩展Windows上可能的Chrome安装路径
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            # 用户目录下可能的Chrome安装路径
            os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Google\Chrome\Application\chrome.exe"),
            os.path.join(os.environ.get('PROGRAMFILES', ''), r"Google\Chrome\Application\chrome.exe"),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), r"Google\Chrome\Application\chrome.exe"),
            # 其他常见浏览器
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Tencent\QQBrowser\QQBrowser.exe",
            r"C:\Program Files\Tencent\QQBrowser\QQBrowser.exe",
            # 可能的Chromium下载位置
            str(Path.home() / "AppData" / "Local" / "pyppeteer" / "pyppeteer" / "local-chromium" / "chrome-win" / "chrome.exe"),
            str(Path.home() / ".local" / "share" / "pyppeteer" / "local-chromium" / "chrome-win" / "chrome.exe"),
        ]
        
        # 添加版本子目录的检查（处理Chrome可能存在的多个版本）
        chrome_app_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Google\Chrome\Application")
        if os.path.exists(chrome_app_path):
            # 列出Application目录下所有可能的版本子目录
            for item in os.listdir(chrome_app_path):
                version_path = os.path.join(chrome_app_path, item, "chrome.exe")
                if os.path.isfile(version_path):
                    paths.insert(0, version_path)  # 添加到列表最前面（优先级更高）
    elif system == 'Darwin':  # macOS
        paths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
            str(Path.home() / "Library" / "Application Support" / "pyppeteer" / "local-chromium"),
        ]
    else:  # Linux
        paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
            str(Path.home() / ".local" / "share" / "pyppeteer" / "local-chromium"),
        ]
    
    # 检查每个路径是否存在
    for path in paths:
        if os.path.exists(path) and os.path.isfile(path):
            print(f"找到浏览器路径: {path}")
            return path
    
    # 如果找不到任何浏览器路径，则返回None
    print("未找到任何可用的Chrome/Chromium浏览器路径")
    return None


# 扩展用户代理池
def get_random_user_agent():
    USER_AGENTS = [
        # 常用浏览器
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        # 移动设备
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36"
    ]
    return random.choice(USER_AGENTS)


# 获取随机代理
def get_random_proxy():
    # 这里可以替换为您自己的代理池或代理服务
    PROXIES = [
        # 示例代理，请替换为实际可用的代理
        # "http://proxy1.example.com:8080",
        # "http://proxy2.example.com:8080",
        # "http://proxy3.example.com:8080",
        # 如果有账号密码认证的代理，格式如下
        # "http://username:password@proxy.example.com:8080"
    ]
    # 如果没有可用代理，返回None
    if not PROXIES:
        return None
    return random.choice(PROXIES)


# 增强版随机延迟 - 使用更自然的延迟模式
async def random_delay():
    # 使用固定5秒延迟
    delay_time = 5.0  # 固定5秒延迟
    print(f"延迟 {delay_time:.1f} 秒...")
    await asyncio.sleep(delay_time)


# 生成随机请求头
def get_random_headers():
    # 常见的请求头
    languages = ["zh-CN,zh;q=0.9,en;q=0.8", "en-US,en;q=0.9", "zh-TW,zh;q=0.9,en;q=0.8", "ja-JP,ja;q=0.9,en;q=0.8"]
    encodings = ["gzip, deflate, br", "gzip, deflate", "br, gzip, deflate"]
    accepts = [
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    ]
    
    return {
        "Accept": random.choice(accepts),
        "Accept-Encoding": random.choice(encodings),
        "Accept-Language": random.choice(languages),
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }


# 自动处理验证码 (提示人工处理)
async def handle_captcha(page):
    # 检测常见的验证码元素
    captcha_selectors = [
        "input[name*='captcha']", 
        "img[src*='captcha']",
        "div[class*='captcha']",
        "div[id*='captcha']",
        ".recaptcha",
        "#recaptcha",
        ".geetest_panel",
        ".vaptcha"
    ]
    
    for selector in captcha_selectors:
        if await page.querySelector(selector):
            print("检测到验证码，请在浏览器中手动完成验证...")
            # 等待用户处理
            await asyncio.sleep(20)  # 给用户20秒时间处理验证码
            return True
    
    return False


# 增强的手动登录函数
async def manual_login(url: str):
    print(f"正在启动浏览器，请手动登录到 {url}...")
    browser = None
    page = None
    try:
        # 检查系统已安装的浏览器
        chrome_executable = get_executable_path()
        if chrome_executable:
            print(f"找到可用浏览器: {chrome_executable}")
        else:
            print("警告: 未找到可用的Chrome/Chromium浏览器")
            print("请手动安装Chrome浏览器，或设置PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=1并安装playwright")
            print("尝试使用内置下载功能，但可能会失败...")
            
        # 配置浏览器启动参数
        browser_options = {
            'headless': False,  # 必须是可见的才能手动登录
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',  # 禁用同源策略，对某些网站有帮助
                '--disable-features=IsolateOrigins,site-per-process',  # 禁用站点隔离
                '--disable-blink-features=AutomationControlled',  # 隐藏自动化特征
                # 添加随机窗口大小，避免被识别为自动化工具
                f'--window-size={random.randint(1024, 1920)},{random.randint(768, 1080)}'
            ],
            'handleSIGINT': False,
            'handleSIGTERM': False,
            'handleSIGHUP': False,
            'autoClose': False,
            'dumpio': True,
            'ignoreHTTPSErrors': True,  # 忽略HTTPS错误
        }
        
        # 如果找到了可用浏览器，使用它
        if chrome_executable:
            browser_options['executablePath'] = chrome_executable
            # 禁用自动下载Chromium
            os.environ['PUPPETEER_SKIP_CHROMIUM_DOWNLOAD'] = '1'
        
        print("正在启动浏览器...")
        try:
            # 尝试启动浏览器
            browser = await launch(**browser_options)
        except Exception as browser_error:
            print(f"浏览器启动失败: {str(browser_error)}")
            
            # 如果是因为没有设置可执行路径而失败，提供更详细的错误信息
            if "executablePath" not in browser_options:
                print("错误: 没有找到可用的Chrome/Chromium浏览器，且自动下载失败")
                print("解决方案:")
                print("1. 安装Chrome浏览器: https://www.google.com/chrome/")
                print("2. 手动下载匹配版本的Chromium并解压到指定位置")
                print("3. 或者使用playwright库替代pyppeteer (推荐)")
                raise Exception("无法启动浏览器，请安装Chrome或其他Chromium浏览器")
            
            raise
            
        # 创建页面并设置反爬参数
        page = await browser.newPage()
        
        # 设置随机视口大小
        width = random.randint(1024, 1920)
        height = random.randint(768, 1080)
        await page.setViewport({'width': width, 'height': height})
        
        # 设置用户代理
        user_agent = get_random_user_agent()
        await page.setUserAgent(user_agent)
        
        # 设置随机请求头
        headers = get_random_headers()
        await page.setExtraHTTPHeaders(headers)
        
        # 修改Navigator对象，隐藏自动化特征
        await page.evaluateOnNewDocument('''() => {
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    { description: "PDF Viewer", filename: "internal-pdf-viewer" },
                    { description: "Chrome PDF Viewer", filename: "chrome-pdf-viewer" },
                    { description: "Chromium PDF Viewer", filename: "chromium-pdf-viewer" },
                    { description: "Microsoft Edge PDF Viewer", filename: "edge-pdf-viewer" },
                    { description: "WebKit built-in PDF", filename: "webkit-pdf-viewer" }
                ],
            });
        }''')

        # 设置页面超时和等待策略 - 修复方法名
        try:
            # pyppeteer 有时会有不同版本的API
            if hasattr(page, 'setDefaultTimeout'):
                page.setDefaultTimeout(50000)
            elif hasattr(page, 'setDefaultNavigationTimeout'):
                page.setDefaultNavigationTimeout(80000)  # 增加超时时间
            else:
                print("警告: 无法设置页面超时时间，使用默认值")
        except Exception as timeout_error:
            print(f"设置超时时间时出错: {str(timeout_error)}")

        # 添加随机延迟 - 模拟人类行为
        await random_delay()
        
        print(f"正在访问 {url}...")
        try:
            response = await page.goto(url, {
                'waitUntil': 'networkidle2', 
                'timeout': 80000
            })
            
            if response and hasattr(response, 'ok') and not response.ok:
                print(f"警告：页面加载失败，状态码：{response.status}")
        except Exception as nav_error:
            print(f"导航过程中出现错误: {str(nav_error)}")
            print("尝试继续处理...")

        # 检查并处理验证码
        try:
            captcha_detected = await handle_captcha(page)
            if captcha_detected:
                print("验证码已处理，继续登录流程...")
        except Exception as captcha_error:
            print(f"验证码检测过程中出现错误: {str(captcha_error)}")

        print("请完成以下操作：")
        print("1. 手动完成登录")
        print("2. 登录成功后，在此控制台按回车键继续...")

        # 持续检查页面是否被关闭
        check_count = 0
        while check_count < 30:  # 最多检查30次
            try:
                if page.isClosed():
                    print("检测到页面被关闭，正在尝试恢复...")
                    page = await browser.newPage()
                    await page.goto(url)
                
                await asyncio.wait_for(page.evaluate('1+1'), timeout=5)
                break
            except Exception as check_error:
                check_count += 1
                print(f"页面检查出错 ({check_count}/30): {str(check_error)}")
                await asyncio.sleep(1)
        
        if check_count >= 30:
            print("页面检查超时，请确认浏览器是否正常运行")

        input("请在登录成功后按回车键继续...")

        # 再次随机延迟，模拟人类行为
        await random_delay()
        
        # 获取cookies前再次检查页面状态
        if page.isClosed():
            raise Exception("页面已关闭，无法获取cookies")

        try:
            cookies = await page.cookies()
            print("成功获取cookies！")
            
            # 保存当前会话的浏览器指纹信息
            browser_fingerprint = {
                'user_agent': user_agent,
                'headers': headers,
                'viewport': {'width': width, 'height': height},
                'timestamp': time.time()
            }
            
            return {
                'cookies': cookies,
                'fingerprint': browser_fingerprint
            }
        except Exception as cookie_error:
            print(f"获取cookies时出错: {str(cookie_error)}")
            return None

    except Exception as e:
        print(f"登录过程中发生严重错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # 确保资源被正确关闭
        try:
            if page and not page.isClosed():
                await page.close()
            if browser:
                await browser.close()
        except Exception as close_error:
            print(f"关闭浏览器时出错: {str(close_error)}")
            pass


# 增强版爬取和保存Markdown文件的函数
async def crawl_and_save_to_md(url: str, file_path: str, session_data=None):
    global use_proxy_globally
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 准备浏览器配置
            proxy = None
            # 只有在用户选择使用代理且代理可用时才设置代理
            if use_proxy_globally and get_random_proxy():
                proxy = get_random_proxy()
                print(f"使用代理: {proxy}")
            else:
                print("不使用代理")
                
            user_agent = session_data.get('fingerprint', {}).get('user_agent') if session_data else get_random_user_agent()
            
            # 添加额外的浏览器启动参数
            extra_browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                f'--window-size={random.randint(1024, 1920)},{random.randint(768, 1080)}'
            ]
            
            # 创建浏览器配置
            browser_config = BrowserConfig(
                headless=True,
                verbose=True,
                user_agent=user_agent,
                cookies=session_data.get('cookies') if session_data else None,
                proxy=proxy,
                extra_args=extra_browser_args
            )

            async with AsyncWebCrawler(config=browser_config) as crawler:
                # 添加随机延迟
                await random_delay()
                
                # 设置自定义请求头
                headers = session_data.get('fingerprint', {}).get('headers') if session_data else get_random_headers()
                
                print(f"正在爬取 {url}...")
                print(f"使用UA: {user_agent[:30]}...")
                
                try:
                    # 使用try-except包装crawler.arun调用
                    result = await crawler.arun(
                        url=url, 
                        headers=headers,
                        wait_time=random.uniform(3, 8)  # 随机等待时间，模拟人类阅读行为
                    )
                    
                    # 检查爬取结果
                    if hasattr(result, 'success') and result.success:
                        print("爬取成功，正在保存为Markdown文件...")
                        
                        # 确保目录存在
                        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                        
                        # 检查markdown属性是否存在
                        if hasattr(result, 'markdown') and result.markdown:
                            with open(file_path, "w", encoding="utf-8") as file:
                                file.write(result.markdown)
                            print(f"Markdown文件已保存到 {file_path}")
                            print("\n内容预览：")
                            print(result.markdown[:500] if len(result.markdown) > 500 else result.markdown)
                            return True
                        else:
                            print("爬取结果中没有Markdown内容")
                    else:
                        # 安全获取错误信息
                        error_msg = getattr(result, 'error', None) or "未知错误"
                        if isinstance(error_msg, Exception):
                            error_msg = str(error_msg)
                        print(f"爬取失败，错误信息：{error_msg}")
                        
                        # 检查是否是代理错误
                        if proxy and ("proxy" in str(error_msg).lower() or "err_proxy" in str(error_msg).lower()):
                            print("代理连接失败，下次尝试将不使用代理")
                            # 全局禁用代理
                            use_proxy_globally = False
                
                except Exception as run_error:
                    print(f"执行爬取时出错: {str(run_error)}")
                
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = random.uniform(5, 10) * retry_count
                    print(f"重试中 ({retry_count}/{max_retries})...将在 {wait_time:.1f} 秒后重试")
                    await asyncio.sleep(wait_time)
            
        except Exception as e:
            print(f"爬取过程中发生错误: {e}")
            retry_count += 1
            if retry_count < max_retries:
                wait_time = random.uniform(5, 10) * retry_count
                print(f"重试中 ({retry_count}/{max_retries})...将在 {wait_time:.1f} 秒后重试")
                await asyncio.sleep(wait_time)
            else:
                print("达到最大重试次数，爬取失败")
                return False
    
    return False


# 提供用户交互界面
async def async_main():
    global use_proxy_globally
    
    print("欢迎使用高级网页爬取工具！")
    print("当前系统信息:")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    
    # 检查是否有Chrome/Chromium
    chrome_path = get_executable_path()
    if chrome_path:
        print(f"检测到浏览器: {chrome_path}")
    else:
        print("警告: 未检测到Chrome/Chromium浏览器，可能影响程序运行")
        print("建议安装Chrome浏览器: https://www.google.com/chrome/")
        
    url_to_crawl = input("请输入要爬取的网址: ").strip()
    while not url_to_crawl.startswith(('http://', 'https://')):
        print("网址格式不正确，请包含http://或https://")
        url_to_crawl = input("请重新输入要爬取的网址: ").strip()

    file_name = input("请输入保存的Markdown文件名（包含路径）: ").strip()
    if not file_name.endswith('.md'):
        file_name += '.md'

    need_login = input("该网址是否需要登录（yes/no）？").strip().lower()
    max_retries = 3
    
    # 添加更多反爬选项
    use_proxy_globally = input("是否使用代理（yes/no）？").strip().lower() == 'yes'
    
    # 警告用户代理问题
    if use_proxy_globally and not get_random_proxy():
        print("警告: 您选择了使用代理，但没有配置可用的代理服务器")
        print("请在代码中的get_random_proxy函数中添加可用的代理服务器")
        use_again = input("是否继续使用代理功能？(yes/no): ").strip().lower()
        use_proxy_globally = use_again == 'yes'
    
    # 使用固定延迟 (5秒)
    print("使用固定延迟: 5秒")

    for attempt in range(1, max_retries + 1):
        try:
            session_data = None
            if need_login == 'yes':
                print(f"尝试登录（第{attempt}次）...")
                session_data = await manual_login(url_to_crawl)
                if not session_data:
                    if attempt == max_retries:
                        print("登录失败，放弃爬取。")
                        return
                    print("登录失败，5秒后重试...")
                    await asyncio.sleep(5)
                    continue
                print("登录成功，开始爬取...")
            
            success = await crawl_and_save_to_md(url_to_crawl, file_name, session_data)
            if success:
                print("爬取完成！")
                break
            elif attempt == max_retries:
                print("已达到最大重试次数，程序退出。")
            else:
                print(f"爬取失败，5秒后重试（第{attempt+1}次）...")
                await asyncio.sleep(5)
                
        except Exception as e:
            print(f"操作失败（第{attempt}次尝试）: {str(e)}")
            if attempt == max_retries:
                print("已达到最大重试次数，程序退出。")
                return
            await asyncio.sleep(5)  # 等待5秒后重试


if __name__ == "__main__":
    # 配置日志
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # 创建新的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # 运行主程序
        loop.run_until_complete(async_main())
    except KeyboardInterrupt:
        print("\n用户中断操作，程序退出。")
    except Exception as e:
        print(f"程序发生未捕获的异常: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        # 彻底清理
        try:
            # 取消所有待处理任务
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()

            # 等待任务取消完成
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

            # 关闭循环
            loop.close()
        except:
            pass

        print("程序完全退出。")