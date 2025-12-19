import pandas as pd
import json
import math

# Membaca data dari file Excel
excel_path = '/home/andra/Documents/Kerjaan/engine-pribadi/plugin_check_all_results.xlsx'
df = pd.read_excel(excel_path)

# Membaca data dari file JSON
json_path = '/home/andra/Documents/Kerjaan/engine-pribadi/onlinenews_datalake.scraper1.json'
with open(json_path, 'r') as f:
    json_data = json.load(f)

# Membuat array untuk menyimpan hasil
data = []

# Menyusun URL dari Excel dan mencocokkannya dengan domain di JSON
for url, status in zip(df['url'], df['status']):
    if status == 'Berhasil' and url and isinstance(url, str):
        for item in json_data:
            if item.get('domain') and isinstance(item['domain'], str) and item['domain'] in url:
                data.append([item['_id'], url])

# Menampilkan jumlah total data yang cocok
total = len(data)
print(f"Total data yang cocok: {total}")

# Menentukan ukuran chunk
chunk_size = 50
chunks = [data[i:i + chunk_size] for i in range(0, total, chunk_size)]

# Menyimpan hasil ke dalam file JSON terpisah
for i, chunk in enumerate(chunks, start=1):
    output_path = f'/home/andra/Documents/Kerjaan/engine-pribadi/SWP_json_{i}.json'
    with open(output_path, 'w') as f:
        json.dump(chunk, f, indent=2)
    print(f"Hasil bagian {i} ({len(chunk)} entri) telah disimpan ke {output_path}")
