import logging
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from auditor.trainers.base_trainer import TrainingStep

BASE_URL = "https://www.google.com/"
INPUT_SELECTOR = "input[title='Search']"
RESULT_SELECTOR = "div.g div.rc h3.r a"


class GoogleSearcher(TrainingStep):
    logger = logging.getLogger(__name__)

    def __init__(self, query_list, delay: int = 20, clickcount=5):
        super().__init__(delay)
        self.query_list = query_list
        self.clickcount = clickcount

    def __call__(self, unit):
        for query in self.query_list:
            try:
                unit.driver.get(BASE_URL)
                search_bar = unit.driver.find_element_by_css_selector(INPUT_SELECTOR)
                ActionChains(unit.driver) \
                    .pause(1) \
                    .send_keys_to_element(search_bar, query) \
                    .send_keys_to_element(search_bar, Keys.RETURN) \
                    .perform()
                search_bar.submit()
            except NoSuchElementException:
                self.logger.exception("Unexpected exception")
                return

            for click in range(self.clickcount):
                try:
                    time.sleep(self.delay)
                    results = unit.driver.find_elements_by_css_selector(RESULT_SELECTOR)
                    if click >= len(results):
                        break
                    ActionChains(unit.driver) \
                        .click(results[click]) \
                        .pause(3) \
                        .perform()
                    self.logger.info("Visited site: %s", unit.driver.current_url)
                    unit.driver.back()
                except NoSuchElementException:
                    self.logger.exception("Unexpected exception")
