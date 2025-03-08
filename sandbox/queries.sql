-- Provider group wants to see thier rates for various things
SELECT nrpg.provider_group_id, pg.payer_assigned_id, sl.billing_code, nr.negotiated_rate, nr.negotiated_type, nr.expiration_date
FROM negotiated_rates nr
JOIN service_lines sl ON nr.service_line_id = sl.id
JOIN negotiated_rate_provider_groups nrpg ON nr.id = nrpg.negotiated_rate_id
JOIN provider_groups pg on nrpg.provider_group_id = pg.id
WHERE nrpg.provider_group_id = '988878372cdc0b21554f6e6cdb1d96b5a1ab76da9cbc6f5d5f253ebae4ced527';

-- Same but based on a provider
SELECT nrpg.provider_group_id, pg.payer_assigned_id, sl.billing_code, nr.negotiated_rate, nr.negotiated_type, nr.expiration_date
FROM negotiated_rates nr
JOIN service_lines sl ON nr.service_line_id = sl.id
JOIN negotiated_rate_provider_groups nrpg ON nr.id = nrpg.negotiated_rate_id
JOIN provider_groups pg on nrpg.provider_group_id = pg.id
JOIN provider_group_members pgm on pg.id = pgm.provider_group_id
JOIN providers pr on pgm.provider_id = pr.id
WHERE pr.npi = '1093367575';

-- Similar Plans
SELECT 
    ARRAY_AGG(p.name ORDER BY p.name) AS plan_names,  -- Group plans sharing same fee schedules
    COUNT(p.id) AS num_plans,  -- Count how many plans share the same bundle
    ARRAY_AGG(fs.description ORDER BY fs.description) AS fee_schedule_bundle
FROM plans p
JOIN plan_fee_schedules pfs ON p.id = pfs.plan_id
JOIN fee_schedules fs ON pfs.fee_schedule_id = fs.id
WHERE p.payer_id = 100
GROUP BY p.category_id, p.category_id_type  -- Adjust grouping as needed
ORDER BY num_plans DESC
LIMIT 100;


-- All provider groups with their member providers
SELECT npi, payer_assigned_id, ein FROM provider_group_members pgm
JOIN providers p on pgm.provider_id = p.id
JOIN provider_groups pg on pgm.provider_group_id = pg.id

-- How much a provider group is paid for a service, accross plans
SELECT p.name AS plan_name, nr.negotiated_rate
FROM negotiated_rates nr
JOIN service_lines sl ON nr.service_line_id = sl.id
JOIN negotiated_rate_provider_groups nrpg ON nr.id = nrpg.negotiated_rate_id
JOIN plans p ON nr.payer_id = p.payer_id
WHERE sl.billing_code = '73221'
AND nrpg.provider_group_id = 54089
ORDER BY nr.negotiated_rate DESC;


-- How much different provider groups are paid for a given service
SELECT pg.payer_assigned_id, nr.negotiated_rate
FROM negotiated_rates nr
JOIN service_lines sl ON nr.service_line_id = sl.id
JOIN negotiated_rate_provider_groups nrpg ON nr.id = nrpg.negotiated_rate_id
JOIN provider_groups pg ON nrpg.provider_group_id = pg.id
WHERE sl.billing_code = '73221'
AND nr.payer_id = 100
ORDER BY nr.negotiated_rate DESC;

--Get all the rates defined for a plan
SELECT 
    p.name,
	nr.negotiated_rate, 
    nr.negotiated_type, 
    nr.expiration_date, 
    nr.billing_class, 
    nr.service_line_id, 
    sl.billing_code, 
    sl.billing_code_type, 
    sl.billing_code_type_version
FROM negotiated_rates nr
JOIN service_lines sl ON nr.service_line_id = sl.id
JOIN plan_fee_schedules pfs ON nr.fee_schedule_id = pfs.fee_schedule_id
JOIN plans p ON pfs.plan_id = p.id
WHERE p.name = 'H15048 282 HMO TGE10 MET ST'

--Group plans by linked fee_schedules
WITH plan_fee_sets AS (
    SELECT 
        plan_id, 
        array_agg(DISTINCT description ORDER BY description) AS fee_schedule_set
    FROM plan_fee_schedules
	JOIN fee_schedules fs on plan_fee_schedules.fee_schedule_id = fs.id
    GROUP BY plan_id
)
SELECT 
    fee_schedule_set, 
	max(p.name),
    COUNT(*) AS num_plans
FROM plan_fee_sets
JOIN plans p on plan_fee_sets.plan_id = p.id
GROUP BY fee_schedule_set
ORDER BY num_plans DESC;

--Get plan details for p lans with fee schedule id 1805
SELECT 
    p.id AS plan_id,
    p.name AS plan_name,
    p.type AS plan_type,
    p.category_id,
    p.category_id_type,
    fs.id AS fee_schedule_id,
    fs.description AS fee_schedule_description
FROM plans p
JOIN plan_fee_schedules pfs ON p.id = pfs.plan_id
JOIN fee_schedules fs ON pfs.fee_schedule_id = fs.id
WHERE fs.id = 1805;

--Get plan details for p lans with fee schedule id 1805
SELECT 
    p.id AS plan_id,
    p.name AS plan_name,
    p.type AS plan_type,
    p.category_id,
    p.category_id_type,
    fs.id AS fee_schedule_id,
    fs.description AS fee_schedule_description
FROM plans p
JOIN plan_fee_schedules pfs ON p.id = pfs.plan_id
JOIN fee_schedules fs ON pfs.fee_schedule_id = fs.id
WHERE fs.id = 1805;

-- Get negotiated rates for billing code 73218 and payer id 100
SELECT 
    nr.id AS negotiated_rate_id,
    p.name AS payer_name,
    pl.name AS plan_name,
    sl.billing_code,
    nr.negotiated_rate,
    nr.expiration_date,
    nr.billing_class,
    nr.service_codes
FROM negotiated_rates nr
JOIN service_lines sl ON nr.service_line_id = sl.id
JOIN fee_schedules fs ON nr.fee_schedule_id = fs.id
JOIN plan_fee_schedules pfs ON fs.id = pfs.fee_schedule_id
JOIN plans pl ON pfs.plan_id = pl.id
JOIN payers p ON pl.payer_id = p.id
JOIN negotiated_rate_provider_groups nrpg ON nr.id = nrpg.negotiated_rate_id
JOIN provider_groups pg ON nrpg.provider_group_id = pg.id
JOIN provider_group_members pgm ON pg.id = pgm.provider_group_id
JOIN providers pr ON pgm.provider_id = pr.id
WHERE 
sl.billing_code = '73218'
AND p.id = 100;
