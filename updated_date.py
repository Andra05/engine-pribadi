from pymongo import MongoClient, UpdateOne
from datetime import datetime, timezone
import cloudscraper
import re
import time
from bs4 import BeautifulSoup

# === Koneksi MongoDB ===
client_get = MongoClient("mongodb://onlinenews_datalake:Kabayan2020@15.235.164.126:3002/?authSource=onlinenews_datalake&directConnection=true")
client_update = MongoClient("mongodb://onlinenews_datalake:Kabayan2020@15.235.164.126:3001/?authSource=onlinenews_datalake&directConnection=true")

db_get = client_get["onlinenews_datalake"]
db_update = client_update["onlinenews_datalake"]

collection_get = db_get["streams"]       # hanya untuk baca
collection_update = db_update["streams"] # hanya untuk update

def extract_journalist(page, url):
    date = page.find('time', attrs={'class':'entry-date published'})['datetime']
    date = parser.parse(date).replace(tzinfo=None)
    date = date - timedelta(hours=1)

    return journalist

pipeline = [
    {
        '$match': {
            'portal': 'AntaraKeyword', 
            'journalist': None, 
            'updated_at': {
                '$gte': datetime(2025, 9, 18, 0, 0, 0, tzinfo=timezone.utc), 
                '$lt': datetime(2025, 9, 19, 0, 0, 0, tzinfo=timezone.utc)
            }
        }
    }, {
        '$project': {
            'url': 1, 
            '_id': 1, 
            'journalist': 1, 
            'updated_at': 1
        }
    }
]

docs = list(collection_get.aggregate(pipeline))

bulk_ops = []
BATCH_SIZE = 50
updated_total = 0

for doc in docs:
    _id = doc["_id"]
    url = doc.get("url")
    updated_at = doc.get("updated_at")
    print(f"Processing {_id} ({url})")
    if not url:
        continue

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }
        if '/video/' in url:
            print("Skip, video")
            continue
        time.sleep(2)
        
        scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
        article_detail = scraper.get(url, headers=headers)
        if article_detail.status_code != 200:
            print(f"[SKIP] {url} status: {article_detail.status_code}")
            continue

        page = BeautifulSoup(article_detail.text, "html.parser")

        journalist = extract_journalist(page, url)

        # === masukkan ke bulk_ops jika ada journalist ===
        if journalist:
            bulk_ops.append(
                UpdateOne(
                    {"_id": _id},
                    {"$set": {"journalist": journalist, "updated_at": datetime.now()}}
                )
            )
            print(f"[QUEUE] {_id} journalist = {journalist}")
        else:
            print(f"[SKIP] Journalist not found for {_id} ({url})")

        # === jalankan bulk kalau sudah mencapai BATCH_SIZE ===
        if len(bulk_ops) >= BATCH_SIZE:
            result = collection_update.bulk_write(bulk_ops, ordered=False)
            updated_total += result.modified_count
            print(f"[BULK WRITE] {result.modified_count} dokumen diupdate (total {updated_total})")
            bulk_ops = []  # kosongkan list setelah flush

    except Exception as e:
        print(f"[ERROR] {_id} ({url}): {e}")

# === flush sisa bulk_ops kalau ada ===
if bulk_ops:
    result = collection_update.bulk_write(bulk_ops, ordered=False)
    updated_total += result.modified_count
    print(f"[FINAL BULK WRITE] {result.modified_count} dokumen diupdate (total {updated_total})")

print(f"\n✅ Selesai. Total dokumen diupdate: {updated_total}")
