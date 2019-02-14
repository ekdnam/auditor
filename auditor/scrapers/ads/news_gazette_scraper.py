import logging
import time
from queue import Queue

from selenium.common.exceptions import NoSuchElementException

from auditor.agent import Agent
from auditor.scrapers.ads.base_ad_scrapers import BaseAdScraper


class NewsGazetteAdScraper(BaseAdScraper):
    logger = logging.getLogger(__name__)

    def __init__(self, delay: int = 30, pages: int = 3):
        super().__init__('champaign', delay, pages)

    def __call__(self, unit: Agent, queue: Queue):
        driver = unit.driver
        driver.get('http://www.news-gazette.com/classified/real-estate')
        time.sleep(self.delay)
        for page in range(self.pages):
            ads = driver.find_elements_by_css_selector('div[id^="google_ads_iframe"]')
            if len(ads) == 0:
                self.logger.error("No ads found")
                break
            for ad in ads:
                try:
                    ad_filename = self.screenshot_elem(driver, ad)
                    self.log_scraped_ad(queue, unit, self, {
                        "image_path": ad_filename,
                    })
                except NoSuchElementException:
                    self.logger.info("Malformed ad")
            try:
                button = driver.find_element_by_css_selector("li.pager-next a")
                button.click()
                time.sleep(10)
            except NoSuchElementException:
                self.logger.debug("No next page")
                break
