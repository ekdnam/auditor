import os

from dotenv import load_dotenv, find_dotenv
from selenium.webdriver import Proxy
from selenium.webdriver.common.proxy import ProxyType

load_dotenv(find_dotenv())

SOCKS_PROXY = os.getenv("SOCKS_PROXY")
SOCKS_USERNAME = os.getenv("SOCKS_USERNAME")
SOCKS_PASSWORD = os.getenv("SOCKS_PASSWORD")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSHOVER_USERKEY = os.getenv("PUSHOVER_USERKEY")

if SOCKS_PROXY is not None and SOCKS_USERNAME is not None and SOCKS_PASSWORD is not None:
    proxy_config = Proxy({
        "proxyType": ProxyType.MANUAL,
        "socksProxy": SOCKS_PROXY,
        "socksUsername": SOCKS_USERNAME,
        "socksPassword": SOCKS_PASSWORD,
    })
else:
    proxy_config = None
