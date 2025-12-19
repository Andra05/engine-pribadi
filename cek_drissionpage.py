from DrissionPage import ChromiumPage
import subprocess

# Inisialisasi ChromiumPage
page = ChromiumPage()

# Ambil path ke Chromium executable dari konfigurasi
chromium_path ='/usr/bin/google-chrome'

# Jalankan chromium dengan --version
result = subprocess.run([chromium_path, '--version'], capture_output=True, text=True)

# Tampilkan hasil
print('Chromium version:', result.stdout.strip())
