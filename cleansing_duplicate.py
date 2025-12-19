from pymongo import MongoClient

# Koneksi ke MongoDB
client = MongoClient("mongodb://onlinenews_datalake:Kabayan2020@15.235.164.126:3001/?authSource=onlinenews_datalake&directConnection=true")  # Ganti sesuai koneksi Anda
db = client["onlinenews_datalake"]  # Ganti sesuai nama database Anda
collection = db["streams"]  # Ganti dengan nama koleksi Anda

# Step 1: Cari duplikat title pada portal "Betahita"
pipeline = [
    {"$match": {"portal": "ipotnews"}},
    {"$group": {
        "_id": "$title",
        "count": {"$sum": 1},
        "ids": {"$push": "$_id"}
    }},
    {"$match": {"count": {"$gt": 1}}}
]

duplicates = collection.aggregate(pipeline)

# Step 2: Tampilkan dan hapus duplikat
total_deleted = 0
for dup in duplicates:
    title = dup["_id"]
    ids = dup["ids"]
    to_delete = ids[1:]  # Sisakan satu

    print(f"\nDuplikat ditemukan untuk title: '{title}'")
    print(f"Total duplikat: {len(ids)} - Menghapus {len(to_delete)} dokumen")

    result = collection.delete_many({"_id": {"$in": to_delete}})
    total_deleted += result.deleted_count

print(f"\n✅ Total dokumen duplikat yang dihapus: {total_deleted}")
