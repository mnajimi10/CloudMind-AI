
from analytics.cost_analytics import (
    get_total_cost,
    get_monthly_costs,
    get_top_resources,
    get_cost_variations,
    get_costs_by_environment,
)


def display_results(title, results):
    print(f"\n{'=' * 50}")
    print(title)
    print("=" * 50)

    if not results:
        print("No results found.")
        return

    for result in results:
        print(result)


def main():
    display_results(
        "TOTAL CLOUD COST",
        get_total_cost()
    )

    display_results(
        "MONTHLY COSTS",
        get_monthly_costs()
    )

    display_results(
        "TOP 5 RESOURCES",
        get_top_resources(limit=5)
    )

    display_results(
        "COST INCREASES",
        get_cost_variations()
    )

    display_results(
        "COSTS BY ENVIRONMENT",
        get_costs_by_environment()
    )


if __name__ == "__main__":
    main()
