import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# === KONFIGURASI ===
INPUT_JSON = "/home/andra/Downloads/Telegram Desktop/MoFAIndonesia_videos.json"
OUTPUT_EXCEL = "/home/andra/Documents/Kerjaan/engine-pribadi/data_youtube1.xlsx"

# === FUNGSI UTAMA ===
def json_to_excel(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = [data]

    rows = []
    for i, item in enumerate(data, start=1):
        dt = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
        published_date = dt.strftime("%d-%m-%Y")
        published_time = dt.strftime("%H:%M:%S")
        saved_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        content = item.get("content") or item.get("title") or ""
        engagement_detail = item.get("engagement_detail", {})

        like = engagement_detail.get("like", 0)
        comment = engagement_detail.get("comment", 0)
        retweet = engagement_detail.get("retweet", 0)  # default 0
        view = engagement_detail.get("view", 0)        # ambil kalau ada
        engagement_count = item.get("engagement_count", 0)

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
            "Retweet": retweet,
            "View": view,
            "Engagement Count": engagement_count,
            "Engagement Rate": engagement_count,
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
    json_to_excel(INPUT_JSON, OUTPUT_EXCEL)
