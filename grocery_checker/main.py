import asyncio
import os
from datetime import datetime
import pandas as pd
from playwright.async_api import async_playwright
from scraper.pnp_scraper import PnPScraper

async def retry_fetch_and_parse(scraper, page, context, semaphore, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            return await scraper.fetch_and_parse(page, context, semaphore)
        except Exception as e:
            print(f"Error on page {page}, attempt {attempt}: {e}")
            if attempt == max_retries:
                print(f"Page {page} failed after {max_retries} attempts.")
                return pd.DataFrame()  # or None if you prefer
            await asyncio.sleep(2 * attempt)  # exponential backoff
    return pd.DataFrame()


async def run_scraper_concurrently(scraper, headless = True, max_concurrency=5):
    all_results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        try:
            total_pages = await scraper.get_total_pages(context)
            print(f"Total pages found: {total_pages}")

            semaphore = asyncio.Semaphore(max_concurrency)

            tasks = [
                retry_fetch_and_parse(scraper, page, context, semaphore, max_retries=3)
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

def save_dataframe(df):
    os.makedirs("data", exist_ok=True)
    # Get current date
    today = datetime.today()
    date_str = today.strftime("%Y-%m-%d")
    # Construct filename
    filename = f"data/pnp_products_{date_str}.json"

    # Save DataFrame
    df.to_json(filename, orient="records", indent=2, index=False)
    # df.to_csv("data/pnp_products.json", index=False)

    print(f"Scraping completed and saved to data/pnp_products_{date_str}.json")

def main():
    scraper = PnPScraper()
    df = asyncio.run(run_scraper_concurrently(scraper))
    save_dataframe(df)

if __name__ == "__main__":
    main()

