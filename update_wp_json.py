import paramiko
from pymongo import MongoClient

# === KONFIGURASI SSH ===
ssh_config = {
    "hostname": "127.0.0.1",       # Ganti jika remote server
    "port": 29017,                    # Port SSH (default 22)
    "username": "monscrap",   # Ganti dengan username SSH
    "password": "Kabayan2020"    # Ganti dengan password SSH
}

# === KONFIGURASI MONGODB ===
mongo_uri = "mongodb://monscrap:Kabayan2020@127.0.0.1:29017/?authSource=monscrap&directConnection=true"
database_name = "proxy"
collection_name = "media_wordpress"
document_id = "combined_files_20250526_155642"

# === DOMAIN LIST ===
domains = [
    "aksarakaltim.id", "Akurasi.id", "Bekesah.co", "Bentangkaltim.com",
    "dialektis.co", "digtalpos.com", "editorialkaltim.com", "expresi.co",
    "Inspirasa.co", "kabarintens.com", "katakaltim.com", "kitamudamedia.com",
    "Klausa.co", "longtime.id", "mediakaltim.com", "Narasipedia.net",
    "Nius.id", "Paradase.id", "pktvkaltim.com", "Potretkata.co",
    "Pranala.co", "radarbontang.com", "Rimbanusa.id", "tekstual.com", "timurmedia.com"
]

# === SSH & MONGO EXECUTION ===
def ssh_and_update_mongo():
    try:
        # SSH Connection
        print("🔐 Connecting via SSH...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=ssh_config['hostname'],
            port=ssh_config['port'],
            username=ssh_config['username'],
            password=ssh_config['password']
        )

        # Check MongoDB status
        print("🧪 Testing MongoDB connection via SSH...")
        stdin, stdout, stderr = ssh.exec_command("mongo --port 29017 --eval 'db.runCommand({ ping: 1 })'")
        print("MongoDB output:")
        for line in stdout:
            print(line.strip())
        for line in stderr:
            print(line.strip())

        ssh.close()
        print("✅ SSH and MongoDB check successful.\n")

        # Connect to MongoDB with pymongo
        print("🔗 Connecting to MongoDB via pymongo...")
        client = MongoClient(mongo_uri)
        db = client[database_name]
        collection = db[collection_name]

        # Prepare data
        swp_json_25 = [
            {
                "_id": domain.lower(),
                "url": f"https://{domain.lower()}/wp-json/wp/v2/posts?_embed&per_page="
            } for domain in domains
        ]

        # Update the document
        print("📦 Updating MongoDB document...")
        result = collection.update_one(
            {"_id": document_id},
            {"$push": {"data.SWP_json_25": {"$each": swp_json_25}}}
        )

        if result.modified_count > 0:
            print("✅ Data berhasil ditambahkan ke SWP_json_25.")
        else:
            print("⚠️  Dokumen tidak ditemukan atau tidak diperbarui.")

    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")

# === EKSEKUSI ===
if __name__ == "__main__":
    ssh_and_update_mongo()
