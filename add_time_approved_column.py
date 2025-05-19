from db_config import get_db_connection

def add_time_approved_column():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False

    cursor = conn.cursor()
    try:
        # First check if column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'visitor_registrations' 
            AND COLUMN_NAME = 'time_approved'
        """)
        if cursor.fetchone()[0] == 0:
            # Add time_approved column
            cursor.execute("""
                ALTER TABLE visitor_registrations
                ADD COLUMN time_approved DATETIME NULL
                AFTER status
            """)
            
            conn.commit()
            print("Successfully added time_approved column")
        else:
            print("time_approved column already exists")
        
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
    add_time_approved_column()
