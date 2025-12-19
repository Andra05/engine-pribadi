import requests

url = "https://scsv.onlinemonitoring.id/media/onlinenews/detail"
params = {
    "name": "klikpendidikan.id"
}

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VySWQiLCJleHAiOjE2OTkwMTg0MDB9.rX1P5UuD7yGpSR2yht3PU6wLi5MekjsFUpbRkIkD6co"
}

response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error {response.status_code}: {response.text}")