import argparse
from datetime import datetime
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
import os
import pprint
import requests

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
MONGO_URI = f"mongodb://localhost:27017/"
STREAM_COLLECTION = "streams"
MEDIA_COLLECTION = "media"
API_URL = "https://scsv.onlinemonitoring.id/media/onlinenews/detail"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VySWQiLCJleHAiOjE2OTkwMTg0MDB9.rX1P5UuD7yGpSR2yht3PU6wLi5MekjsFUpbRkIkD6co"

def fetch_api_data(id_account):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }
    params = {
        "name": id_account
    }
    try:
        response = requests.get(API_URL, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('data')
        else:
            print(f"Gagal fetch untuk {id_account}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception saat fetch API untuk {id_account}: {e}")
        return None

def main(start_date, end_date, update_media=True, update_stream=True, dry_run=False):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    stream = db[STREAM_COLLECTION]
    media = db[MEDIA_COLLECTION]

    if update_media:
        updates = []
        for doc in media.find({}, {"_id": 1, "id_account": 1, "province": 1, "tier": 1}):
            id_account = doc.get("id_account")
            if not id_account:
                continue

            api_data = fetch_api_data(id_account)
            if not api_data:
                continue

            new_province = api_data.get("provinsi")
            new_tier = api_data.get("tier")

            if new_province is None:
                print(f"Provinsi None untuk {id_account}, lewati update.")
                continue

            if new_province != doc.get("province") or new_tier != doc.get("tier"):
                print(f"Akan update {id_account}:")
                print(f" - Province: {doc.get('province')} -> {new_province}")
                print(f" - Tier    : {doc.get('tier')} -> {new_tier}")

                update_doc = {
                    "province": new_province,
                    "tier": new_tier,
                    "updated_at": datetime.now()
                }
                updates.append(
                    UpdateOne({"_id": doc["_id"]}, {"$set": update_doc})
                )
            else:
                print(f"Tidak ada perubahan untuk {id_account}")

        if updates:
            if dry_run:
                print(f"[DRY RUN] {len(updates)} dokumen akan diupdate.")
            else:
                result = media.bulk_write(updates)
                print(f"{result.modified_count} dokumen berhasil diupdate.")
        else:
            print("Tidak ada dokumen yang perlu diupdate.")

    if update_stream:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        query = {
            "timestamp": {
                "$gte": start_dt,
                "$lte": end_dt
            }
        }

        accounts = stream.find(query)
        operations = []
        update_preview = []

        for account in accounts:
            account_id = account.get("id_account")
            province = account.get("province")
            tier = account.get("tier")

            if province and tier:
                continue

            media_data = media.find_one({"id_account": account_id})
            if not media_data:
                continue

            media_province = media_data.get("province")
            media_tier = media_data.get("tier")

            if media_province == "" or media_tier == "":
                continue

            update_fields = {}
            if not province and media_province:
                update_fields["province"] = media_province
            if not tier and media_tier:
                update_fields["tier"] = media_tier

            if update_fields:
                update_data = {
                    "_id": str(account["_id"]),
                    "id_account": account_id,
                    "update_fields": update_fields
                }

                if dry_run:
                    update_preview.append(update_data)
                else:
                    print("[UPDATE] Akan mengupdate dokumen:")
                    pprint.pprint(update_data)
                    operations.append(
                        UpdateOne(
                            {"_id": account["_id"]},
                            {"$set": update_fields}
                        )
                    )

        if dry_run:
            print(f"[DRY RUN] Rencana update: {len(update_preview)} dokumen")
            for item in update_preview:
                pprint.pprint(item)
        else:
            if operations:
                result = stream.bulk_write(operations)
                print(f"Selesai! {result.modified_count} dokumen berhasil diperbarui.")
            else:
                print("Tidak ada dokumen yang perlu diperbarui.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update data province & tier dari media dan stream")

    parser.add_argument("--start-date", type=str, required=True, help="Tanggal mulai (format: YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, required=True, help="Tanggal akhir (format: YYYY-MM-DD)")
    
    parser.add_argument("--update-media", dest="update_media", action="store_true", help="Lakukan update pada koleksi media")
    parser.add_argument("--update-stream", dest="update_stream", action="store_true", help="Lakukan update pada koleksi stream")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="Simulasikan perubahan tanpa menyimpan ke DB")

    args = parser.parse_args()
    
    if not args.update_media and not args.update_stream:
        args.update_media = True
        args.update_stream = True

    print("=== ARGUMENTS ===")
    print(f"Start Date   : {args.start_date}")
    print(f"End Date     : {args.end_date}")
    print(f"Update Media : {args.update_media}")
    print(f"Update Stream: {args.update_stream}")
    print(f"Dry Run      : {args.dry_run}")
    print("=================")

    main(
        start_date=args.start_date,
        end_date=args.end_date,
        update_media=args.update_media,
        update_stream=args.update_stream,
        dry_run=args.dry_run
    )