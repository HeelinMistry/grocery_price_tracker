import pandas as pd
from bs4 import BeautifulSoup

from scraper.base_scraper import BaseScraper


class PnPScraper(BaseScraper):
    BASE_URL = "https://www.pnp.co.za/c/pnpbase"
    total_pages = 1

    async def fetch_and_parse(self, page, context, semaphore):
        async with semaphore:
            print(page)
            page_url = f"{self.BASE_URL}?currentPage={page}"
            page_obj = await context.new_page()
            try:
                await page_obj.goto(page_url, timeout=10000)
                await page_obj.wait_for_selector("div.product-grid-item__info-container", timeout=10000)
                html = await page_obj.content()
                return self.parse(html)
            except TimeoutError:
                print(f"[Timeout] Page {page} skipped")
                return pd.DataFrame()
            finally:
                await page_obj.close()

    async def get_total_pages(self, context):
        page_obj = await context.new_page()
        try:
            await page_obj.goto(self.BASE_URL, timeout=15000)
            await page_obj.wait_for_selector("div.cx-pagination", timeout=10000)
            html = await page_obj.content()
            soup = BeautifulSoup(html, "html.parser")
            # Try finding the last pagination number button
            last_page = soup.select_one("a.last")
            if last_page and "currentPage=" in last_page["href"]:
                return int(last_page["href"].split("currentPage=")[1]) + 1
            return 1
        except Exception as e:
            print(f"[Error getting total pages] {e}")
            return 1
        finally:
            await page_obj.close()

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