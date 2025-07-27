import pandas as pd
from bs4 import BeautifulSoup

from scraper.base_scraper import BaseScraper


class FoodlineScraper(BaseScraper):
    BASE_URL = "https://foodline.co.za/shop-3"
    total_pages = 1

    async def fetch_and_parse(self, page, context, semaphore):
        async with semaphore:
            page_url = f"{self.BASE_URL}/page/{page}/"
            print(f"{page}")
            page_obj = await context.new_page()
            try:
                await page_obj.goto(page_url, timeout=10000)
                await page_obj.wait_for_selector("ul.products", timeout=10000)
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
            await page_obj.wait_for_selector("nav.woocommerce-pagination", timeout=10000)
            html = await page_obj.content()
            soup = BeautifulSoup(html, "html.parser")

            # Select all numbered pagination links
            page_links = soup.select("nav.woocommerce-pagination ul.page-numbers a.page-numbers")

            # Extract numeric values from href or text
            page_numbers = []
            for link in page_links:
                href = link.get("href", "")
                text = link.get_text(strip=True)
                try:
                    # Prefer aria-label for consistency
                    page_num = int(link.get("aria-label", text).replace("Page ", ""))
                    page_numbers.append(page_num)
                except ValueError:
                    continue
            return max(page_numbers) if page_numbers else 1
        except Exception as e:
            print(f"[Error getting total pages] {e}")
            return 1
        finally:
            await page_obj.close()

    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")
        # print(soup.prettify())
        try:
            items = soup.select("ul.products > li.product")
            return self.extract_info(items)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e


    def extract_info(self, items):
        products = []
        for item in items:
            name_tag = item.select_one("h2.woocommerce-loop-product__title")
            old_price_tag = item.select_one("del .amount")
            price_tag = item.select_one("ins .amount") or item.select_one("span.price .amount")

            if name_tag and price_tag:
                # Extract and clean text
                name = name_tag.get_text(strip=True)
                price_text = price_tag.get_text(strip=True).replace("R", "").replace(",", "")

                try:
                    price = float(price_text)
                except ValueError:
                    continue  # skip this item if price can't be converted

                if old_price_tag:
                    old_price_text = old_price_tag.get_text(strip=True).replace("R", "").replace(",", "")
                    try:
                        old_price = float(old_price_text)
                    except ValueError:
                        old_price = None
                else:
                    old_price = None

                products.append({
                    "store": "Foodline",
                    "name": name,
                    "price": price,
                    "old_price": old_price,
                    "promotion": None  # Placeholder if you want to add logic
                })

        return pd.DataFrame(products)
