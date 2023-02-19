import logging
import time
from urllib.parse import urlparse, ParseResult

from selenium.common.exceptions import WebDriverException, TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.remote.webdriver import WebDriver

from auditor.trainers.base_trainer import TrainingStep


class SiteVisitor(TrainingStep):
    logger = logging.getLogger(__name__)

    def __init__(self, site_list, delay: int = 20):
        super().__init__(delay)
        self.site_list = site_list

    def __call__(self, unit):
        driver: WebDriver = unit.driver
        for url in self.site_list:
            url: ParseResult = urlparse(url)
            if not url.scheme:
                url = url._replace(scheme='https')
            try:
                self.logger.info("accessing url: ", str(url))
                unit.driver.get(url.geturl())
            except TimeoutException:
                self.logger.info("Site '%s' timeout", url.geturl())
            except UnexpectedAlertPresentException:
                self.logger.info("Unexpected alert on site %s", url.geturl())
                driver.save_screenshot(f"{url.hostname}.alert.png")
            except WebDriverException:
                self.logger.exception("Unexpected exception: Site %s", url.geturl())
            time.sleep(self.delay)
