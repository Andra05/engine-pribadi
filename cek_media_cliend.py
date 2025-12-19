import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# 1. Baca Excel
# Ganti path sesuai file Anda
input_excel = "/home/andra/Downloads/Telegram Desktop/Untitled 1.ods"
df = pd.read_excel(input_excel)
# print(df)
# exit()
# 2. Koneksi MongoDB
client = MongoClient("mongodb://onlinenews_datalake:Kabayan2020@15.235.164.126:3001/?authSource=onlinenews_datalake&directConnection=true")
db = client["onlinenews_datalake"]
collection = db["streams"]

# 3. Siapkan list hasil
results = []

# 4. Loop tiap URL Media
for url_media in df['URL Media']:
    # Query: cari dokumen terbaru
    doc = collection.find_one(
        {"id_account".replace("www.", ""): url_media.lower()},
        sort=[("date", -1)],
        projection={"_id": 0, "url": 1, "date": 1}
    )
    # Tambahkan ke hasil
    if doc:
        results.append({
            "URL Media": url_media,
            "URL": doc.get("url", ""),
            "Date": doc.get("date", "")
        })
    else:
        results.append({
            "URL Media": url_media,
            "URL": "Not found",
            "Date": ""
        })

# 5. Buat DataFrame hasil
result_df = pd.DataFrame(results)

# 6. Simpan ke Excel baru
output_excel = "url_media_latest_articles(3).xlsx"
result_df.to_excel(output_excel, index=False)

print(f"Hasil disimpan ke {output_excel}")
