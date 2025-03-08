-- Drop existing tables if they exist
DROP TABLE IF EXISTS payers;
DROP TABLE IF EXISTS plans;
DROP TABLE IF EXISTS providers;
DROP TABLE IF EXISTS provider_groups;
DROP TABLE IF EXISTS provider_group_members;
DROP TABLE IF EXISTS fee_schedules;
DROP TABLE IF EXISTS negotiated_rate_provider_groups;
DROP TABLE IF EXISTS negotiated_rates;
DROP TABLE IF EXISTS plan_fee_schedules;
DROP TABLE IF EXISTS service_lines;

-- Create tables
CREATE TABLE payers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    mrf_index_file_url TEXT
);

CREATE TABLE plans (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,  
    description TEXT,            
    plan_type TEXT NOT NULL,     
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE fee_schedules (
    id SERIAL PRIMARY KEY,
    plan_id INT REFERENCES plans(id) ON DELETE CASCADE,  -- Links to the curated display plan
    service_code TEXT NOT NULL,  -- CPT, HCPCS, DRG, etc.
    billing_class TEXT,  -- Professional, Facility, etc.
    negotiated_rate NUMERIC,  -- Fully built reimbursement rate
    provider_type TEXT,  -- Physician, Hospital, Imaging Center, etc.
    geography TEXT,  -- If applicable (state, region)
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE providers (
    id TEXT PRIMARY KEY,
    npi BIGINT UNIQUE NOT NULL
);

CREATE TABLE service_lines (
    id TEXT PRIMARY KEY,
    billing_code TEXT NOT NULL,
    billing_code_type TEXT NOT NULL,
    billing_code_type_version TEXT
);


CREATE TABLE subplans (
    id TEXT PRIMARY KEY,
    payer_id INT REFERENCES payers(id),
    name TEXT NOT NULL,
    type TEXT,
    category_id TEXT,
    category_id_type TEXT,
    plan_market_type TEXT
);


CREATE TABLE provider_groups (
    id TEXT PRIMARY KEY,
    payer_id INT REFERENCES payers(id),
    payer_assigned_id TEXT NOT NULL UNIQUE,
    ein TEXT
);

CREATE TABLE provider_group_members (
    provider_group_id TEXT REFERENCES provider_groups(id),
    provider_id TEXT REFERENCES providers(id),
    PRIMARY KEY (provider_group_id, provider_id)
);

CREATE TABLE machine_readable_files (
    id TEXT PRIMARY KEY,
    payer_id INT REFERENCES payers(id),
    description TEXT NOT NULL,
    source_file_url TEXT
);

CREATE TABLE machine_readable_file_links (
    id BIGSERIAL PRIMARY KEY,
    subplan_id TEXT REFERENCES subplans(id),
    machine_readable_file_id TEXT REFERENCES machine_readable_files(id)
);

CREATE TABLE negotiated_rates (
    id TEXT PRIMARY KEY,
    payer_id INT REFERENCES payers(id),
    fee_schedule_id TEXT REFERENCES fee_schedules(id),
    service_line_id TEXT REFERENCES service_lines(id),
    negotiation_arrangement TEXT,
    negotiated_type TEXT,
    negotiated_rate DECIMAL(10,2),
    expiration_date DATE,
    billing_class TEXT,
    service_codes TEXT[]  -- Array of strings for service codes
);

CREATE TABLE negotiated_rate_provider_groups (
    id BIGSERIAL PRIMARY KEY,
    negotiated_rate_id TEXT REFERENCES negotiated_rates(id),
    provider_group_id TEXT REFERENCES provider_groups(id)
);

CREATE INDEX idx_sp_subplan_mrf ON subplan_machine_readable_files (subplan_id, machine_readable_file_id);
CREATE INDEX idx_nrpg_negotiated_rate_provider ON negotiated_rate_provider_groups (negotiated_rate_id, provider_group_id);


-- Insert data
INSERT INTO payers (id, name, mrf_index_file_url) VALUES
(100, 'Blue Cross and Blue Shield of Illinois', 'https://app0004702110a5prdnc868.blob.core.windows.net/toc/2025-02-21_Blue-Cross-and-Blue-Shield-of-Illinois_index.json'),
(200, 'United Healthcare', '');

