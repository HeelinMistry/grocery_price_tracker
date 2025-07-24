from abc import ABC, abstractmethod

class BaseScraper(ABC):
    @abstractmethod
    def fetch(self):
        pass

    @abstractmethod
    def parse(self, html):
        pass

    @abstractmethod
    def extract_info(self, pdf_links):
        pass

    @abstractmethod
    def save(self, data):
        pass
