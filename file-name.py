import os
import json
import glob
import pandas as pd

json_folder = '/home/andra/Documents/Kerjaan/engine-pribadi'
python_folder = '/home/andra/Documents/Kerjaan/online-news-scraper'

json_files = [f'SWP_json_{i}.json' for i in range(1, 26)]
nama_list = set()

print("📂 Membaca semua file JSON...")
for json_file in json_files:
    json_path = os.path.join(json_folder, json_file)
    if os.path.exists(json_path):
        print(f"🔎 Membaca: {json_file}")
        with open(json_path, 'r') as f:
            try:
                data = json.load(f)
                for item in data:
                    if isinstance(item, list) and len(item) >= 1:
                        nama_list.add(item[0])
            except Exception as e:
                print(f"❌ Gagal membaca {json_file}: {e}")
    else:
        print(f"⚠️ File tidak ditemukan: {json_file}")

print(f"✅ Total nama unik ditemukan dari JSON: {len(nama_list)}\n")

print("📂 Mengambil semua file Python dari subfolder...")
python_files = glob.glob(os.path.join(python_folder, '**', '*.py'), recursive=True)
print(f"✅ Total file Python ditemukan: {len(python_files)}\n")

hasil = []

for nama in sorted(nama_list):
    print(f"🔍 Mencari string: \"{nama}\"")
    ditemukan = False
    lokasi_ditemukan = ''
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if f'"{nama}"' in line or f"'{nama}'" in line:
                        print(f"✅ Ditemukan di file: {py_file}")
                        ditemukan = True
                        lokasi_ditemukan = py_file
                        break
        except Exception as e:
            print(f"❌ Gagal membaca file: {py_file} ({e})")
        if ditemukan:
            break

    if not ditemukan:
        print(f"❌ Tidak ditemukan di file mana pun.")

    hasil.append({
        'Nama': nama,
        'Status': 'ada' if ditemukan else 'tidak ada',
        'File Python': lokasi_ditemukan if ditemukan else '-'
    })
    print("-" * 50)

output_excel = 'hasil_pencocokan.xlsx'
df = pd.DataFrame(hasil)
df.to_excel(output_excel, index=False)

print(f"\n🎉 Selesai! Hasil disimpan di: {output_excel}")
