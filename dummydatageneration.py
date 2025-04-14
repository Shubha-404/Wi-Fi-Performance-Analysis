import random
import json
from datetime import datetime, timedelta

# Define locations and their coordinates
locations = {
    "ECC": (67.12, -43.45),
    "GEC": (70.21, -40.31),
    "SDB": (65.78, -42.50),
    "FOODCOURT": (68.33, -41.25),
    "LOUNGE": (69.0, -39.9)
}

# Time range and interval
start_time = datetime(2025, 4, 5, 8, 0)
end_time = datetime(2025, 4, 8, 18, 0)
interval = timedelta(minutes=5)

# Container for final dataset
wifi_data = []

# Loop through each location
for loc_name, (x, y) in locations.items():
    records = []
    timestamp = start_time
    run_no = 1
    while timestamp <= end_time:
        record = {
            "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "location": {
                "position[name]": loc_name,
                "position[x]": x,
                "position[y]": y
            },
            "download_speed": round(random.uniform(10, 100), 10),
            "upload_speed": round(random.uniform(4, 50), 10),
            "latency_ms": random.randint(30, 120),
            "jitter_ms": 0,
            "packet_loss": 0,
            "rssi": 100,
            "run_no": run_no
        }
        records.append(record)
        run_no += 1
        timestamp += interval

    wifi_data.append({loc_name: records})

# Save to JSON
with open("data/dummy_wifi_data.json", "w") as f:
    json.dump(wifi_data, f, indent=2)

print("✅ Large dataset written to data/large_wifi_data.json")
