import os
import re
import pandas as pd

# Paths
excel_path = '/home/andra/Downloads/Telegram Desktop/list_wordpress.ods'
tier_excel_path = '/home/andra/Downloads/Telegram Desktop/Pembuatan Scrapper Pelindo (1).xlsx'
output_excel = 'request_scraper1.xlsx'

# Load URL list dari Excel pertama
df_urls = pd.read_excel(excel_path)
url_list = df_urls.iloc[:, 0].dropna().tolist()
# Load Tier & Cakupan dari Excel kedua
df_tier = pd.read_excel(tier_excel_path)
# Asumsi: URL Media di kolom kedua (index 1), Tier di kolom ketiga (index 2), Cakupan di kolom kelima (index 4)

result = []

# Loop file di coba
for base_url in url_list:
    match = df_tier[df_tier['URL Media'] == base_url]
    if not match.empty:
        tier = match.iloc[0]['Tier']
        cakupan = match.iloc[0]['Cakupan']
        scraper_name = base_url
        if scraper_name in base_url:
            result.append({
                'file_name': "WP.py",
                'scraper_name': scraper_name,
                'url': base_url,
                'tier': tier,
                'cakupan': cakupan
            })

# Simpan ke Excel baru
df_result = pd.DataFrame(result)
df_result.to_excel(output_excel, index=False)

print(f"Selesai! File hasil: {output_excel}")
