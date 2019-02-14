import logging

from selenium.common.exceptions import NoSuchElementException

from auditor.scrapers.ads.base_ad_scrapers import BaseAdScraper
from auditor.scrapers.base_scraper import strip_html_tags


class BBCAdScraper(BaseAdScraper):
    logger = logging.getLogger(__name__)

    def __init__(self, delay: int = 60, pages: int = 1):
        super().__init__('', delay, pages)

    def __call__(self, unit, queue):
        driver = unit.driver
        for rep in range(self.pages):
            try:
                driver.get("https://www.bbc.com/news/world")
                iframes = driver.find_elements_by_css_selector("div.bbccom_adsense_slot iframe")
            except:
                self.logger.exception("Could not get main page and ads")
                return
            for slot in iframes:
                try:
                    driver.switch_to.frame(slot)
                    frame = driver.find_element_by_css_selector('iframe[id^="google_ads_frame"]')
                    driver.switch_to.frame(frame)
                    ads = driver.find_elements_by_css_selector("div.ads div.ad")
                    for ad in ads:
                        try:
                            parsed_ad = dict()
                            parsed_ad['title'] = strip_html_tags(ad.find_element_by_css_selector("div.title").text)
                            parsed_ad['url'] = strip_html_tags(ad.find_element_by_css_selector("a.body-link").text)
                            parsed_ad['body'] = strip_html_tags(ad.find_element_by_css_selector("a.url-link").text)
                            self.log_scraped_ad(queue, unit, self, parsed_ad)
                            self.logger.debug("Complete ad: %s", ad.get_attribute('outerHTML'))
                        except NoSuchElementException:
                            self.logger.exception("Could not scrape ad: %s", ad.get_attribute('outerHTML'))
                    driver.switch_to.default_content()
                except:
                    self.logger.exception("Could not extract ad")
