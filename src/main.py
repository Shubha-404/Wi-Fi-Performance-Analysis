import speedtest
import time
import subprocess
import re
from datetime import datetime

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

