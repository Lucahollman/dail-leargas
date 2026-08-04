import requests
import json

# Date you want to fetch
date = "2026-01-21" 

# API request
response = requests.get(
    "https://api.oireachtas.ie/v1/debates",
    params={
        "chamber": "dail",
        "date_start": date,
        "date_end": date,
        "limit": 50
    }
)

# Check request succeeded
response.raise_for_status()

# Convert to JSON
data = response.json()

# Save JSON file
with open(f"debates_{date}.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"Saved debates for {date}")