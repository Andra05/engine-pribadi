import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# === KONFIGURASI ===
INPUT_JSON = "/home/andra/Downloads/Telegram Desktop/dl_tiktok.formatted_streams.json"
OUTPUT_EXCEL = "/home/andra/Documents/Kerjaan/engine-pribadi/data_tiktok.xlsx"

# === FUNGSI UTAMA ===
def json_to_excel_tiktok(input_file, output_file):
    # Baca file JSON
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = [data]

    rows = []
    for i, item in enumerate(data, start=1):
        # Ambil tanggal publikasi
        date_str = item.get("date", {}).get("$date") or item.get("date")
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        published_date = dt.strftime("%d-%m-%Y")
        published_time = dt.strftime("%H:%M:%S")

        # Ambil tanggal simpan
        created_str = item.get("created_at", {}).get("$date") or datetime.now().isoformat()
        saved_date = datetime.fromisoformat(created_str.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")

        # Ambil detail engagement
        engagement_detail = item.get("engagement_detail", {})
        like = engagement_detail.get("like", 0)
        comment = engagement_detail.get("comment", 0)
        share = engagement_detail.get("share", 0)
        play = engagement_detail.get("play", 0)
        engagement_count = item.get("engagement_count", 0)

        # Ambil konten (caption video)
        content = item.get("content", "").strip()

        rows.append({
            "No": i,
            "Published Date": published_date,
            "Published Time": published_time,
            "Saved Date": saved_date,
            "Content": content,
            "Media Type": "video",
            "URL": item.get("url", ""),
            "Like": like,
            "Comment": comment,
            "Retweet": share,
            "Engagement Count": engagement_count,
            "Engagement": engagement_count,
        })

    df = pd.DataFrame(rows, columns=[
        "No", "Published Date", "Published Time", "Saved Date", "Content",
        "Media Type", "URL", "Like", "Comment", "Retweet", "View",
        "Engagement Count", "Engagement"
    ])

    df.to_excel(output_file, index=False)
    print(f"✅ File berhasil dibuat: {Path(output_file).resolve()}")

# === JALANKAN ===
if __name__ == "__main__":
    json_to_excel_tiktok(INPUT_JSON, OUTPUT_EXCEL)
