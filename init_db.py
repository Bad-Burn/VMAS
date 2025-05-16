import mysql.connector
from db_config import get_db_connection
import os

def init_database():
    # First, create database and tables
    try:
        # Initial connection to MySQL server without database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            print("Connected to MySQL server")
            cursor = connection.cursor()

            # Create database first
            cursor.execute("CREATE DATABASE IF NOT EXISTS vmas")
            cursor.execute("USE vmas")
            print("Created and switched to vmas database")

            # Read the SQL script
            with open('database.sql', 'r') as file:
                sql_script = file.read()
            
            # Execute each command separately
            current_command = ''
            for line in sql_script.split('\n'):
                line = line.strip()
                
                # Skip comments and empty lines
                if line.startswith('--') or not line:
                    continue
                    
                current_command += line + ' '
                
                if line.endswith(';'):
                    try:
                        print(f"Executing: {current_command}")
                        cursor.execute(current_command)
                        connection.commit()
                    except Exception as e:
                        print(f"Error executing command: {e}")
                    current_command = ''

            print("Database and tables created successfully!")

            # Test the connection to the new database
            test_conn = get_db_connection()
            if test_conn:
                print("Successfully connected to VMAS database")
                test_conn.close()
                print("Database initialization complete!")
            else:
                print("Failed to connect to VMAS database after creation")
            
    except mysql.connector.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    init_database()
