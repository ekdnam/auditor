import logging
import time
from queue import Queue

from selenium.common.exceptions import NoSuchElementException

from auditor.agent import Agent
from auditor.scrapers.advertisement.base_ad_scrapers import BaseAdScraper


class ChicagoReaderScraper(BaseAdScraper):
    logger = logging.getLogger(__name__)

    def __init__(self, delay: int, pages: int = 1):
        super().__init__('chicago', delay, pages)

    def __call__(self, unit: Agent, queue: Queue):
        driver = unit.driver
        for rep in range(self.pages):
            time.sleep(self.delay)
            try:
                driver.get("https://www.chicagoreader.com/chicago/classifieds/Content?category=61309067")
            except NoSuchElementException:
                self.logger.exception("Could not load main page")
                return

            try:
                ads = driver.find_elements_by_css_selector('iframe[id^="google_ads_iframe"]')
                for ad in ads:
                    try:
                        ad_filename = self.screenshot_elem(driver, ad)
                        self.log_scraped_ad(queue, unit, self, {
                            "image_path": ad_filename,
                        })
                    except NoSuchElementException:
                        self.logger.info("Malformed ad")
            except NoSuchElementException:
                self.logger.exception("Could not get ads")




