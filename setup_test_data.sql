-- Insert test departments
INSERT INTO departments (department_id, department_name, email, status) VALUES
('D000001', 'IT Department', 'it@lspu.edu.ph', 'active'),
('D000002', 'Admin Office', 'admin@lspu.edu.ph', 'active'),
('D000003', 'Library', 'library@lspu.edu.ph', 'active');

-- Insert test security guard
INSERT INTO security_guards (security_id, email, username, password_hash) VALUES
('S000001', 'security@lspu.edu.ph', 'security1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LudJ4KtchP9AJwukq');  -- Password: test123

-- Insert test visitor
INSERT INTO visitors (visitor_id, email, visitor_name, password_hash, address, contact_no) VALUES
('V000001', 'visitor@test.com', 'John Doe', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LudJ4KtchP9AJwukq', '123 Test St, City', '+639123456789');  -- Password: test123
