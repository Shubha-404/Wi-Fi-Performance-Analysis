import speedtest
import time
import subprocess
import re
import json
from datetime import datetime
from threading import Event
from Database.database import get_db_connection

stop_event = Event()

# Function to get WiFi RSSI on Windows using netsh
def get_rssi():
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True)
        match = re.search(r"Signal\s+:\s+(\d+)", result.stdout)
        return int(match.group(1)) if match else None
    except Exception as e:
        print(f"Error getting RSSI: {e}")
        return None

# Function to get packet loss, jitter, and latency using ping
def get_ping_stats():
    try:
        result = subprocess.run(['ping', '-n', '10', '8.8.8.8'], capture_output=True, text=True)
        output = result.stdout
        match_loss = re.search(r"(\d+)% packet loss", output)
        packet_loss = float(match_loss.group(1)) if match_loss else 0.0
        match_latency = re.search(r"Average = (\d+)ms", output)
        latency = float(match_latency.group(1)) if match_latency else 0.0
        jitter = 0.0  # Jitter estimation not available in ping
        return latency, jitter, packet_loss
    except Exception as e:
        print(f"Error getting ping stats: {e}")
        return None, None, None

# Function to get download and upload speeds using speedtest-cli
def get_speed():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1e6  # Mbps
        upload_speed = st.upload() / 1e6  # Mbps
        return download_speed, upload_speed
    except Exception as e:
        print(f"Error getting speed: {e}")
        return None, None

# Function to write data to a JSON file
def write_to_json_file(data, location, filename=r"data/wifi_data.json"):
    try:
        try:
            with open(filename, 'r') as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {}
        
        if location not in existing_data:
            existing_data[location] = []
        existing_data[location].append(data)
        
        with open(filename, 'w') as f:
            json.dump(existing_data, f, indent=4)
    except Exception as e:
        print(f"Error writing to JSON file: {e}")

# Function to store data in MySQL
def store_data_in_db(location_name, position_x, position_y, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO positions (position_name, position_x, position_y)
            VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE position_x = %s, position_y = %s
        """, (location_name, position_x, position_y, position_x, position_y))
        
        cursor.execute("""
            INSERT INTO wifi_data (timestamp, position_name, download_speed, upload_speed, latency_ms, jitter_ms, packet_loss, rssi)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (data['timestamp'], location_name, data['download_speed'], data['upload_speed'], data['latency_ms'], data['jitter_ms'], data['packet_loss'], data['rssi']))
        
        conn.commit()
    except Exception as e:
        print(f"Error storing data in database: {e}")
    finally:
        cursor.close()
        conn.close()

# Main function to collect and store WiFi data
def collect_and_store_data(location_name, position_x, position_y):
    stop_event.clear()
    while not stop_event.is_set():
        download_speed, upload_speed = get_speed()
        latency, jitter, packet_loss = get_ping_stats()
        rssi = get_rssi()
        
        if download_speed is not None and upload_speed is not None and latency is not None:
            data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "download_speed": download_speed,
                "upload_speed": upload_speed,
                "latency_ms": latency,
                "jitter_ms": jitter,
                "packet_loss": packet_loss,
                "rssi": rssi
            }
            write_to_json_file(data, location_name)
            store_data_in_db(location_name, position_x, position_y, data)
            print(f"Data saved at {datetime.now()} for {location_name}")
        
        time.sleep(60)

def start_collection(location_name, position_x, position_y):
    print("Data collection started.")
    collect_and_store_data(location_name, position_x, position_y)

def stop_collection():
    stop_event.set()
    print("Data collection stopped.")

# if __name__ == "__main__":
#     start_collection("ECC", 67.123, -43.456)
