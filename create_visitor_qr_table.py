from db_config import get_db_connection

def create_visitor_qr_table():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False

    cursor = conn.cursor()
    try:
        # Create visitor_qr table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visitor_qr (
                id INT AUTO_INCREMENT PRIMARY KEY,
                visitor_id VARCHAR(20),
                qr_code TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                valid_until DATETIME,
                FOREIGN KEY (visitor_id) REFERENCES visitors(visitor_id)
            )
        """)
        conn.commit()
        print("Successfully created visitor_qr table")
        return True
    except Exception as e:
        print(f"Error creating visitor_qr table: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_visitor_qr_table()
