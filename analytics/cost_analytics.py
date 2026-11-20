
from pipeline.db import get_connection


def execute_query(query, params=None):
    """
    Execute a SQL query and return results as dictionaries.
    """

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(query, params or ())

        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


def get_total_cost():
    """Return total cloud cost grouped by currency."""

    query = """
        SELECT
            currency,
            SUM(cost) AS total_cost
        FROM cloud_costs
        GROUP BY currency
        ORDER BY currency;
    """

    return execute_query(query)


def get_monthly_costs():
    """Return monthly cloud costs."""

    query = """
        SELECT
            month,
            currency,
            total_cost,
            resources_count
        FROM vw_monthly_costs
        ORDER BY month, currency;
    """

    return execute_query(query)


def get_top_resources(limit=10):
    """Return the most expensive cloud resources."""

    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or limit > 100:
        raise ValueError("limit must be an integer between 1 and 100")

    query = """
        SELECT
            resource_name,
            service_name,
            currency,
            total_cost
        FROM vw_costs_by_resource
        ORDER BY total_cost DESC
        LIMIT %s;
    """

    return execute_query(query, (limit,))


def get_cost_variations():
    """Return services with significant cost increases."""

    query = """
        SELECT
            month,
            service_name,
            currency,
            total_cost,
            previous_cost,
            variation_percentage,
            cost_status
        FROM vw_monthly_cost_variations
        WHERE cost_status = 'COST_INCREASE'
        ORDER BY variation_percentage DESC;
    """

    return execute_query(query)


def get_costs_by_environment():
    """Return cloud costs grouped by environment."""

    query = """
        SELECT
            environment,
            currency,
            total_cost,
            resources_count
        FROM vw_costs_by_environment
        ORDER BY total_cost DESC;
    """

    return execute_query(query)
