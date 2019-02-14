import json
import logging
import time
from datetime import datetime
from queue import Queue

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains

from auditor.agent import Agent
from auditor.scrapers.realestate_ranking.base_ranking_scraper import BaseRankingScraper


class RedfinScraper(BaseRankingScraper):
    logger = logging.getLogger(__name__)

    # def __init__(self, query, delay: int, pages):
    #     super().__init__(None, delay, 1)
    #     self.location = location
    #     self.num_ads = num_ads

    def transform_ad(self, ad):
        try:
            details = {
                'type': str(self.category)
            }
            for data in ad.find_elements_by_css_selector("script"):
                parsed = json.loads(data.get_attribute('innerHTML'))
                if 'location' in parsed:
                    if 'address' in parsed['location']:
                        details['street address'] = parsed['location']['address']['streetAddress']
                        details['locality'] = parsed['location']['address']['addressLocality']
                        details['region'] = parsed['location']['address']['addressRegion']
                        details['postal code'] = parsed['location']['address']['postalCode']
                    if 'geo' in parsed['location']:
                        details['latitude'] = parsed['location']['geo']['latitude']
                        details['longitude'] = parsed['location']['geo']['longitude']
                if 'offers' in parsed:
                    details['price'] = parsed['offers']['price']
            return details
        except NoSuchElementException:
            RedfinScraper.logger.exception("Malformed listing: \n\n%s\n\n", ad.text)

    def __call__(self, unit: Agent, queue: Queue):
        driver = unit.driver
        time.sleep(self.delay)
        try:
            driver.get(f"https://www.redfin.com/{self.query}")
            # searchbar = driver.find_element_by_css_selector("div.home-hero-outer input.search-input-box")
            ActionChains(driver) \
                .pause(5) \
                .perform()
            #     .click(searchbar) \
            #     .send_keys(self.location) \
            #     .send_keys(Keys.RETURN) \
            #     .pause(2) \
            #
            # link = driver.find_element_by_link_text(self.link_name)
            #
            # ActionChains(driver) \
            #     .click(link) \
            #     .pause(2) \
            #     .perform()
        except NoSuchElementException:
            self.logger.warning("Could not find page element: %s", driver.current_url)
            driver.save_screenshot(f"output/failures/{datetime.now()}.png")
            return
        try:
            ads = driver.find_elements_by_css_selector("div.HomeCardContainer")
            if len(ads) == 0:
                output_filename = f"output/failures/{datetime.now()}.png"
                driver.save_screenshot(output_filename)
                self.logger.error("No ads found: %s", output_filename)
                return
            ads = ads[:self.num_ads]
            ads = [self.transform_ad(ad) for ad in ads]
            self.log_scraped_ranking(queue, unit, self, ads)
        except NoSuchElementException:
            self.logger.exception("Unexpected exception")
