from flask import Flask, redirect
from dash_app import create_dash_app

from Database.models import create_table
from src.main import start_collection, stop_collection

# Initialize Flask app
proj = Flask(__name__)

# Mount Dash app onto Flask
dash_app = create_dash_app(proj)

# Route: Root → Redirect to dashboard (Graphs page by default)

@proj.route('/')
def dashboard():
    return redirect('/dashboard/')

# Route: Create database tables
@proj.route('/initdb')
def initdb():
    try:
        create_table()
        return "✅ Database and tables created successfully!"
    except Exception as e:
        return f"❌ Error: {e}"

# Custom CLI command to initialize DB
@proj.cli.command("db-load")
def db_load():
    """Create tables in the database."""
    create_table()
    print("✅ Database tables created successfully!")

# Route: Placeholder for raw data viewing (can enhance later)
@proj.route('/showdata')
def showdata():
    return "📊 Data will display here"

# Route: Start data collection (uses dummy or real input)
@proj.route('/startCollection')
def startCollection():
    start_collection("GEC", 7.123, 3.456)  # Update with dynamic params if needed
    return "🚀 Data Collection Started"

# Route: Stop data collection
@proj.route('/stopCollection')
def stopCollection():
    stop_collection()
    return "🛑 Data Collection Stopped"

# Main entry point
if __name__ == "__main__":
    proj.run(debug=True)