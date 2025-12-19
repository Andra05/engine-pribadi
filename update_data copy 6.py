import requests
import time
import sys
import re
from bs4.element import Tag

from datetime import datetime, timedelta
from dateutil import parser
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from bson.objectid import ObjectId
import cloudscraper
from modules.proxy import Proxy, proxy_get
from model.db import DBMongo
import pytz
from modules.helper import ChangeMonth, related_links
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from pymongo import UpdateOne
from bs4 import BeautifulSoup
import requests, cloudscraper
load_dotenv()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

today = datetime.today()
d = today.strftime('%d')
m = today.strftime('%m')
y = datetime.today().year
array_error =[]

class Femina:

    def __init__(self):
        self.StartTime = time.time()
        self.IST = pytz.timezone('Asia/Jakarta')
        self.datetime_ist = datetime.now(self.IST)
        
        # log_format = "%(levelname)s %(asctime)s - %(message)s"
        # logging.basicConfig(filename=self.filename, filemode='w', format=log_format, level=logging.ERROR)
        # self.logger = logging.getLogger()

        self.ConnectionDB = DBMongo(HOST = os.getenv('DB_HOST'), USERNAME = os.getenv('DB_USER'), PASSWORD = os.getenv('DB_PASS'), AUTH_SOURCE = os.getenv('DB_NAME'))
        self.db = None
        self.streams = None
        self.logs = None
        self.logs_proxy= None
        self.proxy = None
        self.counter = 0
        self.page = 1
        self.log_error = []

    def __enter__(self):
        print("--------------------------------------------------------")
        print("           Online News Scraper: Femina")
        print("--------------------------------------------------------")
        print("Started Time:", self.datetime_ist)
        self.db = self.ConnectionDB.GetDatabase(os.getenv('DB_NAME'))
        self.streams = self.db['streams']
        self.logs = self.db['logs']
        self.scraper = self.db['scraper']
        self.proxy = self.db['proxy']
        self.logs_proxy = self.db['logs_proxy']	
        return self

    def insert(self, dict):
        stream = self.streams.insert_one(dict)
        # if stream.inserted_id:
        #     print("Data inserted sucessfully")
        # else:
        #     print("Data Not Inserted")

    def insert_log(self):
        logs = {}
        logs['scraper_name'] = 'Femina'
        logs['start'] = datetime.now()
        logs['end'] = None
        logs['duration'] = None
        logs['count'] = None
        logs['status'] = 'Running'
        # logs['log'] = self.filename

        log = self.logs.insert_one(logs)
        logs['id'] = log.inserted_id

        return logs


    def get_content(self, url):
        berita = self.streams.find_one({'origin_url': url})
        print(berita['content'])
        
        
        if berita and 'content' in berita:
            # Membersihkan teks dari "Baca juga:" hingga akhir baris
            teks_bersih = re.sub(r'^Baca Juga.*$', '', berita['content'], flags=re.MULTILINE)
            
            # print(teks_bersih)
            # exit()
            return teks_bersih  # Mengembalikan teks yang sudah dibersihkan
        else:
            print("Berita tidak ditemukan atau tidak memiliki konten.")
            return None

    def get_journalist(self, page):
        writer = page.find('div', id='penulis')
        editor = page.find('div', id='editor')
        credit_names = page.find('div', class_='credit-title-name')

        if writer:
            if 'Kontributor' in writer.text:
                journalist = writer.text.split(', ')[1].strip()
            else:
                journalist = writer.text.replace('Penulis ', '').replace('Kontributor ', '').strip()
        elif editor:
            journalist = editor.text.replace('Editor ', '').strip()
        elif credit_names:
            # Ambil semua editor dari credit-title-nameEditor dan filter yang kosong
            editors = credit_names.find_all('div', class_='credit-title-nameEditor')
            journalist = ' '.join([e.text.strip() for e in editors if e.text.strip()])

            
        return journalist
    
    def request(self, url, params=None, **kwargs):
        scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
        allow_redirects = kwargs.get('allow_redirects', True)
        max_retries = 3
        retries = 0
        page = None
        while retries < max_retries:
            try :
                ## Pakai Proxy
                get_proxy = proxy_get()
                if get_proxy is not None:
                    print(f"Proxy  : {get_proxy.partition('@')[2]}")
                    proxies = {
                        "https": "socks5://"+ get_proxy,
                        "http": "socks5://"+ get_proxy,
                    }
                    # page = scraper.get(url,  proxies=proxies,  headers=headers, params=params, allow_redirects=allow_redirects)
                    page = requests.get(url, proxies=proxies, params=params, headers=headers, allow_redirects=allow_redirects)
                    if page.status_code != 200:
                        print('Gagal Pakai Proxy', str(page.status_code))
                        print("Retrying...")
                        retries += 1
                        logs_ ={
                            "url": url, 
                            "proxy": get_proxy.partition('@')[2].partition(':')[0],
                            "port": get_proxy.partition('@')[2].partition(':')[2],
                            "message": "Gagal pakai Proxy Status Code:" + str(page.status_code),
                            "status": "Failed"
                            }
                        self.logs_proxy.insert_one(logs_)
                        continue
                    logs_ ={
                        "url": url, 
                        "proxy": get_proxy.partition('@')[2].partition(':')[0],
                        "port": get_proxy.partition('@')[2].partition(':')[2],
                        "status": "Success"
                        }
                    self.logs_proxy.insert_one(logs_)
                    break
                ## Tidak pakai Proxy
                else:
                    print('Proxy Tidak Ada')
                    page = scraper.get(url, params=params,  headers=headers, allow_redirects=allow_redirects)

                    # page = requests.get(url, params=params,  headers=headers, allow_redirects=allow_redirects)
            # except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.ChunkedEncodingError, ValueError, TypeError, KeyError, AttributeError) as e:
            except (requests.exceptions.ConnectionError, requests.exceptions.TooManyRedirects, BaseException) as e:
                logs_ = {
                    "url": url, 
                    "proxy": get_proxy.partition('@')[2].partition(':')[0],
                    "port": get_proxy.partition('@')[2].partition(':')[2],
                    "message": "Gagal pakai Proxy: " + str(e),  # Convert the exception to a string
                    "status": "Failed"
                }
                self.logs_proxy.insert_one(logs_)
                print(e)
                retries += 1
                print("Retrying...")
                continue
        return(page)


    def parse_page(self, url=None):
        # Path file JSON
        file_path = r"ada.json"
        if not os.path.exists(file_path):
            print("File tidak ditemukan:", file_path)
            return

        # Load JSON
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Ambil semua origin_url tanpa filter
        berita = [item.get("origin_url") for item in data if "origin_url" in item]

        if not berita:
            print("Tidak ada artikel ditemukan.")
            return

        print("Contoh URL pertama:", berita[0])
        print("Total articles:", len(berita))
    

        # --- Bulk Update Setup ---
        bulk_ops = []
        batch_size = 50
        self.counter = 0

        for article in berita:
            try:
                source = article + "?page=all"
                print("Processing:", article)

                try:
                    page = self.request(source)
                    if page is None or not isinstance(page, requests.Response):
                        print('Failed to use Proxy, fallback to cloudscraper...')
                        scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
                        page = scraper.get(source)

                    if page.status_code != 200:
                        print('Error:', page.status_code, "URL:", source)
                        continue
                except requests.exceptions.ConnectionError:
                    print("Error: Gagal mengambil berita karena halaman down")
                    continue

                soup = BeautifulSoup(page.text, 'html.parser')
                journalist = self.get_journalist(soup)  # ambil nama jurnalis

                # Tambahkan ke batch update
                bulk_ops.append(
                    UpdateOne(
                        {'origin_url': article},
                        {
                            '$set': {
                                'journalist': journalist,
                                'updated_at': datetime.now()
                            }
                        }
                    )
                )
                self.counter += 1

                # Kalau sudah batch_size, eksekusi bulk_write
                if len(bulk_ops) >= batch_size:
                    self.streams.bulk_write(bulk_ops, ordered=False)
                    print(f"{len(bulk_ops)} records updated (batch commit)")
                    bulk_ops = []  # reset batch

            except Exception as e:
                print(f"Error saat proses {article}: {str(e)}")
                continue

        # Eksekusi sisa batch
        if bulk_ops:
            self.streams.bulk_write(bulk_ops, ordered=False)
            print(f"{len(bulk_ops)} records updated (last batch)")

        return self.counter

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print("Close Database Connection...")
        print("Ended at: {}".format(datetime.now(self.IST)))
        self.ConnectionDB.DisconnectDatabase()
        print("----------- Crawler Run %f seconds -----------" %(time.time() - self.StartTime))

