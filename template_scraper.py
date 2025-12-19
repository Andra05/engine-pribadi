scraper_template = """
import requests
import time
import sys
import cloudscraper
from modules.proxy import Proxy, proxy_get
from datetime import datetime, timedelta
from dateutil import parser
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from bson.objectid import ObjectId
from urllib3.util.retry import Retry
from pymongo import MongoClient, errors, UpdateOne
from requests.adapters import HTTPAdapter
from model.db import DBMongo
import pytz
from modules.helper import ChangeMonth, cek_date
import os
from dotenv import load_dotenv
load_dotenv()

headers = {{
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}}


today = datetime.today()
d = today.strftime('%d')
m = today.strftime('%m')
y = datetime.today().year
array_error =[]

class (nama domain):

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
        self.counter = 0
        self.page = 1
        self.log_error = []
        self.proxy = None
        self.logs_proxy= None

    def __enter__(self):
        print("--------------------------------------------------------")
        print("           Online News Scraper: (nama domain)")
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
        logs = {{}}
        logs['scraper_name'] = '(nama domain)'
        logs['start'] = datetime.now()
        logs['end'] = None
        logs['duration'] = None
        logs['count'] = None
        logs['status'] = 'Running'
        # logs['log'] = self.filename

        log = self.logs.insert_one(logs)
        logs['id'] = log.inserted_id

        return logs

    def get_title(self, page):
        title = page.find('meta', attrs={{'property':'og:title'}})['content']
        return title

    def get_journalist(self, page):
        journalist = page.find('meta', attrs={{'name':'author'}})['content']
        return journalist

    def get_publish_date(self, page):
        if page.find('meta', attrs={{'property': 'article:published_time'}}):
            date = page.find('meta', attrs={{'property': 'article:published_time'}})['content']
        else :
            date = page.find('time', class_='post-published')['datetime']
        date = parser.parse(date).replace(tzinfo=None)
        return date
    
    def get_thumbnail(self, page):
        image = page.find('meta', attrs={{'property':'og:image'}})['content']
        return image

    def get_content(self, page):
        paragraphs = page.find('div', class_ = 'entry-content').find_all('p')

        content = ''
        for p in paragraphs:
            if('baca juga:' in p.text.lower()):
                continue

            content += p.text + "\n\n"

        return content

    def request(self, url, params=None, **kwargs):
        allow_redirects = kwargs.pop('allow_redirects', True)
        scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
        max_retries = 3
        retries = 0
        page = None
        while retries < max_retries:
            try :
                ## Pakai Proxy
                get_proxy = proxy_get()
                if get_proxy is not None:
                    print(f"Proxy  : {{get_proxy.partition('@')[2]}}")
                    proxies = {{
                        "https": "socks5://"+ get_proxy,
                        "http": "socks5://"+ get_proxy,
                    }}
                    # page = scraper.get(url,  proxies=proxies,  headers=headers, params=params, allow_redirects=allow_redirects)
                    page = requests.get(url, proxies=proxies, params=params, headers=headers)
                    if page.status_code != 200:
                        print('Gagal Pakai Proxy', str(page.status_code))
                        print("Retrying...")
                        retries += 1
                        logs_ ={{
                            "url": url, 
                            "proxy": get_proxy.partition('@')[2].partition(':')[0],
                            "port": get_proxy.partition('@')[2].partition(':')[2],
                            "message": "Gagal pakai Proxy Status Code:" + str(page.status_code),
                            "status": "Failed"
                            }}
                        self.logs_proxy.insert_one(logs_)
                        continue
                    logs_ ={{
                        "url": url, 
                        "proxy": get_proxy.partition('@')[2].partition(':')[0],
                        "port": get_proxy.partition('@')[2].partition(':')[2],
                        "status": "Success"
                        }}
                    self.logs_proxy.insert_one(logs_)
                    break
                ## Tidak pakai Proxy
                else:
                    print('Proxy Tidak Ada')
                    page = scraper.get(url, params=params, headers=headers, allow_redirects=allow_redirects)
                    break
            except (requests.exceptions.ConnectionError, requests.exceptions.TooManyRedirects, BaseException) as e:
                if get_proxy == None:
                    return page
                else:
                    logs_ = {{
                        "url": url,
                        "proxy": get_proxy.partition('@')[2].partition(':')[0],
                        "port": get_proxy.partition('@')[2].partition(':')[2],
                        "message": "Gagal pakai Proxy: " + str(e),
                        "status": "Failed"
                    }}
                    self.logs_proxy.insert_one(logs_)
                    print(e)
                    retries += 1
                    print("Retrying...")
                    continue
        return(page)

    def parse_page(self, url, params=None, headers=None):
        print(url)
        try :
            page = self.request(url, params=params)
            if page is None or page.status_code != 200:
                print("pe")
                scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
                page = scraper.get(url, headers=headers)
                if page.status_code != 200:
                    print("Error : Gagal mengambil berita karena website berstatus", str(page.status_code))
                    return self.counter
        except requests.exceptions.ConnectionError:
            crawler.logs.update_one({{'_id': ObjectId(logs['id'])}}, {{'$set': {{'end': datetime.now(), 'count': 0, 'duration': (datetime.now()-logs['start']).total_seconds(), 'status': 'Unavailable',  'error_message': "Site can’t be reached"}}}})
            print("Error : Gagal mengambil berita karena website down")
            exit()
        soup = BeautifulSoup(page.text, "html.parser")

        if soup.find('h2', class_='h2 jl_fe_title'):
            articles = soup.findAll('h2', class_='h2 jl_fe_title')
        else:
            crawler.logs.update_one({{'_id': ObjectId(logs['id'])}}, {{'$set': {{'end': datetime.now(), 'count': 0, 'duration': (datetime.now()-logs['start']).total_seconds(), 'status': 'MissingClass',  'error_message': 'Element not found'}}}})
            print("Error : Gagal menemukan element")
            exit()
        all_urls = []
        for article in articles:
            a_tag = article.find('a')
            if a_tag and 'href' in a_tag.attrs:
                url = a_tag['href']
                all_urls.append(url)

        
        existing_docs = self.streams.find({{'origin_url': {{'$in': all_urls}}}}, {{'origin_url': 1}})
        existing_urls = set(doc['origin_url'] for doc in existing_docs)

        new_articles = []
        for a in articles:
            a_tag = a.find('a')
            if a_tag and 'href' in a_tag.attrs:
                href_url = a_tag['href']
                if href_url not in existing_urls:
                    new_articles.append(a)

        bulk_operations = []
        print("Total articles: {{}}".format(len(all_urls)))
        if new_articles:
            for article in new_articles:
                try:
                    url = article.a['href']
                    print(url)

                    try :
                        article_detail = self.request(url, params=params)
                        if article_detail is None or article_detail.status_code != 200:
                            print('Failed to use Proxy')
                            scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
                            article_detail = scraper.get(url, headers=headers)
                            if article_detail.status_code != 200:
                                print('Error: ' + str(article_detail.status_code))
                                print('URL: ' + url)
                                continue
                    except requests.exceptions.ConnectionError:
                        print("Error : Gagal mengambil berita karena halaman berita down")
                        continue
                    page = BeautifulSoup(article_detail.text, 'html.parser')

                    # get publish date 
                    date = self.get_publish_date(page)
                    # get title
                    title = self.get_title(page)
                    # get journalist
                    journalist = self.get_journalist(page)
                    # get thumbnail
                    thumbnail = self.get_thumbnail(page)
                    # get content
                    content = self.get_content(page)

                    account = urlparse(url).netloc.replace('www.', '')

                    # build meta dict for insert to db
                    meta = {{}}
                    meta['id_account'] = account
                    meta['date'] = date
                    meta['title'] = title
                    meta['content'] = content # str(content.encode('utf-8').decode('unicode_escape'))
                    meta['account'] = account
                    meta['journalist'] = journalist
                    meta['url'] = url
                    meta['origin_url'] = url
                    meta['source'] = 'news'
                    meta['portal'] = '(nama domain)'
                    meta['category'] = 'Straight News'
                    meta['timestamp'] = datetime.now()
                    meta['updated_at'] =datetime.now()
                    meta['thumbnail'] = thumbnail

                    # print(meta)
                    bulk_operations.append(
                        UpdateOne(
                            {{'origin_url': url}},  # filter key unik
                            {{'$set': meta}},# data untuk update/insert
                            upsert=True
                        )
                    )
                except Exception as e:
                    print(url)
                    print(str(e))
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    error ={{
                        'url' :url,
                        'error': str(e),
                        'type':str(exc_type),
                        'line': str(exc_tb)
                    }}
                    ## error di tampung 
                    array_error.append(error)
                    continue
                
            if bulk_operations:
                try:
                    result = self.streams.bulk_write(bulk_operations, ordered=False)
                    inserted_count = result.upserted_count
                    self.counter += inserted_count

                    print(f"\n✅ Inserted {{inserted_count}} new article(s):")
                    for index in result.upserted_ids:
                        op = bulk_operations[index]
                        print("📰", op._filter.get("origin_url"))

                except errors.BulkWriteError as bwe:
                    print("Bulk upsert error:", bwe.details)
            else:
                print("Tidak ada data baru untuk di-upsert.")
            ## hasil error yang di tampung masukan ke method
            if len(array_error) > 0:
                self.log_error.append(array_error)
        return self.counter

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print("Close Database Connection...")
        print("Ended at: {{}}".format(datetime.now(self.IST)))
        self.ConnectionDB.DisconnectDatabase()
        print("----------- Crawler Run %f seconds -----------" %(time.time() - self.StartTime))

if __name__ == '__main__':

    with (nama domain)() as crawler:
        logs = crawler.insert_log()
        ## Update File name Scraper
        file_name = os.path.basename(__file__)
        crawler.scraper.update_one(
            {{'_id':logs['scraper_name']}},
            {{'$set': {{'file_name': file_name}}}}
        )
        ## End
        try:
            base_url = "https://(nama domain)/?s=+"
            total_data = crawler.parse_page(base_url)

            ## cek method log error ada tidak
            if len(crawler.log_error) > 0:
                crawler.logs.update_one({{'_id': ObjectId(logs['id'])}}, {{'$set': {{'end': datetime.now(), 'count': total_data, 'duration': (datetime.now()-logs['start']).total_seconds(), 'status': 'Error','error_message':crawler.log_error[0]}}}})
            else:
                crawler.logs.update_one({{'_id': ObjectId(logs['id'])}}, {{'$set': {{'end': datetime.now(), 'count': total_data, 'duration': (datetime.now()-logs['start']).total_seconds(), 'status': 'Completed'}}}})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(str(e), exc_type, fname, exc_tb.tb_lineno)
            crawler.logs.update_one({{'_id': ObjectId(logs['id'])}}, {{'$set': {{'end': datetime.now(), 'count': 0, 'duration': (datetime.now()-logs['start']).total_seconds(), 'status': 'Error',  'error_message': (str(e) + ' Line : ' + str(exc_tb.tb_lineno) + ' ' + str(exc_type))}}}})

"""