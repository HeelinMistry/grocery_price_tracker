import asyncio

import pandas as pd
from playwright.async_api import async_playwright

from scraper.pnp_scraper import PnPScraper

async def run_scraper_concurrently(scraper, max_concurrency=10):
    all_results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        try:
            total_pages = await scraper.get_total_pages(context)
            # total_pages = 10
            print(f"Total pages found: {total_pages}")

            semaphore = asyncio.Semaphore(max_concurrency)

            tasks = [
                scraper.fetch_and_parse(page, context, semaphore)
                for page in range(total_pages)
            ]
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            await context.close()
            await browser.close()

    # Handle potential exceptions in results
    clean_results = []
    for r in all_results:
        if isinstance(r, Exception):
            print("Skipped a failed page.")
        else:
            clean_results.append(r)

    combined_df = pd.concat(
        [df for df in clean_results if not df.empty], ignore_index=True
    )
    return combined_df

def main():
    scraper = PnPScraper()
    df = asyncio.run(run_scraper_concurrently(scraper))
    df.to_csv("data/pnp_products.csv", index=False)
    print("Scraping completed and saved to pnp_products.csv")
    print(df.head())
#
# def main():
#     scraper = PnPScraper()
#     html = scraper.fetch()
#     total_pages = scraper.get_total_pages(html)
#     all_data = pd.DataFrame()
#     for page in range(total_pages):
#         print(page)
#         if page != 0:
#             html = scraper.fetch(page)
#         page_data = scraper.parse(html)
#         all_data = pd.concat([all_data, page_data], ignore_index=True)
#
#         # Save to CSV
#         all_data.to_csv("data/products.csv", index=False)
#
#     print("Scraping completed and saved to products.csv")

if __name__ == "__main__":
    main()

