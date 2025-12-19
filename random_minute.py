import os
import re
import random

# Daftar path direktori
paths = ['/home/andra/Documents/Kerjaan/dags-vm2']

# Pola regex untuk menangkap schedule_interval
pattern = re.compile(r'(schedule_interval\s*=\s*[\'"])\d{1,2}(\s+[^\n\'"]+)([\'"])')

def modify_schedule_interval(directory):
    total_modified = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):  # Hanya file Python
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Ganti menit pertama dengan angka acak
                    def replace_schedule(match):
                        new_minute = str(random.randint(0, 59))  # Random 0-59
                        return f"{match[1]}{new_minute}{match[2]}{match[3]}"

                    modified_content = pattern.sub(replace_schedule, content)

                    # Tulis kembali file yang telah dimodifikasi
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(modified_content)

                    total_modified += len(pattern.findall(content))

                except Exception as e:
                    print(f"Error modifying {file_path}: {e}")

    return total_modified

# Total semua yang dimodifikasi
grand_total = sum(modify_schedule_interval(path) for path in paths)

# Cetak hasil akhir
print(f"\nTotal schedule_interval yang diubah: {grand_total}")
