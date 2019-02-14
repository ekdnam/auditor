import logging
import time

from selenium.common.exceptions import NoSuchElementException

from auditor.scrapers.advertisement.base_ad_scrapers import BaseAdScraper


class CNNAdScraper(BaseAdScraper):
    logger = logging.getLogger(__name__)

    def __init__(self, delay: int = 60, pages: int = 1):
        super().__init__('', delay, pages)

    def __call__(self, unit, queue):
        driver = unit.driver
        for rep in range(self.pages):
            time.sleep(self.delay)
            try:
                driver.get("https://www.cnn.com/us")
                ads = driver.find_elements_by_css_selector('iframe[id^="google_ads_iframe"]')
            except:
                self.logger.exception("Could not get main page and ads")
                return
            for ad in ads:
                try:
                    ad_filename = self.screenshot_elem(driver, ad)
                    self.log_scraped_ad(queue, unit, self, {
                        "image_path": ad_filename,
                    })
                except NoSuchElementException:
                    self.logger.info("Malformed ad")
