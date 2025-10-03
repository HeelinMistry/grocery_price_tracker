import asyncio
import os
from datetime import datetime
import pandas as pd
from playwright.async_api import async_playwright

from scraper.foodline_scraper import FoodlineScraper
from scraper.makro_scraper import MakroScraper
from scraper.pnp_scraper import PnPScraper

async def retry_fetch_and_parse(scraper, page, context, semaphore, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            df = await scraper.fetch_and_parse(page, context, semaphore)
            if df.empty:
                print(f"No products found on page {page}. Ending scraping.")
                return df  # or signal to stop scraping
            return df
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

def save_dataframes(store_dfs: dict[str, pd.DataFrame]):
    today = datetime.today().strftime("%Y-%m-%d")

    os.makedirs("data", exist_ok=True)
    os.makedirs("docs/data", exist_ok=True)

    combined_df = pd.DataFrame()

    for store, df in store_dfs.items():
        if df.empty:
            print(f"⚠️ No data to save for {store}")
            continue

        filename = f"{store.lower()}_products_{today}.csv"
        file_path = os.path.join("data", filename)
        df.to_csv(file_path, index=False)

        print(f"✅ Saved {store} data to {file_path}")
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    # Save combined latest.json
    latest_path = os.path.join("docs/data", "latest.json")
    combined_df.to_json(latest_path, orient="records", indent=2, index=False)
    print(f"✅ Saved combined data to {latest_path}")


def main():
    scrapers = [PnPScraper(), MakroScraper()]
    store_dfs = {}
    for scraper in scrapers:
        store_name = scraper.__class__.__name__.replace("Scraper", "")
        print(f"🔍 Running scraper for: {store_name}")
        df = asyncio.run(run_scraper_concurrently(scraper))
        store_dfs[store_name] = df
    save_dataframes(store_dfs)

if __name__ == "__main__":
    main()
