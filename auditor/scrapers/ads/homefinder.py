import logging
import time
from queue import Queue

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from auditor.agent import Agent
from auditor.scrapers.ads.base_ad_scrapers import BaseAdScraper
from auditor.scrapers.base_scraper import strip_html_tags

INPUT_SELECTOR = "div.full-search div.search-box input"


class HomeFinderAdScraper(BaseAdScraper):
    logger = logging.getLogger(__name__)

    def __init__(self, query, delay: int, pages: int = 1):
        super().__init__(query, delay, pages)

    def __call__(self, unit: Agent, queue: Queue):
        driver = unit.driver
        for rep in range(self.pages):
            time.sleep(self.delay)
            try:
                driver.get("https://homefinder.com")
                search_bar = driver.find_element_by_css_selector(INPUT_SELECTOR)
                ActionChains(driver) \
                    .pause(1) \
                    .send_keys_to_element(search_bar, self.query) \
                    .send_keys_to_element(search_bar, Keys.RETURN) \
                    .perform()
            except NoSuchElementException:
                self.logger.exception("Could not load main page")
                return

            # Scrape sidebar
            try:
                frame = driver.find_element_by_css_selector('div#adSenseForSearchRightRail iframe')
                driver.switch_to.frame(frame)
                ads = driver.find_element_by_css_selector('div#adBlock div.a_')
                for ad in ads:
                    parsed_ad = dict()
                    parsed_ad['url'] = strip_html_tags(
                        ad.find_element_by_css_selector("a.test_domainLink").get_attribute('innerHTML'))
                    parsed_ad['title'] = strip_html_tags(
                        ad.find_element_by_css_selector("a.test_titleLink").get_attribute('innerHTML'))
                    parsed_ad['body'] = strip_html_tags(
                        ad.find_element_by_css_selector("span.descText").get_attribute('innerHTML'))
                    parsed_ad['additional'] = strip_html_tags(
                        ad.find_element_by_css_selector('div.hd_').get_attribute('innerHTML'))
                    self.log_scraped_ad(queue, unit, self, parsed_ad)
                    self.logger.debug("Complete ad: %s", ad.get_attribute('outerHTML'))
            except NoSuchElementException:
                self.logger.exception("Could not get sidebar ads")
            finally:
                driver.switch_to.default_content()

            # Scrape ad block at bottom of page
            try:
                frame = driver.find_element_by_css_selector("div#googleAdsenseContainer > iframe")
                driver.switch_to.frame(frame)
                ads = driver.find_elements_by_css_selector("div#adBlock div.a_")
                for ad in ads:
                    try:
                        parsed_ad = dict()
                        parsed_ad['url'] = strip_html_tags(
                            ad.find_element_by_css_selector("a.test_domainLink").get_attribute('innerHTML'))
                        parsed_ad['title'] = strip_html_tags(
                            ad.find_element_by_css_selector("a.test_titleLink").get_attribute('innerHTML'))
                        parsed_ad['body'] = strip_html_tags(
                            ad.find_element_by_css_selector("span.descText").get_attribute('innerHTML'))
                        parsed_ad['additional'] = strip_html_tags(
                            ad.find_element_by_css_selector('div.hd_').get_attribute('innerHTML'))
                        self.log_scraped_ad(queue, unit, self, parsed_ad)
                        self.logger.debug("Complete ad: %s", ad.get_attribute('outerHTML'))
                    except NoSuchElementException:
                        self.logger.exception("Could not scrape ad: %s", ad.get_attribute('outerHTML'))
                driver.switch_to.default_content()
            except NoSuchElementException:
                self.logger.exception("Could not get main page and ads")
            finally:
                driver.switch_to.default_content()
