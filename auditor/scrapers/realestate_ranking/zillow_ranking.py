import logging
from datetime import datetime
from queue import Queue
import time
from threading import Semaphore

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from auditor.agent import Agent
from auditor.scrapers.base_scraper import strip_html_tags
from auditor.scrapers.realestate_ranking.base_ranking_scraper import BaseRankingScraper


class ZillowScraper(BaseRankingScraper):
    logger = logging.getLogger(__name__)
    scrape_lock = Semaphore(2)

    # def __init__(self, query, delay: int, num_ads: int = 10):
    #     super().__init__(query, delay, 1, num_ads=num_ads)

    def transform_ad(self, ad):
        try:
            return {
                "type": str(self.category),
                "price": strip_html_tags(ad.find_element_by_css_selector(
                    ".zsg-photo-card-price").get_attribute('innerHTML')),
                "street address": strip_html_tags(ad.find_element_by_css_selector(
                    "span[itemprop='address'] span[itemprop='streetAddress']").get_attribute('innerHTML')),
                "locality": strip_html_tags(ad.find_element_by_css_selector(
                    "span[itemprop='address'] span[itemprop='addressLocality']").get_attribute('innerHTML')),
                "region": strip_html_tags(ad.find_element_by_css_selector(
                    "span[itemprop='address'] span[itemprop='addressRegion']").get_attribute('innerHTML')),
                "postal code": strip_html_tags(ad.find_element_by_css_selector(
                    "span[itemprop='address'] span[itemprop='postalCode']").get_attribute('innerHTML')),
                "latitude": strip_html_tags(ad.find_element_by_css_selector(
                    "span[itemprop='geo'] meta[itemprop='latitude']").get_attribute('content')),
                "longitude": strip_html_tags(ad.find_element_by_css_selector(
                    "span[itemprop='geo'] meta[itemprop='longitude']").get_attribute('content')),
            }
        except NoSuchElementException:
            ZillowScraper.logger.exception("Malformed listing: \n\n%s\n\n", ad.text)

    def __call__(self, unit: Agent, queue: Queue, category=BaseRankingScraper.ScrapeType.BUY):
        with ZillowScraper.scrape_lock:
            driver = unit.driver
            time.sleep(self.delay)
            try:
                driver.get("https://www.zillow.com")
                searchbar = driver.find_element_by_css_selector("div.search-container form div input")
                actions = ActionChains(driver).pause(1)

                if category == ZillowScraper.ScrapeType.RENT:
                    rent_tab = driver.find_element_by_css_selector("a[href='/rent']")
                    actions.click(rent_tab).pause(1)

                actions.click(searchbar) \
                    .send_keys(self.query) \
                    .send_keys(Keys.RETURN) \
                    .pause(2) \
                    .perform()

                button = driver.find_element_by_link_text('Homes for You')
                button.click()
            except NoSuchElementException:
                now = str(datetime.now())
                self.logger.warning("Could not find ranked page element: %s, %s", driver.current_url, now)
                driver.save_screenshot(f"output/failures/{now}.png")
                return
            try:
                ads = driver.find_elements_by_css_selector("div#search-results ul.photo-cards li article")
                if len(ads) == 0:
                    self.logger.error("No ads found")
                    return
                ads = ads[:self.num_ads]
                ads = [self.transform_ad(ad) for ad in ads]
                self.log_scraped_ranking(queue, unit, self, ads)
            except NoSuchElementException:
                self.logger.exception("Unexpected exception")
