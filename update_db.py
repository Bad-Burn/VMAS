from db_config import get_db_connection

def update_database():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False

    cursor = conn.cursor()
    try:
        # Add missing columns
        add_columns_sql = """
        ALTER TABLE visitor_registrations 
        ADD COLUMN IF NOT EXISTS time_in DATETIME NULL,
        ADD COLUMN IF NOT EXISTS time_out DATETIME NULL;
        """
        cursor.execute(add_columns_sql)

        # Update status enum
        update_status_sql = """
        ALTER TABLE visitor_registrations 
        MODIFY COLUMN status ENUM('pending', 'approved', 'rejected', 'completed', 'active', 'verified') 
        NOT NULL DEFAULT 'pending';
        """
        cursor.execute(update_status_sql)

        # Create indexes
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_visit_dates 
        ON visitor_registrations(visit_date, created_at);
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_visitor_status 
        ON visitor_registrations(visitor_id, status);
        """)

        # Update NULL dates
        cursor.execute("""
        UPDATE visitor_registrations 
        SET visit_date = CURDATE() 
        WHERE visit_date IS NULL;
        """)

        conn.commit()
        print("Database updated successfully")
        return True

    except Exception as e:
        print(f"Error updating database: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_database()
