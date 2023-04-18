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

INPUT_SELECTOR = "input[type='submit']"

import requests

def connected_to_internet(url='http://www.google.com/', timeout=5):
    try:
        _ = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("No internet connection available.")
    return False

class GoogleSearchAdScraper(BaseAdScraper):
    logger = logging.getLogger(__name__)
    scrape_lock = Semaphore(2)

    def __init__(self, query: str, delay: int, pages: int = 1):
        super().__init__(query, delay, pages)
        self.name = 'GoogleSearchAdScraper'

    def __call__(self, unit: Agent, queue: Queue):
        def save_file(unit, driver, folder, filename):
            # Ref: https://www.tutorialspoint.com/save-a-web-page-with-python-selenium
            self.logger.info("Saving file ---  ", unit.treatment_id)
            save_path = f'{os.getcwd()}/{folder}'
            if not os.path.exists(save_path):
                os.mkdir(os.path.join(os.getcwd(), folder))
            n = os.path.join(save_path,filename + '.html')
            f = codecs.open(n, "w", "utf−8")
            h = driver.page_source
            f.write(h)

        # with GoogleSearchAdScraper.scrape_lock:
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
        except Exception as e:
            self.logger.info("Exception occurred while searching on google for results")
            self.logger.exception(e)
        i = 0
        for page in range(self.pages):
            time.sleep(self.delay)
            if "https://www.google.com/sorry/index" in driver.current_url:
                self.logger.error("Hit anti-bot captcha on page %i", page)
                return
            # query file names to build data structure
            # ref: https://stackoverflow.com/questions/10607688/how-to-create-a-file-name-with-the-current-date-time-in-python
            # https://stackoverflow.com/questions/10501247/best-way-to-generate-random-file-names-in-python 
            time_stamp = time.strftime("%Y%m%d-%H%M%S")
            query_ID = str(uuid.uuid4())
            agent_ID = str(unit.agent_id) + "___" + str(unit.treatment_id)
            file_name = agent_ID + "___" + time_stamp + "___" + query_ID
            self.logger.info('Save file')
            save_file(unit, driver, 'output-html', file_name)
            i += 1
