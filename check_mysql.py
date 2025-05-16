import mysql.connector
from mysql.connector import Error

def check_mysql_connection():
    try:
        # Try to connect to MySQL server (not to a specific database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            row = cursor.fetchone()
            print("Connected to MySQL Server version:", db_info)
            print("Your connection ID is:", connection.connection_id)
            
            # Check if our database exists
            cursor.execute("SHOW DATABASES LIKE 'vmas';")
            if cursor.fetchone():
                print("VMAS database exists")
                
                # Try connecting to vmas database
                try:
                    cursor.execute("USE vmas;")
                    print("Successfully connected to VMAS database")
                    
                    # Check tables
                    cursor.execute("SHOW TABLES;")
                    tables = cursor.fetchall()
                    print("\nTables in VMAS database:")
                    for table in tables:
                        print(f"- {table[0]}")
                        
                        # Get table structure
                        cursor.execute(f"DESCRIBE {table[0]};")
                        columns = cursor.fetchall()
                        for col in columns:
                            print(f"  - {col[0]} ({col[1]})")
                            
                except Error as e:
                    print(f"Error accessing VMAS database: {e}")
            else:
                print("VMAS database does not exist!")
    
    except Error as e:
        print("Error connecting to MySQL Server:", e)
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nMySQL connection closed.")

if __name__ == "__main__":
    check_mysql_connection()
