from db_config import get_db_connection
from datetime import datetime

def add_updated_at_column():
    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to connect to database")
            return False

        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'vmas'
            AND TABLE_NAME = 'visitor_registrations' 
            AND COLUMN_NAME = 'updated_at'
        """)
        
        if cursor.fetchone()[0] == 0:
            # Add updated_at column
            cursor.execute("""
                ALTER TABLE visitor_registrations
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            """)
            
            # Initialize the column with created_at values
            cursor.execute("""
                UPDATE visitor_registrations 
                SET updated_at = created_at 
                WHERE updated_at IS NULL
            """)
            
            conn.commit()
            print("Successfully added updated_at column")
        else:
            print("Column already exists")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"Error adding column: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    add_updated_at_column()
