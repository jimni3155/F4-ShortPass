-- Add S3 URL columns for transcript / agent logs / evidence
ALTER TABLE evaluations ADD COLUMN IF NOT EXISTS transcript_s3_url TEXT;
ALTER TABLE evaluations ADD COLUMN IF NOT EXISTS agent_logs_s3_url TEXT;
ALTER TABLE evaluations ADD COLUMN IF NOT EXISTS evidence_s3_url TEXT;
