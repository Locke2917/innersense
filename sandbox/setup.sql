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
    mrf_index_file_url TXT
);

CREATE TABLE plans (
    id SERIAL PRIMARY KEY,
    payer_id INT REFERENCES payers(id),
    name TEXT NOT NULL,
    type TEXT,
    category_id TEXT,
    category_id_type TEXT,
    plan_market_type TEXT
);

CREATE TABLE providers (
    id SERIAL PRIMARY KEY,
    npi BIGINT UNIQUE NOT NULL
);

CREATE TABLE provider_groups (
    id SERIAL PRIMARY KEY,
    payer_id INT REFERENCES payers(id),
    payer_assigned_id TEXT NOT NULL UNIQUE,
    ein TEXT
);

CREATE TABLE provider_group_members (
    provider_group_id INT REFERENCES provider_groups(id),
    provider_id INT REFERENCES providers(id),
    PRIMARY KEY (provider_group_id, provider_id)
);

CREATE TABLE fee_schedules (
    id SERIAL PRIMARY KEY,
    payer_id INT REFERENCES payers(id),
    description TEXT NOT NULL,
    source_file_url TEXT
);

CREATE TABLE plan_fee_schedules (
    id SERIAL PRIMARY KEY,
    plan_id INT REFERENCES plans(id),
    fee_schedule_id INT REFERENCES fee_schedules(id)
);

CREATE TABLE service_lines (
    id SERIAL PRIMARY KEY,
    billing_code TEXT NOT NULL,
    billing_code_type TEXT NOT NULL,
    billing_code_type_version TEXT
);

CREATE TABLE negotiated_rates (
    id SERIAL PRIMARY KEY,
    payer_id INT REFERENCES payers(id),
    fee_schedule_id INT REFERENCES fee_schedules(id),
    service_line_id INT REFERENCES service_lines(id),
    negotiation_arrangement TEXT NOT NULL,
    negotiated_type TEXT NOT NULL,
    negotiated_rate DECIMAL(10,2) NOT NULL,
    expiration_date DATE,
    billing_class TEXT NOT NULL,
    service_codes TEXT[]  -- Array of strings for service codes
);

CREATE TABLE negotiated_rate_provider_groups (
    id SERIAL PRIMARY KEY,
    negotiated_rate_id INT REFERENCES negotiated_rates(id),
    provider_group_id INT REFERENCES provider_groups(id)
);

CREATE INDEX idx_nrpg_negotiated_rate_provider ON negotiated_rate_provider_groups (negotiated_rate_id, provider_group_id);


-- Insert data
INSERT INTO payers (id, name, mrf_index_file_url) VALUES
(100, 'Blue Cross and Blue Shield of Illinois', 'https://app0004702110a5prdnc868.blob.core.windows.net/toc/2025-02-21_Blue-Cross-and-Blue-Shield-of-Illinois_index.json');

INSERT INTO plans (id, payer_id, name, type, category_id, category_id_type, plan_market_type) VALUES
(500, 100, '000523 10 PPO+ NPP83323_XOF', 'PPO', '36096', 'HIOS', 'group');

INSERT INTO providers (id, npi) VALUES
(99, 1003232992),
(98, 1003823220),
(97, 1023161940),
(96, 1033327069),
(95, 1003882374),
(94, 1013409903),
(93, 1992092167);

INSERT INTO provider_groups (id, payer_id, payer_assigned_id, ein) VALUES
(999, 100, '121.1', '37-1488231'),
(998, 100, '121.2', '36-3616314');

INSERT INTO provider_group_members (provider_group_id, provider_id) VALUES
(999, 99),
(999, 98),
(999, 97),
(999, 96),
(998, 95),
(998, 94),
(998, 93);

INSERT INTO fee_schedules (id, payer_id, description, source_file_url) VALUES
(10000, 100, 'PPO Participating Provider Options in-network file', 'https://app0004702110a5prdnc868.blob.core.windows.net/output/2025-02-17_Blue-Cross-and-Blue-Shield-of-Illinois_Blue-Advantage-HMO_in-network-rates.json.gz'),
(10001, 100, 'HMO Illinois in-network file', 'https://app0004702110a5prdnc868.blob.core.windows.net/output/2025-02-17_Blue-Cross-and-Blue-Shield-of-Illinois_HMO-Illinois_in-network-rates.json.gz'),
(10001, 100, 'Blue Advantage HMO in-network file', 'https://app0004702110a5prdnc868.blob.core.windows.net/output/2025-02-17_Blue-Cross-and-Blue-Shield-of-Illinois_Blue-Advantage-HMO_in-network-rates.json.gz');


