from pymongo import MongoClient
from datetime import datetime

# Koneksi ke MongoDB
client = MongoClient("mongodb://onlinenews_datalake:Kabayan2020@15.235.164.126:3001/?authSource=onlinenews_datalake&directConnection=true")
db = client["onlinenews_datalake"]
collection = db["streams"] 

# Query Aggregation
pipeline = [
    {
        "$match": {
            "portal": {
                "$in": ["Bidiknasional", "suarabanyuurip", "Japantimes"]
            },
            "timestamp": {
                "$gte": datetime(2025, 1, 1)
            }
        }
    },
    {
        "$match": {
            "$expr": {"$gt": ["$date", "$timestamp"]}
        }
    },
    {
        "$count": "total_documents"
    }
]

# Menjalankan query
result = list(collection.aggregate(pipeline))

# Menampilkan jumlah dokumen yang ditemukan
if result:
    print(f"Total dokumen yang sesuai: {result[0]['total_documents']}")
else:
    print("Tidak ada dokumen yang sesuai.")