if __name__ == '__main__':

    with Femina() as crawler:
        logs = crawler.insert_log()
        ## Update File name Scraper
        file_name = os.path.basename(__file__)
        crawler.scraper.update_one(
            {'_id':logs['scraper_name']},
            {'$set': {'file_name': file_name}}
        )
        ## End
        try:
            base_url = "#"
            total_data = crawler.parse_page(base_url)
            print("Sucessfully processing {} article(s)".format(crawler.counter))

            ## cek method log error ada tidak
            if len(crawler.log_error) > 0:
                crawler.logs.update_one({'_id': ObjectId(logs['id'])}, {'$set': {'end': datetime.now(), 'count': total_data, 'duration': (datetime.now()-logs['start']).total_seconds(), 'status': 'Error','error_message':crawler.log_error[0]}})
            else:
                crawler.logs.update_one({'_id': ObjectId(logs['id'])}, {'$set': {'end': datetime.now(), 'count': total_data, 'duration': (datetime.now()-logs['start']).total_seconds(), 'status': 'Completed'}})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(str(e), exc_type, fname, exc_tb.tb_lineno)
            crawler.logs.update_one({'_id': ObjectId(logs['id'])}, {'$set': {'end': datetime.now(), 'count': 0, 'duration': (datetime.now()-logs['start']).total_seconds(), 'status': 'Error',  'error_message': (str(e) + ' Line : ' + str(exc_tb.tb_lineno) + ' ' + str(exc_type))}})