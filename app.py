import os                               # this line should go at the top of your file
# cd c:/Utils/Python/Codecademy/"Build Python Web Apps with Flask"/"Build Python Web Apps with Flask Capstone Project"
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

database = "my_idea_box.db"
app = Flask(__name__)
#app.secret_key = os.getenv("APP_SECRET_KEY")
app.secret_key = "my_secret_key"
"""
When we added PostgreSQL to our heroku project, it automatically created that DATABASE_URL environment variable for us. So when our code is run on Heroku, os.environ['DATABASE_URL'] should automatically point to the PostgreSQL database.
"""
DATABASE_URL = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or f"sqlite:///{database}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ------- Managing logged in state -------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # The name of the view to redirect to when the user needs to log in. 

import routes, models


# Initializing the database
if not DATABASE_URL and not os.path.exists(database):
    # initilize SQLite database on localhost:
    print("Initialize database...")
    db.create_all()