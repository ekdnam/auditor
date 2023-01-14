import logging
import time
from datetime import datetime
from queue import Queue
from threading import Semaphore
import uuid
import codecs
import os

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

# from Screenshot import Screenshot_Clipping

from auditor.agent import Agent
from auditor.scrapers.advertisement.base_ad_scrapers import BaseAdScraper
from auditor.scrapers.base_scraper import strip_html_tags

INPUT_SELECTOR = "input[title='Search']"


class GoogleSearchAdScraper(BaseAdScraper):
    logger = logging.getLogger(__name__)
    scrape_lock = Semaphore(2)

    def __init__(self, query: str, delay: int, pages: int = 3):
        super().__init__(query, delay, pages)
        self.name = 'GoogleSearchAdScraper'

    def __call__(self, unit: Agent, queue: Queue):
        def save_screenshot(driver, path: str = '/tmp/screenshot.png') -> None:
            # Ref: https://stackoverflow.com/a/52572919/
            original_size = driver.get_window_size()
            required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
            required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
            driver.set_window_size(required_width, required_height)
            # driver.save_screenshot(path)  # has scrollbar
            driver.find_element_by_tag_name('body').screenshot(path)  # avoids scrollbar
            driver.set_window_size(original_size['width'], original_size['height'])

        def save_file(driver, folder, filename):
            # Ref: https://www.tutorialspoint.com/save-a-web-page-with-python-selenium
            save_path = f'{os.getcwd()}/{folder}'
            if not os.path.exists(save_path):
                os.mkdir(os.path.join(os.getcwd(), folder))
            n = os.path.join(save_path,filename + '.html')
            f = codecs.open(n, "w", "utf−8")
            h = driver.page_source
            f.write(h)

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
            i = 0
            for page in range(self.pages):
                time.sleep(self.delay)
                if "https://www.google.com/sorry/index" in driver.current_url:
                    self.logger.error("Hit anti-bot captcha on page %i", page)
                    return
                # ss = Screenshot_Clipping.Screenshot()
                # image = ss.full_Screenshot(driver, save_path=r'.' , image_name=f'{i}.png')


                # query file names to build data structure
                # ref: https://stackoverflow.com/questions/10607688/how-to-create-a-file-name-with-the-current-date-time-in-python
                # https://stackoverflow.com/questions/10501247/best-way-to-generate-random-file-names-in-python 
                time_stamp = time.strftime("%Y%m%d-%H%M%S")
                query_ID = str(uuid.uuid4())
                agent_ID = unit.agent_id + "___" +unit.treatment_id
                file_name = agent_ID + "___" + time_stamp + "___" + query_ID
                # self.logger.info(unit.agent_id)
                # self.logger.info(unit.treatment_id)
                self.logger.info('Save file')
                save_file(driver, 'output-html', file_name)
                i += 1
                ads = driver.find_elements_by_css_selector("li.ads-ad")
                # for ad in ads:
                #     try:
                #         title = ad.find_element_by_css_selector('div.ad_cclk a:not([style*="display:none"])').text
                #         body = strip_html_tags(str(ad.find_element_by_css_selector("div.ads-creative")
                #                                    .get_attribute('innerHTML')))
                #         parsed_ad = dict()
                #         parsed_ad['query'] = self.query
                #         parsed_ad['title'] = strip_html_tags(title)
                #         parsed_ad['url'] = ad.find_element_by_css_selector("div.ads-visurl cite").text
                #         parsed_ad['body'] = strip_html_tags(body)
                #         self.log_scraped_ad(queue, unit, self, parsed_ad)
                #         self.logger.debug("Complete ad: %s", ad.get_attribute('outerHTML'))
                #         driver.save_screenshot('ss.png')
                #     except NoSuchElementException:
                #         self.logger.exception("Unparseable ad: %s", ad.get_attribute('outerHTML'))
                # try:
                #     driver.execute_script("arguments[0].scrollIntoView();",
                #                           driver.find_element_by_css_selector("#pnnext"))
                #     driver.find_element_by_css_selector("#pnnext").click()
                # except NoSuchElementException:
                #     filename = str(datetime.now()) + '.screenie.png'
                #     driver.save_screenshot(filename)
                #     self.logger.exception("Element not found: %s", filename)
