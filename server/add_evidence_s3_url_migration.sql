-- Add evidence_s3_url field to evaluations table
ALTER TABLE evaluations ADD COLUMN IF NOT EXISTS evidence_s3_url TEXT;
