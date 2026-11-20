
from fastapi import FastAPI, HTTPException, Query

from analytics.cost_analytics import (
    get_total_cost,
    get_monthly_costs,
    get_top_resources,
    get_cost_variations,
    get_costs_by_environment,
)

app = FastAPI(
    title="CloudMind AI API",
    description="FinOps analytics API for Azure cloud costs.",
    version="1.0.0",
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "application": "CloudMind AI API",
    }


@app.get("/api/v1/costs/total", tags=["Costs"])
def total_costs():
    try:
        return get_total_cost()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve total cloud costs.",
        )


@app.get("/api/v1/costs/monthly", tags=["Costs"])
def monthly_costs():
    try:
        return get_monthly_costs()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve monthly costs.",
        )


@app.get("/api/v1/costs/top-resources", tags=["Costs"])
def top_resources(
    limit: int = Query(default=10, ge=1, le=100)
):
    try:
        return get_top_resources(limit=limit)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve top resources.",
        )


@app.get("/api/v1/costs/variations", tags=["Anomalies"])
def cost_variations():
    try:
        return get_cost_variations()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve cost variations.",
        )


@app.get("/api/v1/costs/environments", tags=["Costs"])
def costs_by_environment():
    try:
        return get_costs_by_environment()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve environment costs.",
        )
