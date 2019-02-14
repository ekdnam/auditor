import logging
from datetime import datetime
from queue import Queue
import time
from threading import Semaphore

from selenium.common.exceptions import NoSuchElementException

from auditor.agent import Agent
from auditor.scrapers.base_scraper import strip_html_tags
from auditor.scrapers.ranking.base_ranking_scraper import BaseRankingScraper


class TruliaScraper(BaseRankingScraper):
    logger = logging.getLogger(__name__)
    scrape_lock = Semaphore(1)

    # def __init__(self, query, delay: int, pages):
    #     super().__init__(None, delay, 1)
    #     self.location = location
    #     self.num_ads = num_ads
    #     self.category = category

    def transform_ad(self, ad):
        try:
            return {
                "type": str(self.category),
                "price": strip_html_tags(ad.find_element_by_css_selector("span.cardPrice").text),
                "beds": strip_html_tags(ad.find_element_by_css_selector(
                    "li[data-testid='beds']").get_attribute('innerHTML')),
                "baths": strip_html_tags(ad.find_element_by_css_selector(
                    "li[data-testid='baths']").get_attribute('innerHTML')),
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
            TruliaScraper.logger.exception("Malformed listing: \n\n%s\n\n", ad.text)

    def __call__(self, unit: Agent, queue: Queue):
        driver = unit.driver
        with TruliaScraper.scrape_lock:
            time.sleep(self.delay)
            i = 0
            try:
                driver.get("https://www.trulia.com")
                # ActionChains(driver).pause(5).perform()
                time.sleep(5)
                # driver.save_screenshot(f"output/checkups/test-{unit.agent_id}-{i}.png")
                # i += 1
                # actions = ActionChains(driver).pause(1)
                time.sleep(1)

                if self.category == TruliaScraper.ScrapeType.RENT:
                    driver.find_element_by_xpath('//button[contains(.,"Rent")]').click()
                    time.sleep(2)
                    # actions.click(driver.find_element_by_xpath('//button[contains(.,"Rent")]')).pause(2)

                input_field = driver.find_element_by_css_selector("input#homepageSearchBoxTextInput")
                input_field.send_keys(self.query)
                driver.find_element_by_css_selector("button.homepageSearchButton").click()
                # actions.click(input_field) \
                #     .send_keys(self.location) \
                #     .send_keys(Keys.RETURN) \
                #     .pause(2) \
                #     .perform()

                # print("Selected new page")
                # driver.save_screenshot(f"output/checkups/test-{unit.agent_id}-{i}.png")
                # i += 1
                # print("Screenshotted")
                # driver.find_element_by_css_selector("select#sortingOptions").click()
                # driver.find_element_by_xpath('//option[contains(.,"Sort: Just For You")]').click()
            except NoSuchElementException:
                now = str(datetime.now())
                # driver.save_screenshot(f"output/failures/{now}.png")
                self.logger.exception("Could not find search element: %s, %s", driver.current_url, now)
                return
            try:
                # ActionChains(driver).pause(5).perform()
                time.sleep(5)
                # print("Screenshotted 2")
                # driver.save_screenshot(f"output/checkups/test-{unit.agent_id}-{i}.png")
                self.logger.debug("Page source: %s", driver.page_source)
                i += 1
                ads = driver.find_elements_by_css_selector("div#resultsColumn ul li div.card")
                if len(ads) == 0:
                    now = str(datetime.now())
                    driver.save_screenshot(f"output/failures/{unit.agent_id}-{now}.png")
                    self.logger.error("No ads found, %s", now)
                    return
                ads = ads[:self.num_ads]
                ads = [self.transform_ad(ad) for ad in ads]
                self.log_scraped_ranking(queue, unit, self, ads)
            except NoSuchElementException:
                self.logger.exception("Unexpected exception")
