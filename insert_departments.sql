USE vmas_dev;

-- First, clear existing departments (optional, comment out if you want to keep existing ones)
-- DELETE FROM departments;

-- Insert LSPU departments
INSERT INTO departments (department_id, department_name, email, status) VALUES
('D000001', 'College of Arts and Sciences', 'cas@lspu.edu.ph', 'active'),
('D000002', 'College of Teacher Education', 'cted@lspu.edu.ph', 'active'),
('D000003', 'College of Agriculture', 'ca@lspu.edu.ph', 'active'),
('D000004', 'College of Engineering', 'coe@lspu.edu.ph', 'active'),
('D000005', 'College of Business Management and Accountancy', 'cbma@lspu.edu.ph', 'active'),
('D000006', 'College of Computer Studies', 'ccs@lspu.edu.ph', 'active'),
('D000007', 'College of Hospitality Management and Tourism', 'chmt@lspu.edu.ph', 'active'),
('D000008', 'College of Criminal Justice Education', 'ccje@lspu.edu.ph', 'active'),
('D000009', 'Graduate School', 'gs@lspu.edu.ph', 'active'),
('D000010', 'Office of the University President', 'president@lspu.edu.ph', 'active'),
('D000011', 'Office of the Vice President for Academic Affairs', 'vpaa@lspu.edu.ph', 'active'),
('D000012', 'Office of the Vice President for Administration', 'vpa@lspu.edu.ph', 'active'),
('D000013', 'Office of the Vice President for Research and Extension', 'vpre@lspu.edu.ph', 'active'),
('D000014', 'Human Resource Department', 'hrd@lspu.edu.ph', 'active'),
('D000015', 'Finance Department', 'finance@lspu.edu.ph', 'active'),
('D000016', 'Registrar Office', 'registrar@lspu.edu.ph', 'active'),
('D000017', 'Admissions Office', 'admissions@lspu.edu.ph', 'active'),
('D000018', 'Library Services', 'library@lspu.edu.ph', 'active'),
('D000019', 'Information Technology Services', 'it@lspu.edu.ph', 'active'),
('D000020', 'Student Affairs Office', 'sao@lspu.edu.ph', 'active'),
('D000021', 'Guidance and Counseling Office', 'guidance@lspu.edu.ph', 'active'),
('D000022', 'Medical Services', 'medical@lspu.edu.ph', 'active'),
('D000023', 'Security Office', 'security@lspu.edu.ph', 'active'),
('D000024', 'Facilities Management', 'facilities@lspu.edu.ph', 'active'),
('D000025', 'Research and Development Office', 'research@lspu.edu.ph', 'active'),
('D000026', 'Extension Services Office', 'extension@lspu.edu.ph', 'active'),
('D000027', 'Quality Assurance Office', 'qa@lspu.edu.ph', 'active'),
('D000028', 'Planning and Development Office', 'planning@lspu.edu.ph', 'active'),
('D000029', 'International Affairs Office', 'international@lspu.edu.ph', 'active'),
('D000030', 'Alumni Relations Office', 'alumni@lspu.edu.ph', 'active');