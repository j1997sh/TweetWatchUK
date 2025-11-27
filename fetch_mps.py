import requests, json, os

API_KEY = "YOUR_TWFY_KEY"

url=f"https://www.theyworkforyou.com/api/getMPs?key={API_KEY}&output=js"
data=requests.get(url).json()

os.makedirs("data", exist_ok=True)
with open("data/mps.json","w") as f:
    json.dump(data,f,indent=2)
