import requests
import json

fp = "cosmetics_cache.json"

resp = requests.get("https://fortnite-api.com/v2/cosmetics/br")
data = resp.json()

with open(fp, "w") as f:
    json.dump(data, f, indent=4)

print("Cached API")
