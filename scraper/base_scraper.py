from abc import ABC, abstractmethod

class BaseScraper(ABC):

    @abstractmethod
    def parse(self, html):
        pass

    @abstractmethod
    def extract_info(self, items):
        pass

    @abstractmethod
    def get_total_pages(self, html):
        pass
