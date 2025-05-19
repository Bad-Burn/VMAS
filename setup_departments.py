import mysql.connector
from mysql.connector import Error

def setup_departments():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS vmas_dev")
            cursor.execute("USE vmas_dev")
            
            # Create departments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    department_id VARCHAR(20) PRIMARY KEY,
                    department_name VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    status ENUM('active', 'inactive') DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert departments
            departments = [
                ('D000001', 'College of Arts and Sciences', 'cas@lspu.edu.ph'),
                ('D000002', 'College of Teacher Education', 'cted@lspu.edu.ph'),
                ('D000003', 'College of Agriculture', 'ca@lspu.edu.ph'),
                ('D000004', 'College of Engineering', 'coe@lspu.edu.ph'),
                ('D000005', 'College of Business Management and Accountancy', 'cbma@lspu.edu.ph'),
                ('D000006', 'College of Computer Studies', 'ccs@lspu.edu.ph'),
                ('D000007', 'College of Hospitality Management and Tourism', 'chmt@lspu.edu.ph'),
                ('D000008', 'College of Criminal Justice Education', 'ccje@lspu.edu.ph'),
                ('D000009', 'Graduate School', 'gs@lspu.edu.ph'),
                ('D000010', 'Office of the University President', 'president@lspu.edu.ph'),
                ('D000011', 'Office of the Vice President for Academic Affairs', 'vpaa@lspu.edu.ph'),
                ('D000012', 'Office of the Vice President for Administration', 'vpa@lspu.edu.ph'),
                ('D000013', 'Office of the Vice President for Research and Extension', 'vpre@lspu.edu.ph'),
                ('D000014', 'Human Resource Department', 'hrd@lspu.edu.ph'),
                ('D000015', 'Finance Department', 'finance@lspu.edu.ph'),
                ('D000016', 'Registrar Office', 'registrar@lspu.edu.ph'),
                ('D000017', 'Admissions Office', 'admissions@lspu.edu.ph'),
                ('D000018', 'Library Services', 'library@lspu.edu.ph'),
                ('D000019', 'Information Technology Services', 'it@lspu.edu.ph'),
                ('D000020', 'Student Affairs Office', 'sao@lspu.edu.ph'),
                ('D000021', 'Guidance and Counseling Office', 'guidance@lspu.edu.ph'),
                ('D000022', 'Medical Services', 'medical@lspu.edu.ph'),
                ('D000023', 'Security Office', 'security@lspu.edu.ph'),
                ('D000024', 'Facilities Management', 'facilities@lspu.edu.ph'),
                ('D000025', 'Research and Development Office', 'research@lspu.edu.ph'),
                ('D000026', 'Extension Services Office', 'extension@lspu.edu.ph'),
                ('D000027', 'Quality Assurance Office', 'qa@lspu.edu.ph'),
                ('D000028', 'Planning and Development Office', 'planning@lspu.edu.ph'),
                ('D000029', 'International Affairs Office', 'international@lspu.edu.ph'),
                ('D000030', 'Alumni Relations Office', 'alumni@lspu.edu.ph')
            ]
            
            # Insert departments with REPLACE to avoid duplicates
            insert_query = """
                REPLACE INTO departments 
                (department_id, department_name, email) 
                VALUES (%s, %s, %s)
            """
            cursor.executemany(insert_query, departments)
            connection.commit()
            print("All departments have been successfully inserted!")
            
            # Verify the data
            cursor.execute("SELECT COUNT(*) FROM departments")
            count = cursor.fetchone()[0]
            print(f"Total departments in database: {count}")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    setup_departments()
