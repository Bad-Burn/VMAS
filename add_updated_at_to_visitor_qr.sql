-- Add updated_at column to visitor_qr table
USE vmas_dev;

-- Create visitor_qr table if it doesn't exist
CREATE TABLE IF NOT EXISTS visitor_qr (
    id INT AUTO_INCREMENT PRIMARY KEY,
    visitor_id VARCHAR(20),
    qr_code TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until DATETIME,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (visitor_id) REFERENCES visitors(visitor_id)
);

-- Add updated_at column if it doesn't exist
ALTER TABLE visitor_qr 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
