import json
import sys
from bson import ObjectId
from datetime import datetime
from pymongo import MongoClient, UpdateOne
import cloudscraper
import re
import time
from bs4 import BeautifulSoup

# === Validasi argumen ===
if len(sys.argv) < 4:
    print("Usage: python update_journalist.py <start_date> <end_date> <json_file>")
    print("Example: python update_journalist.py 2025-01-01 2025-02-01 data.json")
    sys.exit(1)

start_date = datetime.fromisoformat(sys.argv[1])  # contoh: 2025-01-01
end_date   = datetime.fromisoformat(sys.argv[2])  # contoh: 2025-02-01
json_file  = sys.argv[3]

# === Koneksi MongoDB untuk update ===
client_update = MongoClient("mongodb://onlinenews_datalake:Kabayan2020@15.235.164.126:3002/?authSource=onlinenews_datalake&directConnection=true")
db_update = client_update["onlinenews_datalake"]
collection_update = db_update["streams"]

# === Load data dari file JSON ===
with open(json_file, "r", encoding="utf-8") as f:
    raw_docs = json.load(f)

docs = []
for doc in raw_docs:
    # pastikan _id dalam format ObjectId
    if isinstance(doc["_id"], dict) and "$oid" in doc["_id"]:
        doc["_id"] = ObjectId(doc["_id"]["$oid"])

    # parsing timestamp
    ts = doc.get("timestamp")
    if isinstance(ts, dict) and "$date" in ts:
        ts_raw = ts["$date"]
        ts_dt = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
    elif isinstance(ts, str):
        ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))

    if ts_dt and start_date <= ts_dt.replace(tzinfo=None) <= end_date:
        docs.append(doc)

print(f"✅ Total dokumen lolos filter: {len(docs)}")

# === Lanjut proses ===
bulk_ops = []
BATCH_SIZE = 50
updated_total = 0

for doc in docs:
    try:
        _id = doc["_id"]
        url = doc.get("url")
        print(f"Processing {_id} ({url})")
        if not url:
            continue

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }
        time.sleep(2)
        scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
        article_detail = scraper.get(url, headers=headers)
        if article_detail.status_code != 200:
            print(f"[SKIP] {url} status: {article_detail.status_code}")
            continue

        soup = BeautifulSoup(article_detail.text, "html.parser")
        journalist = None

        # === parsing sesuai url ===
        if '/video/' in url:
            print("Skip, video")
            continue
        elif '/rilis-pers/' in url:
            content = soup.find('div', class_='tags-wrapper')
            if content and content.find('span'):
                journalist = content.find('span').text.strip()
            elif content and content.find('div', class_='small'):
                journalist = content.find('div', class_='small').text.strip()
            elif content:
                match = re.search(r'Pewarta\s*:\s*(.+?)Editor:', content.get_text(" ", strip=True))
                if match:
                    journalist = match.group(1).strip()
        elif '/berita/' in url:
            if soup.find('p', class_='simple-share'):
                journalist_list = soup.find('header', class_='post-header').find('p', class_='simple-share').find_all('span', recursive=False)
                for j_elem in journalist_list:
                    j_text = j_elem.text.strip()
                    if not any(char.isdigit() for char in j_text):
                        journalist = j_text.replace('Oleh ', '').replace('*)', '').strip()
                    else:
                        content = soup.find('div', class_='tags-wrapper')
                        if content and content.find('span'):
                            journalist = content.find('span').text.strip()
                        elif content and content.find('div', class_='small'):
                            journalist = content.find('div', class_='small').text.strip()
                        elif content:
                            match = re.search(r'Pewarta\s*:\s*(.+?)Editor:', content.get_text(" ", strip=True))
                            if match:
                                journalist = match.group(1).strip()

                        if journalist:
                            if 'Penerjemah' in journalist:
                                m2 = re.search(r'Penerjemah:\s*(.*)', journalist)
                                if m2:
                                    journalist = m2.group(1).strip()
                            elif 'Pewarta' in journalist:
                                m2 = re.search(r'Pewarta:\s*(.*)', journalist)
                                if m2:
                                    journalist = m2.group(1).strip()

        # === masuk ke bulk update ===
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

        if len(bulk_ops) >= BATCH_SIZE:
            result = collection_update.bulk_write(bulk_ops, ordered=False)
            updated_total += result.modified_count
            print(f"[BULK WRITE] {result.modified_count} dokumen diupdate (total {updated_total})")
            bulk_ops = []

    except Exception as e:
        print(f"[ERROR] {doc.get('_id')} ({doc.get('url')}): {e}")

# === flush terakhir ===
if bulk_ops:
    result = collection_update.bulk_write(bulk_ops, ordered=False)
    updated_total += result.modified_count
    print(f"[FINAL BULK WRITE] {result.modified_count} dokumen diupdate (total {updated_total})")

print(f"\n✅ Selesai. Total dokumen diupdate: {updated_total}")
