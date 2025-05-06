import asyncio
import random
from crawl4ai import AsyncWebCrawler, BrowserConfig


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


# 封装的爬取和保存Markdown文件的函数
async def crawl_and_save_to_md(url: str, file_path: str):
    """
    爬取指定网址并保存为Markdown文件

    :param url: 要爬取的网址
    :param file_path: 保存Markdown文件的路径
    """
    # 创建浏览器配置
    browser_config = BrowserConfig(
        headless=True,  # 设置为True以无头模式运行
        verbose=True,
        user_agent=get_random_user_agent(),  # 设置随机用户代理
        # 不需要设置代理和cookies
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

    print(f"正在爬取 {url_to_crawl} 并保存为 {file_name}...")
    asyncio.run(crawl_and_save_to_md(url_to_crawl, file_name))


if __name__ == "__main__":
    main()