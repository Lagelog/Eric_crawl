import asyncio
import random
from crawl4ai import AsyncWebCrawler, BrowserConfig
from pyppeteer import launch


# 随机选择一个用户代理
def get_random_user_agent():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0"
    ]
    return random.choice(USER_AGENTS)


# 随机延迟
async def random_delay():
    await asyncio.sleep(random.uniform(1, 3))  # 随机延迟1-3秒


# 手动登录并获取登录后的浏览器会话
async def manual_login(url: str):
    print(f"正在启动浏览器，请手动登录到 {url}...")
    browser = await launch(headless=False, executablePath=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    page = await browser.newPage()
    await page.setUserAgent(get_random_user_agent())  # 设置随机用户代理
    await page.goto(url)

    # 使用 asyncio.Event 等待用户完成登录操作
    done = asyncio.Event()

    async def close_handler():
        done.set()

    # 监听浏览器关闭事件
    browser.on('disconnected', lambda: asyncio.create_task(close_handler()))

    print("请手动完成登录操作，登录完成后关闭浏览器窗口。")
    await done.wait()  # 等待用户关闭浏览器

    # 获取登录后的cookies
    cookies = await page.cookies()

    # 手动关闭浏览器
    try:
        await browser.close()
    except Exception as e:
        print(f"关闭浏览器时出现问题：{e}")

    return cookies


# 封装的爬取和保存Markdown文件的函数
async def crawl_and_save_to_md(url: str, file_path: str, cookies=None):
    """
    爬取指定网址并保存为Markdown文件

    :param url: 要爬取的网址
    :param file_path: 保存Markdown文件的路径
    :param cookies: 登录后的cookies
    """
    # 创建浏览器配置
    browser_config = BrowserConfig(
        headless=True,  # 设置为True以无头模式运行
        verbose=True,
        user_agent=get_random_user_agent(),  # 设置随机用户代理
        cookies=cookies  # 使用登录后的cookies
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # 爬取指定网址
        await random_delay()
        result = await crawler.arun(url=url)

        if result.success:
            print("爬取成功，正在保存为Markdown文件...")
            # 将爬取结果保存为本地Markdown文件
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(result.markdown)
            print(f"Markdown文件已保存到 {file_path}")

            # 可选：打印部分内容预览
            print("\n内容预览：")
            print(result.markdown[:500])  # 打印前500个字符
        else:
            print(f"爬取失败，错误信息：{result.error}")


# 提供用户交互界面
def main():
    print("欢迎使用网页爬取工具！")
    url_to_crawl = input("请输入要爬取的网址: ")
    file_name = input("请输入保存的Markdown文件名（包含路径，例如D:\\Downloads\\example.md）: ")

    # 检查文件名是否以.md结尾
    if not file_name.endswith('.md'):
        file_name += '.md'

    # 检查是否需要登录
    need_login = input(f"该网址是否需要登录（yes/no）？").strip().lower()
    if need_login == 'yes':
        print("正在启动手动登录流程...")
        try:
            cookies = asyncio.run(manual_login(url_to_crawl))
            print("登录完成，开始爬取...")
            asyncio.run(crawl_and_save_to_md(url_to_crawl, file_name, cookies))
        except Exception as e:
            print(f"登录过程中出现问题：{e}")
            print("请检查网页链接的合法性，或尝试切换网络环境后重试。")
    else:
        print(f"正在爬取 {url_to_crawl} 并保存为 {file_name}...")
        asyncio.run(crawl_and_save_to_md(url_to_crawl, file_name))


if __name__ == "__main__":
    main()