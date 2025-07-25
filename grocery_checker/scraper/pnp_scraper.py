import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from scraper.base_scraper import BaseScraper


class PnPScraper(BaseScraper):
    BASE_URL = "https://www.pnp.co.za/c/pnpbase"
    total_pages = 1

    def fetch(self, page_index=0):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            url = f"{self.BASE_URL}?currentPage={page_index}"
            page.goto(url, timeout=10000)
            page.wait_for_selector("div.product-grid-item__info-container", timeout=10000)
            page.wait_for_timeout(10000)  # wait 5s for JS to load
            content = page.content()
        return content

    def get_total_pages(self, html):
        soup = BeautifulSoup(html, "html.parser")
        last_page = soup.select_one("a.last")
        if last_page and "currentPage=" in last_page["href"]:
            return int(last_page["href"].split("currentPage=")[1]) + 1
        return 1

    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")
        # print(soup.prettify())
        items = soup.find_all("div", class_="product-grid-item list-mobile ng-star-inserted")
        return self.extract_info(items)

    def extract_info(self, items):
        products = []
        for item in items:
            name = item.get("data-cnstrc-item-name")
            price = item.get("data-cnstrc-item-price")

            old_price_elem = item.select_one(".product-grid-item__price-container .old")
            old_price = None

            if old_price_elem:
                try:
                    # Remove any currency symbols or spaces and convert to float
                    old_price = float(old_price_elem.get_text(strip=True).replace("R", "").replace(",", ""))
                except ValueError:
                    pass  # Fallback to None if conversion fails

            # Extract promotion (if available)
            promotion_elem = item.select_one(".product-grid-item__promotion-container a")
            promotion = promotion_elem.get_text(strip=True) if promotion_elem else None

            if name and price:
                products.append({
                    "store": "Pick n Pay",
                    "name": name.strip(),
                    "price": float(price),
                    "old_price": old_price,  # Will be None if not discounted
                    "promotion": promotion  # None if no promotion
                })
        # Example output
        # data = []
        # for p in products:
        #     data.append(p)
        return pd.DataFrame(products)