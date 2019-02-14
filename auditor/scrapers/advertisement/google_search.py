import logging
import time
from datetime import datetime
from queue import Queue
from threading import Semaphore

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from auditor.agent import Agent
from auditor.scrapers.advertisement.base_ad_scrapers import BaseAdScraper
from auditor.scrapers.base_scraper import strip_html_tags

INPUT_SELECTOR = "input[title='Search']"


class GoogleSearchAdScraper(BaseAdScraper):
    logger = logging.getLogger(__name__)
    scrape_lock = Semaphore(2)

    def __init__(self, query: str, delay: int, pages: int = 3):
        super().__init__(query, delay, pages)

    def __call__(self, unit: Agent, queue: Queue):
        with GoogleSearchAdScraper.scrape_lock:
            driver = unit.driver
            time.sleep(self.delay)
            try:
                driver.get("https://www.google.com/")
                search_bar = driver.find_element_by_css_selector(INPUT_SELECTOR)
                ActionChains(driver) \
                    .pause(1) \
                    .send_keys_to_element(search_bar, self.query) \
                    .send_keys_to_element(search_bar, Keys.RETURN) \
                    .perform()
            except NoSuchElementException:
                self.logger.exception("Unexpected exception")

            for page in range(self.pages):
                time.sleep(self.delay)
                if "https://www.google.com/sorry/index" in driver.current_url:
                    self.logger.error("Hit anti-bot captcha on page %i", page)
                    return

                ads = driver.find_elements_by_css_selector("li.ads-ad")
                for ad in ads:
                    try:
                        title = ad.find_element_by_css_selector('div.ad_cclk a:not([style*="display:none"])').text
                        body = strip_html_tags(str(ad.find_element_by_css_selector("div.ads-creative")
                                                   .get_attribute('innerHTML')))
                        parsed_ad = dict()
                        parsed_ad['query'] = self.query
                        parsed_ad['title'] = strip_html_tags(title)
                        parsed_ad['url'] = ad.find_element_by_css_selector("div.ads-visurl cite").text
                        parsed_ad['body'] = strip_html_tags(body)
                        self.log_scraped_ad(queue, unit, self, parsed_ad)
                        self.logger.debug("Complete ad: %s", ad.get_attribute('outerHTML'))
                    except NoSuchElementException:
                        self.logger.exception("Unparseable ad: %s", ad.get_attribute('outerHTML'))
                try:
                    driver.execute_script("arguments[0].scrollIntoView();",
                                          driver.find_element_by_css_selector("#pnnext"))
                    driver.find_element_by_css_selector("#pnnext").click()
                except NoSuchElementException:
                    filename = str(datetime.now()) + '.screenie.png'
                    driver.save_screenshot(filename)
                    self.logger.exception("Element not found: %s", filename)
