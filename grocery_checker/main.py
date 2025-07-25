import pandas as pd

from scraper.pnp_scraper import PnPScraper


def main():
    scraper = PnPScraper()
    html = scraper.fetch()
    total_pages = scraper.get_total_pages(html)
    all_data = pd.DataFrame()
    for page in range(total_pages):
        print(page)
        if page != 0:
            html = scraper.fetch(page)
        page_data = scraper.parse(html)
        all_data = pd.concat([all_data, page_data], ignore_index=True)

        # Save to CSV
        all_data.to_csv("data/products.csv", index=False)

    print("Scraping completed and saved to products.csv")

if __name__ == "__main__":
    main()

