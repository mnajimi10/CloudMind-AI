
-- 1. Daily cloud costs
CREATE OR REPLACE VIEW vw_daily_costs AS
SELECT
    usage_date,
    currency,
    SUM(cost) AS total_cost,
    COUNT(*) AS cost_records,
    COUNT(DISTINCT resource_id) AS resources_count
FROM cloud_costs
GROUP BY usage_date, currency;


-- 2. Monthly cloud costs
CREATE OR REPLACE VIEW vw_monthly_costs AS
SELECT
    DATE_TRUNC('month', usage_date)::DATE AS month,
    currency,
    SUM(cost) AS total_cost,
    COUNT(DISTINCT resource_id) AS resources_count
FROM cloud_costs
GROUP BY DATE_TRUNC('month', usage_date)::DATE, currency;


-- 3. Costs by Azure service
CREATE OR REPLACE VIEW vw_costs_by_service AS
SELECT
    service_name,
    service_family,
    currency,
    SUM(cost) AS total_cost,
    COUNT(DISTINCT resource_id) AS resources_count
FROM cloud_costs
GROUP BY service_name, service_family, currency;


-- 4. Costs by resource
CREATE OR REPLACE VIEW vw_costs_by_resource AS
SELECT
    resource_id,
    resource_name,
    resource_group,
    service_name,
    region,
    currency,
    SUM(cost) AS total_cost
FROM cloud_costs
GROUP BY
    resource_id,
    resource_name,
    resource_group,
    service_name,
    region,
    currency;


-- 5. Costs by environment
CREATE OR REPLACE VIEW vw_costs_by_environment AS
SELECT
    COALESCE(tags ->> 'environment', 'unknown') AS environment,
    currency,
    SUM(cost) AS total_cost,
    COUNT(DISTINCT resource_id) AS resources_count
FROM cloud_costs
GROUP BY
    COALESCE(tags ->> 'environment', 'unknown'),
    currency;
