-- Add missing time_in and time_out columns if they don't exist
ALTER TABLE visitor_registrations 
ADD COLUMN IF NOT EXISTS time_in DATETIME NULL,
ADD COLUMN IF NOT EXISTS time_out DATETIME NULL;

-- Update status enum to include all needed statuses
ALTER TABLE visitor_registrations 
MODIFY COLUMN status ENUM('pending', 'approved', 'rejected', 'completed', 'active', 'verified') NOT NULL DEFAULT 'pending';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_visit_dates ON visitor_registrations(visit_date, created_at);
CREATE INDEX IF NOT EXISTS idx_visitor_status ON visitor_registrations(visitor_id, status);

-- Update any NULL visit dates to current date
UPDATE visitor_registrations 
SET visit_date = CURDATE() 
WHERE visit_date IS NULL;
