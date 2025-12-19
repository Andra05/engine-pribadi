import os

# Path folder
folder_onsite = "/home/andra/Documents/Kerjaan/online-news-scraper/onsite-sc01"
folder_vm3 = "/home/andra/Documents/Kerjaan/online-news-scraper/VM 3"

# Ambil list file di masing-masing folder
files_onsite = set(os.listdir(folder_onsite))
files_vm3 = set(os.listdir(folder_vm3))

# Cari file yang sama
same_files = sorted(files_onsite.intersection(files_vm3))

# Simpan hasil ke file txt
output_file = "/home/andra/Documents/Kerjaan/same_files.txt"
with open(output_file, "w") as f:
    if same_files:
        f.write("File yang sama di kedua folder (hanya .py yang dihapus dari onsite):\n")
        for filename in same_files:
            f.write(filename + "\n")

            # Hanya hapus file .py
            if filename.endswith(".py"):
                file_path_onsite = os.path.join(folder_onsite, filename)
                if os.path.exists(file_path_onsite):
                    os.remove(file_path_onsite)
                    print(f"Deleted: {file_path_onsite}")
    else:
        f.write("Tidak ada file yang sama.\n")

print(f"Validasi selesai. Hasil disimpan di {output_file}")
