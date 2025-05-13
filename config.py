import os
from pathlib import Path

# 基础路径配置
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'
DOWNLOAD_DIR = BASE_DIR / 'downloads'

# 创建必要的目录
TEMPLATES_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
DOWNLOAD_DIR.mkdir(exist_ok=True)

# 服务器配置
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 5000))
DEBUG = True

# 爬虫配置
DEFAULT_TIMEOUT = 30000  # 毫秒
DEFAULT_WAIT_TIME = (15, 25)  # 随机等待时间范围(秒)
PAGE_LOAD_WAIT = 10  # 页面加载等待时间(秒)
IFRAME_LOAD_WAIT = 3  # iframe加载等待时间(秒)

# 浏览器配置
BROWSER_ARGS = [
    '--disable-blink-features=AutomationControlled',
    '--disable-web-security',
    '--disable-features=IsolateOrigins,site-per-process',
    '--no-sandbox',
    '--ignore-certificate-errors',
    '--disable-gpu',
    '--disable-setuid-sandbox',
    '--disable-infobars',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--disable-extensions',
    '--disable-background-networking',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-breakpad',
    '--disable-component-extensions-with-background-pages',
    '--disable-component-update',
    '--disable-domain-reliability',
    '--disable-hang-monitor',
    '--disable-ipc-flooding-protection',
    '--disable-notifications',
    '--disable-offer-store-unmasked-wallet-cards',
    '--disable-popup-blocking',
    '--disable-print-preview',
    '--disable-prompt-on-repost',
    '--metrics-recording-only',
    '--no-default-browser-check',
    '--no-first-run',
    '--no-pings',
    '--password-store=basic',
    '--use-mock-keychain',
    '--disable-sync',
    '--autoplay-policy=no-user-gesture-required',
    '--window-position=0,0',
    '--window-size=1920,1080'
]

# 新浪特定配置
SINA_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Referer': 'https://www.sina.com.cn/'
}

SINA_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36" 