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

# Time range: April 5 to April 8, 2025
start_date = datetime(2025, 4, 5, 8, 0)
end_date = datetime(2025, 4, 8, 18, 0)
interval = timedelta(minutes=15)

wifi_data = {}

# Generate data
for loc_name, (x, y) in locations.items():
    wifi_data[loc_name] = []
    timestamp = start_date
    while timestamp <= end_date:
        measurement = {
            "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "location": {
                "position[x]": x,
                "position[y]": y,
                "position[name]": loc_name
            },
            "download_speed": round(random.uniform(30, 100), 3),
            "upload_speed": round(random.uniform(10, 50), 3),
            "latency_ms": round(random.uniform(30, 100), 1),
            "jitter_ms": round(random.uniform(0.1, 5.0), 1),
            "packet_loss": round(random.uniform(0.0, 0.5), 2),
            "rssi": random.randint(70, 100)
        }
        wifi_data[loc_name].append(measurement)
        timestamp += interval

# Save to your existing data file path
with open("data/wifi_data.json", "w") as f:
    json.dump(wifi_data, f, indent=4)

print("✅ Dummy data written to data/wifi_data.json")
