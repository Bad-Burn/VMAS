from db_config import get_db_connection

def insert_departments():
    # Department data
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

    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to connect to database")
            return False

        cursor = conn.cursor()

        # Insert departments
        insert_sql = """
        INSERT IGNORE INTO departments 
        (department_id, department_name, email, status) 
        VALUES (%s, %s, %s, 'active')
        """
        
        for dept in departments:
            try:
                cursor.execute(insert_sql, dept)
                print(f"Inserted department: {dept[1]}")
            except Exception as e:
                print(f"Error inserting {dept[1]}: {e}")
                continue

        conn.commit()
        print("Departments inserted successfully")
        return True

    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            print("Database connection closed")

if __name__ == "__main__":
    insert_departments()
