# from undetected_chromedriver import Chrome
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pandas as pd
import time
from dotenv import load_dotenv
load_dotenv()

# Inisialisasi options

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# driver = Chrome(options=chrome_options)
driver = webdriver.Chrome(options=chrome_options)


url = "https://sp134.idcloudhosting.cloud:8443/login_up.php"
driver.get(url)

driver.find_element(By.ID, "login_name").send_keys('andra')
time.sleep(5)
driver.find_element(By.ID, "passwd").send_keys('d6?6mNg63')
driver.find_element(By.NAME, "send").click()
WebDriverWait(driver, 20).until(EC.url_changes(url))

# Cetak URL baru
print("Berhasil Login Url dasboard:", driver.current_url)
url_addsubdomain = "https://sp134.idcloudhosting.cloud:8443/smb/web/add-subdomain"
driver.get(url_addsubdomain)
domain_utama = "primerpos.com"
subdomain = [
  "AcehPos",
  "SumateraUtaraPos",
  "SumateraBaratPos",
  "RiauPos",
  "KepulauanRiauPos",
  "JambiPos",
  "SumateraSelatanPos",
  "BengkuluPos",
  "LampungPos",
  "KepulauanBangkaBelitungPos",
  "DKIJakartaPos",
  "JawaBaratPos",
  "JawaTengahPos",
  "DIYogyakartaPos",
  "JawaTimurPos",
  "BantenPos",
  "BaliPos",
  "NusaTenggaraBaratPos",
  "NusaTenggaraTimurPos",
  "KalimantanBaratPos",
  "KalimantanTengahPos",
  "KalimantanSelatanPos",
  "KalimantanTimurPos",
  "KalimantanUtaraPos",
  "SulawesiUtaraPos",
  "SulawesiTengahPos",
  "SulawesiSelatanPos",
  "SulawesiTenggaraPos",
  "SulawesiBaratPos",
  "GorontaloPos",
  "MalukuPos",
  "MalukuUtaraPos",
  "PapuaPos",
  "PapuaBaratPos",
  "PapuaTengahPos",
  "PapuaSelatanPos",
  "PapuaPegununganPos",
  "PapuaBaratDayaPos",
  "Keuangan",
  "Infobiz"
]

for sub in subdomain:
    # Isi subdomain
    subdomain_field = driver.find_element(By.ID, "domainName-name")
    subdomain_field.clear()
    subdomain_field.send_keys(sub)

    time.sleep(1)

    # Isi domain utama
    domain_input = driver.find_element(By.CSS_SELECTOR, "#domainName-domain input.form-control")
    domain_input.click()
    domain_input.clear()
    domain_input.send_keys(domain_utama)

    # 2. Tunggu dropdown-nya muncul
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.lookup-dropdown-menu"))
    )

    # 3. Jalankan script JS buat klik item "primerpos.com"
    script = """
    let items = document.querySelectorAll('li.dropdown-menu-list-item');
    for (let item of items) {
        if (item.textContent.includes("primerpos.com")) {
            item.style.display = 'block'; // pastikan visible kalau sebelumnya hidden
            item.scrollIntoView(); // kalau perlu scroll ke situ
            item.click();
            break;
        }
    }
    """
    driver.execute_script(script)
    # script = """
    # let items = document.querySelectorAll('li.dropdown-menu-list-item');
    # for (let item of items) {
    #     if (item.textContent.includes("primerpos.com")) {
    #         item.style.display = 'block'; // pastikan visible
    #         item.click();
    #         break;
    #     }
    # }
    # """
    # domain_input = driver.find_element(By.CSS_SELECTOR, "#domainName-domain input.form-control")
    # domain_input.click()
    # domain_input.clear()
    # domain_input.send_keys(domain_utama)
    # WebDriverWait(driver, 10).until(
    #     EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.lookup-dropdown-menu"))
    # )
    # dropdown_items = driver.find_elements(By.CSS_SELECTOR, "li.dropdown-menu-list-item a")
    # for item in dropdown_items:
    #     if domain_utama in item.text:
    #         item.click()
    #         break
    time.sleep(5)

    # Isi root folder
    root_field = driver.find_element(By.ID, "hostingSettings-root")
    root_field.clear()
    root_field.send_keys("httpdocs")

    time.sleep(1)

    # Klik tombol oke
    driver.find_element(By.ID, "btn-send").click()
    print(f"Subdomain '{sub}.{domain_utama}' dikirim.")
    time.sleep(5)

    # get url add subdomain
    driver.get(url_addsubdomain)
    time.sleep(3)

driver.quit()