import re
import pandas as pd
from bs4 import BeautifulSoup

from scraper.base_scraper import BaseScraper


class MakroScraper(BaseScraper):
    BASE_URL = "https://www.makro.co.za/food-products/pr?sid=eat"
    total_pages = 1

    async def fetch_and_parse(self, page, context, semaphore):
        async with semaphore:
            print(page)
            page_url = f"{self.BASE_URL}&page={page}"
            page_obj = await context.new_page()
            try:
                await page_obj.goto(page_url, timeout=10000)
                await page_obj.wait_for_selector("div._1kfTjk", timeout=10000)
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
            await page_obj.wait_for_selector("div._2MImiq", timeout=10000)
            html = await page_obj.content()
            soup = BeautifulSoup(html, "html.parser")
            page_info_span = soup.find("span", string=re.compile(r"Page\s+\d+\s+of\s+\d+", re.I))

            # Extract the total number using regex
            total_pages = None
            if page_info_span:
                match = re.search(r"Page\s+\d+\s+of\s+(\d+)", page_info_span.text)
                if match:
                    total_pages = int(match.group(1))
            return total_pages
        except Exception as e:
            print(f"[Error getting total pages] {e}")
            return 1
        finally:
            await page_obj.close()

    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")
        # print(soup.prettify())
        items = soup.find_all("div", class_="_4ddWXP")
        return self.extract_info(items)

    def extract_info(self, items):
        products = []
        if items:
            for item in items:
                a_tag = item.select_one('a.s1Q9rs')
                product_name = a_tag['title'] if a_tag and a_tag.has_attr('title') else None

                # Extract pack size from <div> tag
                pack_div = item.select_one('div._3Djpdu')
                pack_size = pack_div.get_text(strip=True) if pack_div else ""

                # Append the pack size to the product name
                name = f"{product_name} ({pack_size})" if product_name else None

                # Extract price parts
                price_rands = item.select_one('span._8TW4TR')
                price_cents = item.select_one('span._1rSsFO')

                # Parse and format
                if price_rands and price_cents:
                    price_rands_text = price_rands.get_text(strip=True).replace("R", "").replace(",", "").strip()
                    price_cents_text = price_cents.get_text(strip=True).strip()
                    price = f"{price_rands_text}.{price_cents_text}"
                else:
                    price = None

                old_price = None
                promotion = None

                if name and price:
                    products.append({
                        "store": "Makro",
                        "name": name.strip(),
                        "price": float(price),
                        "old_price": old_price,  # Will be None if not discounted
                        "promotion": promotion  # None if no promotion
                    })
        return pd.DataFrame(products)