from scraper.pnp_scraper import PnPScraper

def main():
    scraper = PnPScraper()
    html = scraper.fetch()
    links = scraper.parse(html)
    catalogue_data = scraper.extract_info(links)
    print(catalogue_data.head())
    # scraper.save(links)

if __name__ == "__main__":
    main()

