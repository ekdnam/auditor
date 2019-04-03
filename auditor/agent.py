import logging
import uuid
from datetime import datetime
from typing import List

from selenium import webdriver
from selenium.webdriver import Proxy
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.firefox.webdriver import WebDriver

from auditor.ad_writer import AdWriter
from auditor.scrapers.base_scraper import ScrapingStep
from auditor.trainers.base_trainer import TrainingStep


class Agent(object):
    """
    A single agent that maps directly to a running browser
    """
    logger = logging.getLogger(__name__)

    def __init__(self, treatment_id, block_id=1, headless=False, proxy=None):
        """

        :param treatment_id:
        :param headless:
        :param proxy:
        """
        self.agent_id = uuid.uuid4()
        self.treatment_id = treatment_id
        self.block_id = block_id
        self.__treatment = {}
        self.__training_steps = list()
        self.__scrape_steps = list()

        if proxy is None:
            self.proxy = Proxy({
                'proxyType': ProxyType.DIRECT,
            })
        else:
            self.proxy = proxy

        options = FirefoxOptions()
        options.log.level = 'error'
        options.headless = headless

        self.driver: WebDriver = webdriver.Firefox(firefox_options=options, proxy=self.proxy)
        self.driver.set_page_load_timeout(60)

    @property
    def driver(self) -> WebDriver:
        return self.__driver

    @driver.setter
    def driver(self, val):
        self.__driver = val

    @property
    def training_steps(self) -> List[TrainingStep]:
        return self.__training_steps

    @property
    def scrape_steps(self) -> List[ScrapingStep]:
        return self.__scrape_steps

    @property
    def treatment(self):
        return self.__treatment

    def add_treatment(self, name, val):
        self.__treatment[name] = val

    def record_ip_addr(self, queue: AdWriter):
        driver: WebDriver = self.driver
        driver.get("https://whatismyipaddress.com/")
        ipv6_addr = driver.find_element_by_css_selector("div#ipv6 a").text
        ipv4_addr = driver.find_element_by_css_selector("div#ipv4 a").text
        queue.queue.put({
            'time': datetime.now(),
            'type': 'meta',
            'treatment': self.treatment,
            'treatment_id': self.treatment_id,
            'agent_id': self.agent_id,
            'block_id': self.block_id,
            'ipv4': ipv4_addr,
            'ipv6': ipv6_addr,
        })

    def run(self, queue: AdWriter):
        """

        :param queue:
        :return: None
        """
        self.logger.info("Started training steps")
        for step in self.training_steps:
            step(self)

        self.logger.info("Started scraping")
        for step in self.scrape_steps:
            step(self, queue)

    def quit(self):
        self.driver.quit()
