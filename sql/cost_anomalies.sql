
CREATE OR REPLACE VIEW vw_monthly_cost_variations AS

WITH monthly AS (
    SELECT
        DATE_TRUNC('month', usage_date)::DATE AS month,
        service_name,
        currency,
        SUM(cost) AS total_cost
    FROM cloud_costs
    GROUP BY
        DATE_TRUNC('month', usage_date)::DATE,
        service_name,
        currency
),

comparisons AS (
    SELECT
        month,
        service_name,
        currency,
        total_cost,

        LAG(total_cost) OVER (
            PARTITION BY service_name, currency
            ORDER BY month
        ) AS previous_cost

    FROM monthly
)

SELECT
    month,
    service_name,
    currency,
    total_cost,
    previous_cost,

    total_cost - previous_cost AS cost_difference,

    ROUND(
        (
            (total_cost - previous_cost)
            / NULLIF(previous_cost, 0)
        ) * 100,
        2
    ) AS variation_percentage,

    CASE
        WHEN previous_cost IS NULL
            THEN 'NO_PREVIOUS_PERIOD'

        WHEN previous_cost = 0
            THEN 'NEW_OR_REACTIVATED_SPENDING'

        WHEN total_cost > previous_cost * 1.20
            THEN 'COST_INCREASE'

        WHEN total_cost < previous_cost * 0.80
            THEN 'COST_DECREASE'

        ELSE 'STABLE'
    END AS cost_status

FROM comparisons;




CREATE OR REPLACE VIEW vw_resource_cost_variations AS

WITH monthly AS (
    SELECT
        DATE_TRUNC('month', usage_date)::DATE AS month,
        resource_id,
        resource_name,
        service_name,
        currency,
        SUM(cost) AS total_cost
    FROM cloud_costs
    GROUP BY
        DATE_TRUNC('month', usage_date)::DATE,
        resource_id,
        resource_name,
        service_name,
        currency
),

comparisons AS (
    SELECT
        *,
        LAG(total_cost) OVER (
            PARTITION BY resource_id, currency
            ORDER BY month
        ) AS previous_cost
    FROM monthly
)

SELECT
    month,
    resource_id,
    resource_name,
    service_name,
    currency,
    total_cost,
    previous_cost,

    ROUND(
        (total_cost - previous_cost)
        / NULLIF(previous_cost, 0) * 100,
        2
    ) AS variation_percentage

FROM comparisons;



