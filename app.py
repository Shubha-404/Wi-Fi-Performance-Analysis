from flask import Flask, redirect
from dash_app import create_dash_app

app = Flask(__name__)

# Initialize Dash app
dash_app = create_dash_app(app)

@app.route('/')
def index():
    return redirect('/dashboard/')

@app.route('/showdata')
def showdata():
    return "Data will display here"

if __name__ == "__main__":
    app.run(debug=True)  # Enable debug mode