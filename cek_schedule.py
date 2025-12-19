import os
import re

# Path direktori yang ingin diproses
paths = [
    '/home/andra/Documents/Kerjaan/dags-vm2',
    '/home/andra/Documents/Kerjaan/dags-vm3'
]

# Tangkap schedule_interval = '...'
pattern = re.compile(r"(schedule_interval\s*=\s*['\"])([^'\"]+)(['\"])")

def modify_schedule_interval(directory):
    total_modified = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith(".py"):
                continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                modifications = []  # list perubahan di file ini

                def repl(m):
                    original = m.group(2).strip()
                    parts = original.split()
                    # Pastikan cron-like (>= 5 kolom)
                    if len(parts) >= 5:
                        minute = parts[0]
                        new_value = f"{minute} */1 * * *"
                        if new_value != original:
                            modifications.append((original, new_value))
                            return f"{m.group(1)}{new_value}{m.group(3)}"
                    return m.group(0)

                new_content = pattern.sub(repl, content)

                if modifications:
                    # tulis ulang file tanpa bikin backup
                    with open(file_path, "w", encoding="utf-8") as wf:
                        wf.write(new_content)

                    for orig, new in modifications:
                        print(f"Modified File: {file_path}")
                        print(f"  Original: {orig}")
                        print(f"  Modified: {new}\n")

                    total_modified += len(modifications)

            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    return total_modified

# Jalankan untuk semua direktori
grand_total = 0
for p in paths:
    print(f"\nChecking directory: {p}")
    t = modify_schedule_interval(p)
    print(f"Total modified in {p}: {t}")
    grand_total += t

print(f"\nGrand total modified across all directories: {grand_total}")
