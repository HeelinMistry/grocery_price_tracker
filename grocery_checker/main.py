from scraper.pnp_scraper import PnPScraper

def main():
    scraper = PnPScraper()
    html = scraper.fetch()
    links = scraper.parse(html)
    scraper.extract_info(links)
    # scraper.save(links)

if __name__ == "__main__":
    main()

