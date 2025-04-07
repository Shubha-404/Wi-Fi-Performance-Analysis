from flask import Flask
from Database.models import create_table
from src.main import start_collection, stop_collection

proj = Flask(__name__)

@proj.route('/')
def index():
    return "Welcome to Wi-Fi Performance Analysis"

@proj.route('/initdb')
def initdb():
    try:
        create_table()
        return "Database and tables created successfully!"
    except Exception as e:
        return f"Error: {e}"
    
# Custom command to load the database
@proj.cli.command("db-load")
def db_load():
    """Create tables in the database."""
    create_table()
    print("Database tables created successfully!")

@proj.route('/showdata')
def showdata():
    return "Data will display here"

@proj.route('/startCollection')
def startCollection():
    start_collection("GEC", 7.123, 3.456)
    return "Data Collection Started"

@proj.route('/stopCollection')
def stopCollection():
    stop_collection()
    return "Data Collection Stopped"

if __name__ == "__main__":
    proj.run(debug=True)  # Enable debug mode
