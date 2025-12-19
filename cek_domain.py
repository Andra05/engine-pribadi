import json
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os

# Path ke file JSON
# json_path = "/home/andra/Documents/Kerjaan/engine-pribadi/onlinenews_datalake.scraper.json"

# # Load isi JSON
# with open(json_path, 'r') as file:
#     data = json.load(file)

# scraper = cloudscraper.create_scraper()
# results = []

# for item in data:
#     domain = item.get("domain")
    # file_name = item.get("file_name")
    # if not domain or not file_name:
    #     continue
    
excel_path = "/home/andra/Downloads/Telegram Desktop/Format Permintaan Pembuatan Scraper_Medco.xlsx"

# Load isi Excel
df = pd.read_excel(excel_path)

scraper = cloudscraper.create_scraper()
results = []

for index, row in df.iterrows():
    domain = row['URL Media']
    if not domain:
        continue

    url = f"https://{domain}"
    print(f"Mengakses: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')

        found = False
        for script in scripts:
            if script.string and '/wp-content/' in script.string:
                found = True
                break
            if script.has_attr('src') and '/wp-content/' in script['src']:
                found = True
                break

        if found:
            results.append({
                # "nama file": file_name,
                "domain": domain,
                "keterangan": "Ditemukan /wp-content/"
            })
            print(f"✅ Ditemukan plugin di {domain}")
        else:
            print(f"❌ Tidak ditemukan plugin di {domain} (tidak dimasukkan ke Excel)")

    except Exception as e:
        print(f"⚠️ Gagal mengakses {domain}: {e}")

# Simpan ke Excel hanya jika ada hasil
if results:
    df = pd.DataFrame(results)
    output_path = os.path.expanduser("~/plugin_check_results.xlsx")
    df.to_excel(output_path, index=False)
    print(f"\n📁 Hasil disimpan ke: {output_path}")
else:
    print("\n🚫 Tidak ada domain yang ditemukan mengandung /wp-content/, Excel tidak dibuat.")
