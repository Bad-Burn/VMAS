from db_config import get_db_connection

def add_time_columns():
    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to connect to database")
            return False

        cursor = conn.cursor()
        
        # Add time_in column if it doesn't exist
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'visitor_registrations'
            AND table_schema = DATABASE()
            AND column_name = 'time_in'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE visitor_registrations
                ADD COLUMN time_in DATETIME NULL AFTER visit_date
            """)
            print("Added time_in column")

        # Add time_out column if it doesn't exist
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'visitor_registrations'
            AND table_schema = DATABASE()
            AND column_name = 'time_out'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE visitor_registrations
                ADD COLUMN time_out DATETIME NULL AFTER time_in
            """)
            print("Added time_out column")

        conn.commit()
        print("Database update completed successfully")
        return True

    except Exception as e:
        print(f"Error updating database: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return False

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_time_columns()
