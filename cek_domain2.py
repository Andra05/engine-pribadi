import pandas as pd
import requests
import json
import cloudscraper
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}
# Path ke file Excel
input_excel = "/home/andra/Downloads/Telegram Desktop/17122025_Format_Permintaan_Pembuatan_Scraper_Tahap_1_345_Media_Online.xlsx"

# Membaca file Excel
df = pd.read_excel(input_excel)
# Menyimpan hasil sukses dan gagal
results = []

# Iterasi per baris
for index, row in df.iterrows():
    domain = row['URL Media']
    url = f"https://{domain}/wp-json/wp/v2/posts?_embed&per_page=10"
    print(f"Mengecek: {url}")
    try:
        scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
        response = scraper.get(url, headers=headers)
        if response.status_code == 200:
            try:
                json.loads(response.text)
                print("✅ Berhasil")
                results.append({'url': url, 'status': 'Berhasil'})
            except json.JSONDecodeError:
                print("❌ Gagal - Respon bukan JSON")
                results.append({'url': url, 'status': 'Gagal - Respon bukan JSON'})
        else:
            print(f"❌ Gagal - Status code: {response.status_code}")
            results.append({'url': url, 'status': f'Gagal - Status code: {response.status_code}'})
    except requests.RequestException as e:
        print(f"❌ Gagal - Error: {e}")
        results.append({'url': url, 'status': f'Gagal - Error: {e}'})

# Simpan semua hasil ke Excel baru
output_df = pd.DataFrame(results)
output_path = "/home/andra/Documents/Kerjaan/engine-pribadi/plugin_check_300++_results.xlsx"
output_df.to_excel(output_path, index=False)

print(f"\nHasil lengkap disimpan di: {output_path}")
