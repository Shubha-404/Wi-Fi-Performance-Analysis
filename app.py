from flask import Flask
from models import create_table

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

@proj.route('/showdata')
def showdata():
    return "Data will display here"

if __name__ == "__main__":
    proj.run(debug=True)  # Enable debug mode