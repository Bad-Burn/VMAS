USE vmas_dev;

-- Create departments table if it doesn't exist
CREATE TABLE IF NOT EXISTS departments (
    department_id VARCHAR(20) PRIMARY KEY,
    department_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create visitor_registrations table if it doesn't exist
CREATE TABLE IF NOT EXISTS visitor_registrations (
    registration_id INT AUTO_INCREMENT PRIMARY KEY,
    visitor_id VARCHAR(20) NOT NULL,
    department_id VARCHAR(20) NOT NULL,
    purpose TEXT NOT NULL,
    visit_date DATE NOT NULL,
    time_in DATETIME DEFAULT NULL,
    time_out DATETIME DEFAULT NULL,
    status ENUM('pending', 'approved', 'rejected', 'completed', 'active') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (visitor_id) REFERENCES visitors(visitor_id),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- Insert some default departments
INSERT IGNORE INTO departments (department_id, department_name) VALUES
('D000001', 'IT Department'),
('D000002', 'Admin Office'),
('D000003', 'Human Resources'),
('D000004', 'Finance Department'),
('D000005', 'Academic Affairs');
