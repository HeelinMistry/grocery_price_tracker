import os
import re
from urllib.parse import urlparse, unquote

import pandas as pd
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from scraper.base_scraper import BaseScraper


def extract_info_details(region, url):
    filename = unquote(urlparse(url).path.split('/')[-1])  # Get last part and decode + chars
    pattern = r'_(\d{2})(\d{2})(\d{4})_(\d{2})(\d{2})(\d{4})_(.+)\.pdf$'

    match = re.search(pattern, filename)
    if not match:
        return None

    start_date = f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
    end_date = f"{match.group(6)}-{match.group(5)}-{match.group(4)}"
    title = match.group(7).replace('+', ' ')

    return {
        "store": "PicknPay",
        "region": region,
        "start_date": start_date,
        "end_date": end_date,
        "title": title,
        "url": url
    }


class PnPScraper(BaseScraper):
    BASE_URL = "https://www.pnp.co.za/catalogues"
    SAVE_DIR = "data/pnp_catalogues"

    def fetch(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.BASE_URL)
            page.wait_for_selector("div.pdfdownload", timeout=10000)
            page.wait_for_timeout(5000)  # wait 5s for JS to load
            content = page.content()

        return content

    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")

        # print(soup.prettify())
        # Find ALL divs with class "pdfdownload"
        pdf_sections = soup.find_all("div", class_="pdfdownload")

        pdf_links = []

        for section in pdf_sections:
            # Find all <a> tags with an href ending in .pdf
            buttons = section.find_all("a", href=True)
            for button in buttons:
                href = button['href']
                if href.endswith(".pdf"):
                    region = button.get_text(strip=True)
                    pdf_links.append((region, href))

        return pdf_links

    def extract_info(self, pdfs):
        data = []
        for region, url in pdfs:
            info = extract_info_details(region, url)
            if info:
                data.append(info)
        return pd.DataFrame(data)

    def save(self, data):
        os.makedirs(self.SAVE_DIR, exist_ok=True)
        for item in data:
            filename = os.path.join(self.SAVE_DIR, item["title"].replace(" ", "_") + ".pdf")
            if not os.path.exists(filename):
                print(f"Downloading {item['url']} to {filename}")
                response = requests.get(item["url"])
                with open(filename, "wb") as f:
                    f.write(response.content)