INSERT INTO plan_fee_schedules (id, plan_id, fee_schedule_id) VALUES
(66, 500, 44);

INSERT INTO service_lines (id, billing_code, billing_code_type, billing_code_type_version) VALUES
(1, '93232', 'CPT', '2025'),
(2, '73218', 'CPT', '2025');

INSERT INTO negotiated_rates (id, payer_id, fee_schedule_id, service_line_id, negotiation_arrangement, negotiated_type, negotiated_rate, expiration_date, billing_class, service_codes) VALUES
(37, 100, 44, 1, 'ffs', 'negotiated', 217.55, '2026-12-31', 'institutional', NULL),
(38, 100, 44, 1, 'ffs', 'negotiated', 238.45, '2025-06-30', 'institutional', NULL),
(39, 100, 44, 2, 'ffs', 'negotiated', 202.92, '2025-02-28', 'institutional', ARRAY['02', '17', '18', '19', '22']);

INSERT INTO negotiated_rate_provider_groups (id, negotiated_rate_id, provider_group_id) VALUES
(1, 37, 999),
(2, 38, 998),
(3, 39, 999),
(4, 39, 998);


-- TO DROP ALL DATA
-- Disable constraints temporarily
ALTER TABLE provider_group_members DROP CONSTRAINT provider_group_members_provider_group_id_fkey;
ALTER TABLE provider_group_members DROP CONSTRAINT provider_group_members_provider_id_fkey;
ALTER TABLE plan_fee_schedules DROP CONSTRAINT plan_fee_schedules_plan_id_fkey;
ALTER TABLE plan_fee_schedules DROP CONSTRAINT plan_fee_schedules_fee_schedule_id_fkey;
ALTER TABLE negotiated_rate_provider_groups DROP CONSTRAINT negotiated_rate_provider_groups_negotiated_rate_id_fkey;
ALTER TABLE negotiated_rate_provider_groups DROP CONSTRAINT negotiated_rate_provider_groups_provider_group_id_fkey;
ALTER TABLE negotiated_rates DROP CONSTRAINT negotiated_rates_payer_id_fkey;
ALTER TABLE negotiated_rates DROP CONSTRAINT negotiated_rates_fee_schedule_id_fkey;
ALTER TABLE negotiated_rates DROP CONSTRAINT negotiated_rates_service_line_id_fkey;

-- Truncate all tables
TRUNCATE TABLE 
    provider_group_members,
    negotiated_rate_provider_groups,
    negotiated_rates,
    service_lines,
    plan_fee_schedules,
    fee_schedules,
    provider_groups,
    providers,
    plans,
    payers
RESTART IDENTITY CASCADE;

-- Re-enable constraints
ALTER TABLE provider_group_members ADD CONSTRAINT provider_group_members_provider_group_id_fkey FOREIGN KEY (provider_group_id) REFERENCES provider_groups(id);
ALTER TABLE provider_group_members ADD CONSTRAINT provider_group_members_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES providers(id);
ALTER TABLE plan_fee_schedules ADD CONSTRAINT plan_fee_schedules_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES plans(id);
ALTER TABLE plan_fee_schedules ADD CONSTRAINT plan_fee_schedules_fee_schedule_id_fkey FOREIGN KEY (fee_schedule_id) REFERENCES fee_schedules(id);
ALTER TABLE negotiated_rate_provider_groups ADD CONSTRAINT negotiated_rate_provider_groups_negotiated_rate_id_fkey FOREIGN KEY (negotiated_rate_id) REFERENCES negotiated_rates(id);
ALTER TABLE negotiated_rate_provider_groups ADD CONSTRAINT negotiated_rate_provider_groups_provider_group_id_fkey FOREIGN KEY (provider_group_id) REFERENCES provider_groups(id);
ALTER TABLE negotiated_rates ADD CONSTRAINT negotiated_rates_payer_id_fkey FOREIGN KEY (payer_id) REFERENCES payers(id);
ALTER TABLE negotiated_rates ADD CONSTRAINT negotiated_rates_fee_schedule_id_fkey FOREIGN KEY (fee_schedule_id) REFERENCES fee_schedules(id);
ALTER TABLE negotiated_rates ADD CONSTRAINT negotiated_rates_service_line_id_fkey FOREIGN KEY (service_line_id) REFERENCES service_lines(id);



