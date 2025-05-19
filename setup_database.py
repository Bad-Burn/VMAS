import mysql.connector
from mysql.connector import Error

def setup_databases():
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
            
            # Create databases if they don't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS vmas")
            cursor.execute("CREATE DATABASE IF NOT EXISTS vmas_dev")
            print("Databases 'vmas' and 'vmas_dev' created successfully")
            
            # Create tables in both databases
            databases = ['vmas', 'vmas_dev']
            
            for db in databases:
                cursor.execute(f"USE {db}")
                print(f"\nSetting up {db} database...")
                
                # Read and execute the SQL script
                with open('database.sql', 'r') as file:
                    # Read the entire script
                    sql_script = file.read()
                    
                    # Split the script into individual statements
                    statements = sql_script.split(';')
                    
                    for statement in statements:
                        if statement.strip():
                            cursor.execute(statement + ';')
                            connection.commit()
                
                print(f"Tables created successfully in {db} database")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nMySQL connection closed")

if __name__ == "__main__":
    setup_databases()
