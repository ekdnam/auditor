import logging
import time
from urllib.parse import urlparse, ParseResult

from selenium.common.exceptions import WebDriverException, TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.remote.webdriver import WebDriver

from auditor.trainers.base_trainer import TrainingStep

import requests

def connected_to_internet(url='http://www.google.com/', timeout=5):
    try:
        _ = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("No internet connection available.")
    return False


class SiteVisitor(TrainingStep):
    logger = logging.getLogger(__name__)

    def __init__(self, site_list, delay: int = 20):
        super().__init__(delay)
        self.site_list = site_list

    def __call__(self, unit):
        driver: WebDriver = unit.driver
        count = {}
        site_list = self.site_list
        for urlx in site_list:
            count[urlx] = 0
        for urlx in site_list:
            url: ParseResult = urlparse(urlx)
            if not url.scheme:
                url = url._replace(scheme='https')
            try:
                if not connected_to_internet():
                    print("Not connected to internet.")
                print("Accessing URL: ", url.geturl())
                count[urlx] += 1
                unit.driver.get(url.geturl())
            except Exception as e:
                print("Unexpected exception: Site %s", url.geturl())
                print(e)
                if urlx in count:
                    if count[urlx] < 3:
                        site_list.append(urlx)
                        count[urlx] += 1
                        print("Adding url back to list: ", url)
            time.sleep(self.delay)
