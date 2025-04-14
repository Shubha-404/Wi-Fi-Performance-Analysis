1. Create a virtual environment inside the "WIFI-PERFORMANCE-ANALYSIS" folder -> "python -m venv .venv"
2. activate it -> ".venv/Scripts/activate" (for windows)
            if error is there then run "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser" then activate again
3. install dependencies -> "pip install -r requirements.txt"
4. in config.py -> change password & database 
                i.e 
                "password": "password",
                "database": "db_name"
5. load the database -> "flask db-load"
6. run the app -> "flask run"

7. if missed the 5th point then go to route "/initdb "to load the db
