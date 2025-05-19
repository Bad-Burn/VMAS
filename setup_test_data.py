from db_config import get_db_connection

def setup_test_data():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return

    cursor = conn.cursor()
    
    try:
        # Read and execute the SQL script
        with open('setup_test_data.sql', 'r') as file:
            sql_script = file.read()
            
        # Execute each command separately
        commands = sql_script.split(';')
        for command in commands:
            command = command.strip()
            if command:  # Skip empty commands
                print(f"Executing: {command}")
                cursor.execute(command)
        
        conn.commit()
        print("Test data setup successfully!")
        
    except Exception as e:
        print(f"Error setting up test data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_test_data()
