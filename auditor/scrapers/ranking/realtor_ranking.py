import logging
import time
from datetime import datetime
from queue import Queue

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from auditor.agent import Agent
from auditor.scrapers.base_scraper import strip_html_tags
from auditor.scrapers.ranking.base_ranking_scraper import BaseRankingScraper


class RealtorRanking(BaseRankingScraper):
    logger = logging.getLogger(__name__)

    # def __init__(self, query, delay: int, num_ads: int = 10, category: BaseRankingScraper.ScrapeType = BaseRankingScraper.ScrapeType.BUY):
    #     super().__init__(query, delay, num_ads, category)

    @staticmethod
    def extract_elem(driver, record, name, ad, elem_selector):
        try:
            record[name] = strip_html_tags(ad.find_element_by_css_selector(elem_selector).get_attribute('innerHTML'))
        except NoSuchElementException:
            driver.save_screenshot(f"output/failures/{datetime.now()}.png")
            RealtorRanking.logger.exception("Malformed listing: \n\n%s\n\n", ad.text)

    @staticmethod
    def transform_ad(driver, ad: WebElement, category):
        record = dict()
        record["type"] = str(category)
        record["data-url"] = ad.get_property('data-url')
        RealtorRanking.extract_elem(driver, record, "price", ad, "span.data-price")
        RealtorRanking.extract_elem(driver, record, "beds", ad, "li[data-label='property-meta-beds'] span")
        RealtorRanking.extract_elem(driver, record, "baths", ad, "li[data-label='property-meta-baths'] span")
        # RealtorRanking.extract_elem(driver, record, "square feet", ad, "li[data-label='property-meta-sqft'] span")
        RealtorRanking.extract_elem(driver, record, "street address", ad, "div[data-label='property-address'] span.listing-street-address")
        RealtorRanking.extract_elem(driver, record, "locality", ad, "div[data-label='property-address'] span.listing-city")
        RealtorRanking.extract_elem(driver, record, "region", ad, "div[data-label='property-address'] span.listing-region")
        RealtorRanking.extract_elem(driver, record, "postal code", ad, "div[data-label='property-address'] span.listing-postal")
        RealtorRanking.extract_elem(driver, record, "realtor", ad, "div.broker-info")
        try:
            record["latitude"] = strip_html_tags(ad.find_element_by_css_selector("span[itemprop='geo'] meta[itemprop='latitude']").get_attribute('content'))
            record["longitude"] = strip_html_tags(ad.find_element_by_css_selector("span[itemprop='geo'] meta[itemprop='longitude']").get_attribute('content'))
        except NoSuchElementException:
            driver.save_screenshot(f"output/failures/{datetime.now()}.png")
            RealtorRanking.logger.exception("Malformed listing: \n\n%s\n\n", ad.text)
        return record

    def __call__(self, unit: Agent, queue: Queue):
        driver = unit.driver
        time.sleep(self.delay)
        try:
            driver.get("https://www.realtor.com")
            ActionChains(driver).pause(5).perform()
            actions = ActionChains(driver).pause(1)

            if self.category == RealtorRanking.ScrapeType.RENT:
                actions.click(driver.find_element_by_css_selector("li.home-nav-item a[title='Homes for rent']")).pause(
                    2)

            input_field = driver.find_element_by_css_selector(
                "label#rdc-main-search-nav-hero input[data-label='searchbox-input']")
            actions.click(input_field) \
                .send_keys(self.query) \
                .send_keys(Keys.RETURN) \
                .pause(2) \
                .perform()
            # driver.find_element_by_css_selector("select#sortingOptions").click()
            # driver.find_element_by_xpath('//option[contains(.,"Sort: Just For You")]').click()
        except NoSuchElementException:
            now = str(datetime.now())
            driver.save_screenshot(f"output/failures/{now}.png")
            self.logger.exception("Could not find ranked page element: %s, %s", driver.current_url, now)
            return
        try:
            ActionChains(driver).pause(5).perform()
            ads = driver.find_elements_by_css_selector("li.js-component_property-card")
            if len(ads) == 0:
                self.logger.error("No ads found")
                return
            ads = ads[:self.num_ads]
            ads = [self.transform_ad(driver, ad, self.category) for ad in ads]
            self.log_scraped_ranking(queue, unit, self, ads)
        except NoSuchElementException:
            self.logger.exception("Unexpected exception")
