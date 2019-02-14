from abc import ABC
from enum import Enum
from datetime import datetime

from auditor.scrapers.base_scraper import ScrapingStep, strip_html_tags


class BaseRankingScraper(ScrapingStep, ABC):
    class ScrapeType(Enum):
        BUY = 1
        RENT = 2

    def __init__(self, query: str, delay: int = 60, num_ads: int = 10, category: ScrapeType = ScrapeType.BUY):
        super().__init__(query, delay)
        self.num_ads = num_ads
        self.category = category

    @staticmethod
    def log_scraped_ranking(queue, agent, scraper: ScrapingStep, ranking):
        queue.put({
            'time': datetime.now(),
            'type': 'ranking',
            'scraper': type(scraper).__name__,
            'query': scraper.query,
            'treatment': agent.treatment,
            'treatment_id': agent.treatment_id,
            'url': agent.driver.current_url,
            'agent_id': agent.agent_id,
            'block_id': agent.block_id,
            'ranking': ranking,
        })

    @staticmethod
    def extract_address(ad, details):
        details["street address"] = strip_html_tags(ad.find_element_by_css_selector(
                    "span[itemprop='address'] span[itemprop='streetAddress']").get_attribute('innerHTML'))
        details["locality"] = strip_html_tags(ad.find_element_by_css_selector(
                    "span[itemprop='address'] span[itemprop='addressLocality']").get_attribute('innerHTML'))
        details["region"] = strip_html_tags(ad.find_element_by_css_selector(
                    "span[itemprop='address'] span[itemprop='addressRegion']").get_attribute('innerHTML'))
        details["postal code"] = strip_html_tags(ad.find_element_by_css_selector(
                    "span[itemprop='address'] span[itemprop='postalCode']").get_attribute('innerHTML'))
        return details

    @staticmethod
    def extract_geo(ad, details):
        details["latitude"] = strip_html_tags(ad.find_element_by_css_selector(
            "span[itemprop='geo'] meta[itemprop='latitude']").get_attribute('content'))
        details["longitude"] = strip_html_tags(ad.find_element_by_css_selector(
            "span[itemprop='geo'] meta[itemprop='longitude']").get_attribute('content'))
        return details
