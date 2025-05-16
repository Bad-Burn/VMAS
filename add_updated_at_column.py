from db_config import get_db_connection

def add_updated_at_column():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False

    cursor = conn.cursor()
    try:
        # Add updated_at column
        cursor.execute("""
            ALTER TABLE visitor_registrations
            ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ON UPDATE CURRENT_TIMESTAMP
            AFTER created_at
        """)
        
        conn.commit()
        print("Successfully added updated_at column to visitor_registrations table")
        return True
        
    except Exception as e:
        print(f"Error adding column: {str(e)}")
        conn.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    add_updated_at_column()
