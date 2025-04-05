from database import get_db_connection

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS wifi_analysis")

    # Create 'positions' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            position_name VARCHAR(100) PRIMARY KEY,
            position_x FLOAT,
            position_y FLOAT
        )
    """)

    # Create 'wifi_data' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wifi_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME,
            position_name VARCHAR(100),
            download_speed FLOAT,
            upload_speed FLOAT,
            latency_ms FLOAT,
            jitter_ms FLOAT,
            packet_loss FLOAT,
            rssi INT,
            FOREIGN KEY (position_name) REFERENCES positions(position_name) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

