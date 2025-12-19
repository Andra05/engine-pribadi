import os
import json
import re

def find_timedelta_occurrences(directories, search_text):
    total_files = 0
    scraper_names = []
    pattern = re.compile(r"logs\['scraper_name'\]\s*=\s*'([^']+)'")
    
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            if search_text in content:
                                total_files += 1
                                match = pattern.search(content)
                                if match:
                                    scraper_names.append(match.group(1))
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
    
    return total_files, scraper_names

if __name__ == "__main__":
    directories = [
        "/home/andra/Documents/Kerjaan/online-news-scraper/Fisik",
        "/home/andra/Documents/Kerjaan/online-news-scraper/onsite-sc01",
        "/home/andra/Documents/Kerjaan/online-news-scraper/VM 1",
        "/home/andra/Documents/Kerjaan/online-news-scraper/VM 2",
        "/home/andra/Documents/Kerjaan/online-news-scraper/VM 3",
    ]
    search_text = "+ timedelta(hours=7)"
    
    total_files, scraper_names = find_timedelta_occurrences(directories, search_text)
    
    result = {
        "total": total_files,
        "scraper_names": scraper_names
    }
    
    print(json.dumps(result, indent=4))