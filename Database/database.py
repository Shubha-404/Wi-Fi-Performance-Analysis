from pymongo import MongoClient
from Database.config import DB_CONFIG

def get_db_connection():
    client = MongoClient(DB_CONFIG["host"], DB_CONFIG["port"])
    db = client[DB_CONFIG["database"]]
    return db
