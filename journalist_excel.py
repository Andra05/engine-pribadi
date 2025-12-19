import pandas as pd
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

# ==== CONFIG ====
EXCEL_FILE = "/home/andra/Downloads/Telegram Desktop/DataCleansing-Kemlu-Adam-Malik-Awards-2025-08-20-17_03_37.xlsx"   # ganti path file excel
MONGO_URI = "mongodb://onlinenews_datalake:Kabayan2020@15.235.164.126:3002/?authSource=onlinenews_datalake&directConnection=true"
DB_NAME = "onlinenews_datalake"
COLLECTION_NAME = "streams"

# ==== CONNECT MONGO ====
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ==== BACA EXCEL ====
df = pd.read_excel(EXCEL_FILE)
# Ambil kolom N (kolom ke-14 karena index mulai 0)
urls = df.iloc[:, 13].dropna().tolist()

for url in urls:
    try:
        print(url)
        exit()
        print(f"[INFO] Requesting {url}")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # === CARA AMBIL NAMA JURNALIS ===
        # Ganti sesuai struktur halaman. Contoh misal ada <meta name="author">:
        journalist = None
        author_meta = soup.find("meta", attrs={"name": "author"})
        if author_meta:
            journalist = author_meta.get("content")

        # Kalau pakai class tertentu
        if not journalist:
            author_tag = soup.find("span", class_="journalist")
            if author_tag:
                journalist = author_tag.get_text(strip=True)

        if journalist:
            result = collection.update_one(
                {"url": url},   # cari berdasarkan url
                {"$set": {
                    "journalist": journalist,
                    "updated_at": datetime.now()
                }}
            )
            if result.matched_count > 0:
                print(f"[OK] Updated journalist='{journalist}' for {url}")
            else:
                print(f"[WARN] URL {url} not found in Mongo")
        else:
            print(f"[WARN] Journalist not found in page: {url}")

    except Exception as e:
        print(f"[ERROR] Failed for {url}: {e}")
