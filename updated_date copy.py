from pymongo import MongoClient
import requests
from datetime import datetime
import cloudscraper
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import timedelta
from modules.helper import ChangeMonth, cek_date
import json, re
# Koneksi MongoDB
client = MongoClient("mongodb://onlinenews_datalake:Kabayan2020@15.235.164.126:3002/?authSource=onlinenews_datalake&directConnection=true")
db = client["onlinenews_datalake"]
collection = db["streams"]

pipeline = [
    {
        "$match": {
            "date": None   
        }
    },
    {
        "$group": {
            "_id": "$portal",
            "count": { "$sum": 1 },
            "urls": { "$push": "$url" },
            "ids": { "$push": "$_id" }
        }
    },
    {
        "$sort": { "count": -1 }
    }
]

result = collection.aggregate(pipeline)

for portal in result:
    print(f"Portal: {portal['_id']}, Count: {portal['count']}")
    for url, doc_id in zip(portal["urls"], portal["ids"]):
        print(f"URL: {url}")
        # Request ulang & update
        try:
            scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
            response = scraper.get(url)
        except requests.exceptions.ConnectionError:
            print("Error : Gagal mengambil berita karena website down")
            continue
        if response.status_code != 200:
            print("Error : Gagal mengambil berita karena website berstatus", str(response.status_code))
            continue
        page = BeautifulSoup(response.text, 'html.parser')
        if portal['_id'] == 'Pelitakarawang':
            date = page.find('div', class_='post_info').time['datetime']
        elif portal['_id'] == 'kabarontime':
            date = page.find('meta', attrs={"name":"content_PublishedDate"})['content']
        elif portal['_id'] == 'lenterajabar':
            date = page.find('span', class_='date-header-item').text.strip()
            date = date.partition(',')[2].replace(',', '').replace('|', '')
            date = date.partition('W')[0]
            date = ChangeMonth(date)
        elif portal['_id'] == 'KanalIndonesia':
            date = page.find('div', class_="text-muted mb-3").text.strip()
            date = date.split('•')[1].strip()
            date = date.split('•')[0].strip()
            date = ChangeMonth(date)
        elif portal['_id'] == 'tarungnews':
            date = page.find("ul", class_="post-tags").find('li').text.strip()
            now = datetime.now()
            if "jam" in date:
                hours = int(date.split()[0])
                date = now - timedelta(hours=hours)
                date = str(date)
            elif "menit" in date:
                minutes = int(date.split()[0])
                date = now - timedelta(minutes=minutes)
                date = str(date)
            elif "hari" in date:
                days = int(date.split()[0])
                date = now - timedelta(days=days)
                date = str(date)
            else:
                date = date.split(",", 1)[1].strip().replace(" |", "").replace("WIB", "")
                date = ChangeMonth(date)
        elif portal['_id'] == 'wartakini.co.id':
            date = page.find('div', class_='author-description').p.text
            date = date.partition(",")[2]
            date = ChangeMonth(date)
            date = date.strip()
        date = parser.parse(date).replace(tzinfo=None)
        if response.status_code == 200:
            collection.update_one(
                {"_id": doc_id},
                {
                    "$set": {
                        "date": date,
                        "updated_at": datetime.now()
                    }
                }
            )
