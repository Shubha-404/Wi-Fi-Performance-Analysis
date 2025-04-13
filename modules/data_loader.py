import pandas as pd
import json
from datetime import datetime
from .utils import get_pixel_coords
import os

def load_wifi_data():
    try:
        
        json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'wifi_data.json')
        with open(json_path, 'r') as file:
            data = json.load(file)

        records = []
        for location, measurements in data.items():
            for measurement in measurements:
                try:
                    timestamp = datetime.strptime(measurement['timestamp'], '%Y-%m-%d %H:%M:%S')
                    record = {
                        'timestamp': timestamp,
                        'date': timestamp.strftime('%Y-%m-%d'),
                        'hour': timestamp.strftime('%H:00'),
                        'location': measurement['location']['position[name]'],
                        'download_speed': measurement['download_speed'],
                        'upload_speed': measurement['upload_speed'],
                        'latency_ms': measurement['latency_ms'],
                        'jitter_ms': measurement['jitter_ms'],
                        'packet_loss': measurement['packet_loss'],
                        'rssi': measurement['rssi']
                    }
                    records.append(record)
                except Exception as e:
                    print(f"⚠️ Skipping bad record: {e}")
                    continue

        df = pd.DataFrame(records)
        return df
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return pd.DataFrame()

def prepare_heatmap_data(df, selected_param):
    df = df.copy()
    df['x'], df['y'] = zip(*df['location'].map(get_pixel_coords))
    df = df.dropna(subset=[selected_param, 'x', 'y'])
    return df[['x', 'y', selected_param, 'location']]
