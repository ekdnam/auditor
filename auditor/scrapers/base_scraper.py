import logging
import re
from abc import ABC, abstractmethod
from queue import Queue


def strip_html_tags(ad: str):
    return ScrapingStep.cleaner_regex.sub('', ad)


class ScrapingStep(ABC):
    logger = logging.getLogger(__name__)
    cleaner_regex = re.compile('<.*?>')

    @abstractmethod
    def __init__(self, query: str, delay: int):
        self.query = query
        self.delay = delay

    @abstractmethod
    def __call__(self, unit, queue: Queue):
        pass

    @staticmethod
    def log_anti_bot():
        # TODO: Log whenever we hit anti-bot
        pass

