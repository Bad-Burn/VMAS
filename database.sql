-- Drop existing tables and constraints
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS visitor_registrations;
DROP TABLE IF EXISTS system_logs;
DROP TABLE IF EXISTS department_staff;
DROP TABLE IF EXISTS visitors;
DROP TABLE IF EXISTS security_guards;
DROP TABLE IF EXISTS departments;
SET FOREIGN_KEY_CHECKS = 1;

-- Create security_guards table
CREATE TABLE IF NOT EXISTS security_guards (
    security_id VARCHAR(20) PRIMARY KEY,
    email VARCHAR(100),
    username VARCHAR(50),
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create departments table
CREATE TABLE IF NOT EXISTS departments (
    department_id VARCHAR(20) PRIMARY KEY,
    department_name VARCHAR(100),
    email VARCHAR(100),
    status ENUM('active', 'inactive'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create visitors table
CREATE TABLE IF NOT EXISTS visitors (
    visitor_id VARCHAR(20) PRIMARY KEY,
    email VARCHAR(100),
    visitor_name VARCHAR(100),
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    address TEXT,
    contact_no VARCHAR(20),
    qr_code_path VARCHAR(255)
);

-- Create visitor_registrations table
CREATE TABLE IF NOT EXISTS visitor_registrations (    registration_id INT(11) PRIMARY KEY AUTO_INCREMENT,
    department_id VARCHAR(20),
    purpose TEXT,
    visit_date DATE,
    time_in DATETIME,
    time_out DATETIME,
    status ENUM('pending', 'approved', 'rejected', 'completed', 'active', 'verified'),
    qr_code_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by_security_id VARCHAR(20),
    visitor_id VARCHAR(20),
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (approved_by_security_id) REFERENCES security_guards(security_id),
    FOREIGN KEY (visitor_id) REFERENCES visitors(visitor_id)
);

-- Create department_staff table
CREATE TABLE IF NOT EXISTS department_staff (
    staff_id VARCHAR(20) PRIMARY KEY,
    department_id VARCHAR(20),
    email VARCHAR(100),
    staff_name VARCHAR(100),
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- Create system_logs table
CREATE TABLE IF NOT EXISTS system_logs (
    log_id INT(11) PRIMARY KEY AUTO_INCREMENT,
    security_id VARCHAR(20),
    staff_id VARCHAR(20),
    action VARCHAR(100),
    ip_address VARCHAR(45),
    related_department_id VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (security_id) REFERENCES security_guards(security_id),
    FOREIGN KEY (staff_id) REFERENCES department_staff(staff_id),
    FOREIGN KEY (related_department_id) REFERENCES departments(department_id)
);

-- Create indexes for better performance
CREATE INDEX idx_visit_status ON visitor_registrations(status);
CREATE INDEX idx_visit_date ON visitor_registrations(visit_date);
CREATE INDEX idx_department_status ON departments(status);
CREATE INDEX idx_visitors_email ON visitors(email);
CREATE INDEX idx_staff_dept ON department_staff(department_id);
CREATE INDEX idx_logs_created ON system_logs(created_at);
