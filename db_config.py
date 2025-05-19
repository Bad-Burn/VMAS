from flask_sqlalchemy import SQLAlchemy
from models.db import db
import os
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vmas_dev'  # Always use vmas_dev for development
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

def init_db(app, environment='development'):
    # Get the environment from environment variable or use default
    env = os.getenv('FLASK_ENV', environment)
    
    # Import and apply config
    from config import config
    app.config.from_object(config[env])
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Create all tables
    with app.app_context():
        db.create_all()
