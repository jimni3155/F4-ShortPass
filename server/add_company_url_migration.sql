-- Add company_url field to companies table
ALTER TABLE companies ADD COLUMN IF NOT EXISTS company_url VARCHAR(500);
