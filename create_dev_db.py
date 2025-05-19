import mysql.connector
from mysql.connector import Error

def create_development_database():
    try:
        # Connect to MySQL server without selecting a database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            port=3306
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create new database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS vmas_dev")
            print("Database 'vmas_dev' created successfully")
            
            # Switch to the new database
            cursor.execute("USE vmas_dev")
            
            # Read and execute the SQL script
            with open('database.sql', 'r') as file:
                sql_script = file.read()
                # Split the script into individual statements
                statements = sql_script.split(';')
                
                for statement in statements:
                    if statement.strip():
                        cursor.execute(statement + ';')
                        connection.commit()
            
            print("Development database tables created successfully")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    create_development_database()
