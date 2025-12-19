from pymongo import MongoClient, DeleteOne
from datetime import datetime
import time

# 🔧 Ganti sesuai koneksi Mongo kamu
client = MongoClient("mongodb://onlinenews_datalake:Kabayan2020@15.235.164.126:3001/?authSource=onlinenews_datalake&directConnection=true")
db = client["onlinenews_datalake"]   # nama database
collection = db["streams"]           # ganti dengan nama koleksi

start_time = time.time()
print(f"🚀 Script started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

start = datetime(2025, 9, 18, 0, 0, 0)
end = datetime(2025, 9, 18, 23, 59, 59)

pipeline = [
    {
        "$match": {
            "timestamp": {"$gte": start, "$lte": end}
        }
    },
    {
        "$project": {
            "cleanUrl": {
                "$replaceOne": {
                    "input": "$url",
                    "find": "://www.",
                    "replacement": "://"
                }
            },
            "originalUrl": "$url"
        }
    },
    {
        "$group": {
            "_id": "$cleanUrl",
            "count": {"$sum": 1},
            "docs": {"$push": {"id": "$_id", "url": "$originalUrl"}}
        }
    },
    {
        "$match": {"count": {"$gt": 1}}
    }
]

duplicates = list(collection.aggregate(pipeline))

duplicate_groups = len(duplicates)     # jumlah grup cleanUrl duplikat
duplicate_docs = sum(len(g["docs"]) for g in duplicates)  
print(f"Duplicate groups   : {duplicate_groups}")
print(f"Duplicate documents: {duplicate_docs}")
bulk_ops = []

for group in duplicates:
    print(f"\n🔗 Duplicate group: {group['_id']} (count={group['count']})")
    for doc in group["docs"]:
        if "://www." in doc["url"]:
            print(f"   🗑️ Marked for delete: {doc['url']} ({doc['id']})")
            bulk_ops.append(DeleteOne({"_id": doc["id"]}))
        else:
            print(f"   ✅ Keep: {doc['url']} ({doc['id']})")

if bulk_ops:
    result = collection.bulk_write(bulk_ops)
    print("\n📊 Summary")
    print(f"Duplicate groups   : {duplicate_groups}")
    print(f"Duplicate documents: {duplicate_docs}")
    print(f"Deleted documents  : {result.deleted_count}")
else:
    print("Tidak ada duplikat dengan 'www.' yang perlu dihapus.")

end_time = time.time()
duration = end_time - start_time
print(f"\n🏁 Script ended at : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"⏱️ Duration        : {duration:.2f} seconds")
