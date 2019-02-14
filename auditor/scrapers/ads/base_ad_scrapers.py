import io
import os
from abc import ABC
from datetime import datetime

import imagehash
from PIL import Image
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from auditor.agent import Agent
from auditor.scrapers.base_scraper import ScrapingStep


class BaseAdScraper(ScrapingStep, ABC):

    def __init__(self, query: str, delay: int, pages: int):
        super().__init__(query, delay)
        self.pages = pages

    @staticmethod
    def screenshot_elem(driver: WebDriver, elem: WebElement):
        driver.execute_script("arguments[0].scrollIntoView();", elem)
        location = elem.location_once_scrolled_into_view
        size = elem.size
        screen = Image.open(io.BytesIO(driver.get_screenshot_as_png()))
        cropped = screen.crop((location['x'], location['y'], location['x'] + size['width'], location['y'] + size['height']))
        cropped.load()
        ad_hash = imagehash.phash(cropped, 8)
        ad_filename = f"output/{ad_hash}.png"
        if not os.path.isfile(ad_filename):
            cropped.save(ad_filename, format="PNG")
            ScrapingStep.logger.info("Scraped new image: %s", ad_filename)
        return ad_filename

    @staticmethod
    def log_scraped_ad(queue, agent: Agent, scraper, ad):
        # TODO: Add query to logged data
        queue.put({
            'time': datetime.now(),
            'type': 'ad',
            'scraper': type(scraper).__name__,
            'treatment': agent.treatment,
            'treatment_id': agent.treatment_id,
            'url': agent.driver.current_url,
            'agent_id': agent.agent_id,
            'block_id': agent.block_id,
            'ad': ad,
        })
