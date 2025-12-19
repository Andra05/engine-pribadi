import json
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}
url = f"https://www.pikiran-rakyat.com/komunitas/pr-019533896/stop-fomo-tips-menghindari-tren-fast-beauty"
print(f"Mengakses: {url}")
scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
response = scraper.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
with open('result.html', 'w', encoding="utf-8") as f:
    f.writelines(str(soup))
    exit()