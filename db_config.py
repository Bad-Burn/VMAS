import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vmas',
            port=3306  # Default XAMPP MySQL port
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None
