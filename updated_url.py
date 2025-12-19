import re
from pymongo import MongoClient, UpdateOne
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Koneksi ke MongoDB
client = MongoClient("mongodb://onlinenews_datalake:Kabayan2020@15.235.164.126:3001/?authSource=onlinenews_datalake&directConnection=true")
db = client["onlinenews_datalake"]   
collection = db["streams"]

# Tahun sekarang
current_year = datetime.now().year

start = datetime(current_year, 9, 18, 10, 0)     # 17 Sept jam 10:00
print(start)

end = datetime(current_year, 9, 18, 14, 30)      # 18 Sept jam 14:30
print(end)
# Query data portal Kisi dengan timestamp tahun ini
docs = collection.find(
    {
        "portal": "Kisi",
        "timestamp": {"$gte": start, "$lt": end}
    },
    {"url": 1, "url_origin": 1, "timestamp":1}
)

bulk_ops = []
batch_size = 50
count = 0
total_updated = 0

for doc in docs:
    url = doc.get("url")
    url_origin = doc.get("url_origin")
    timestamp = doc.get("timestamp")
    print(f"Processing : {url}")
    if '/blog/artikel/blog/artikel/' in url:
        print("Sudah update, Skip")
        continue
    print(f"Run Date : {timestamp}")
    try:
        response = requests.get(url, timeout=10)
    except Exception as e:
        print(f"Error request {url}: {e}")
        continue  # skip kalau error request
    
    page = BeautifulSoup(response.text, "html.parser")
    if page.find('noscript'):
        # Ambil ID numeric di akhir URL (misal: 34489, 33625, dst.)
        match = re.search(r"/(\d+)$", url)
        if match:
            article_id = match.group(1)
            new_url = f"https://kisi.co.id/blog/artikel/blog/artikel/{article_id}"
        else:
            new_url = url  # fallback kalau tidak ketemu ID

        if url_origin:
            match_origin = re.search(r"/(\d+)$", url_origin)
            if match_origin:
                article_id_origin = match_origin.group(1)
                new_url_origin = f"https://kisi.co.id/blog/artikel/blog/artikel/{article_id_origin}"
            else:
                new_url_origin = url_origin
        else:
            new_url_origin = url_origin
        
        bulk_ops.append(
            UpdateOne(
                {"_id": doc["_id"]},
                {"$set": {
                    "url": new_url,
                    "url_origin": new_url_origin,
                    "updated_at": datetime.now()
                }}
            )
        )

        count += 1
        print(f"Prepared: {doc['_id']} | {url} -> {new_url}")

        # Eksekusi setiap batch_size (10 dokumen)
        if count % batch_size == 0:
            result = collection.bulk_write(bulk_ops, ordered=False)
            print(f"Bulk update {count} dokumen. Modified: {result.modified_count}")
            total_updated += result.modified_count
            bulk_ops = []

# Eksekusi sisa dokumen
if bulk_ops:
    result = collection.bulk_write(bulk_ops, ordered=False)
    print(f"Bulk update terakhir. Modified: {result.modified_count}")
    total_updated += result.modified_count

print(f"Selesai update data. Total Modified: {total_updated}")
