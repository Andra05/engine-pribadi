import os
import re

# Path folder yang berisi file yang akan dimodifikasi
folder_path = "/home/andra/Documents/Kerjaan/dags-sc-01"

# Pola yang akan dicari dalam file
pattern = re.compile(r"schedule_interval\s*=\s*'(?P<minute>\d{1,2}) \*/1 \* \* \*'")

# Variasi pengganti
replacements = [
    "0-23/3",
    "1-23/3",
    "2-23/3",
    "3-23/3",
    "4-23/3",
    "5-23/3"
]

# Mendapatkan semua file dalam folder
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

for i, filename in enumerate(files):
    file_path = os.path.join(folder_path, filename)
    
    # Membaca isi file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Mengecek apakah pola ada dalam file
    match = pattern.search(content)
    if match:
        minute = match.group("minute")
        new_schedule = f"{minute} {replacements[i % len(replacements)]} * * *"
        new_content = pattern.sub(f"schedule_interval = '{new_schedule}'", content)
        
        # Menulis ulang file dengan perubahan
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print(f"Modified: {filename} -> {new_schedule}")
