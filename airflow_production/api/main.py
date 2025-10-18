"""
Agricultural SRI Market Data API

FastAPI server providing real-time access to SRI data,
reports, and agricultural risk assessments.

Endpoints:
- GET /sri/latest - Latest SRI data
- GET /sri/{year} - Specific year data
- GET /sri/state/{state} - State-specific data
- GET /reports/{year} - Annual report
- GET /health - Health check
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import pandas as pd
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Agricultural SRI Market Data API",
    description="Real-time access to agricultural risk assessments and market intelligence",
    version="1.0.0",
    contact={
        "name": "Agricultural Risk Team",
        "email": "api@agcompany.com"
    }
)

# CORS middleware (allow access from dashboards)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data directory
DATA_DIR = "/opt/airflow/data/results"
REPORTS_DIR = "/opt/airflow/data/reports"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_available_years() -> List[int]:
    """Get list of years with available data"""
    if not os.path.exists(DATA_DIR):
        return []

    years = []
    for item in os.listdir(DATA_DIR):
        item_path = os.path.join(DATA_DIR, item)
        if os.path.isdir(item_path) and item.isdigit():
            years.append(int(item))

    return sorted(years, reverse=True)


def load_sri_data(year: int) -> pd.DataFrame:
    """Load SRI data for a specific year"""
    file_path = os.path.join(DATA_DIR, str(year), 'sri_results.csv')

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"SRI data not found for year {year}"
        )

    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        logger.error(f"Error loading SRI data for {year}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading data: {str(e)}"
        )


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "message": "Agricultural SRI Market Data API",
        "version": "1.0.0",
        "endpoints": {
            "/sri/latest": "Get latest SRI data",
            "/sri/{year}": "Get SRI data for specific year",
            "/sri/state/{state}": "Get state-specific SRI data",
            "/sri/high-risk": "Get high-risk states",
            "/reports/{year}/summary": "Get market summary report",
            "/health": "Health check",
            "/docs": "API documentation"
        }
    }


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    available_years = get_available_years()

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_available": len(available_years) > 0,
        "available_years": available_years,
        "latest_year": available_years[0] if available_years else None
    }


@app.get("/sri/latest", tags=["SRI Data"])
async def get_latest_sri(
    limit: Optional[int] = Query(None, description="Limit number of results")
):
    """
    Get latest SRI data (most recent year)

    Returns all SRI scores for the most recent year
    """
    available_years = get_available_years()

    if not available_years:
        raise HTTPException(
            status_code=404,
            detail="No SRI data available"
        )

    latest_year = available_years[0]
    df = load_sri_data(latest_year)

    # Convert to dict
    data = df.to_dict('records')

    if limit:
        data = data[:limit]

    return {
        "year": latest_year,
        "updated": datetime.now().isoformat(),
        "total_records": len(df),
        "returned_records": len(data),
        "data": data
    }


@app.get("/sri/{year}", tags=["SRI Data"])
async def get_sri_by_year(
    year: int,
    state: Optional[str] = Query(None, description="Filter by state name"),
    commodity: Optional[str] = Query(None, description="Filter by commodity (CORN, SOYBEANS, WHEAT)")
):
    """
    Get SRI data for a specific year

    Optional filters:
    - state: Filter by state name (e.g., "California")
    - commodity: Filter by commodity (e.g., "CORN")
    """
    df = load_sri_data(year)

    # Apply filters
    if state:
        df = df[df['state_name'].str.upper() == state.upper()]

        if len(df) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for state: {state}"
            )

    if commodity:
        df = df[df['commodity'].str.upper() == commodity.upper()]

        if len(df) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for commodity: {commodity}"
            )

    data = df.to_dict('records')

    return {
        "year": year,
        "filters": {
            "state": state,
            "commodity": commodity
        },
        "total_records": len(data),
        "data": data
    }


@app.get("/sri/state/{state_name}", tags=["SRI Data"])
async def get_sri_by_state(
    state_name: str,
    years: Optional[int] = Query(5, description="Number of recent years to return")
):
    """
    Get SRI data for a specific state across multiple years

    Returns historical SRI trends for the specified state
    """
    available_years = get_available_years()

    if not available_years:
        raise HTTPException(
            status_code=404,
            detail="No SRI data available"
        )

    # Limit to requested number of years
    years_to_fetch = available_years[:years]

    all_data = []

    for year in years_to_fetch:
        try:
            df = load_sri_data(year)
            df_state = df[df['state_name'].str.upper() == state_name.upper()]

            if len(df_state) > 0:
                state_data = df_state.to_dict('records')
                all_data.extend(state_data)

        except Exception as e:
            logger.warning(f"Could not load data for {year}: {str(e)}")
            continue

    if not all_data:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for state: {state_name}"
        )

    return {
        "state": state_name,
        "years": years_to_fetch,
        "total_records": len(all_data),
        "data": all_data
    }


@app.get("/sri/high-risk", tags=["SRI Data"])
async def get_high_risk_states(
    year: Optional[int] = Query(None, description="Specific year (default: latest)"),
    threshold: float = Query(50.0, description="SRI threshold for high-risk (default: 50.0)")
):
    """
    Get list of high-risk states based on SRI threshold

    Returns states with SRI scores above the threshold
    """
    available_years = get_available_years()

    if not available_years:
        raise HTTPException(
            status_code=404,
            detail="No SRI data available"
        )

    target_year = year if year else available_years[0]
    df = load_sri_data(target_year)

    # Filter high-risk states
    high_risk = df[df['SRI'] >= threshold].copy()

    # Sort by SRI descending
    high_risk = high_risk.sort_values('SRI', ascending=False)

    # Group by state and get average SRI
    state_summary = high_risk.groupby('state_name').agg({
        'SRI': 'mean',
        'commodity': lambda x: ', '.join(x.unique())
    }).reset_index()

    state_summary = state_summary.sort_values('SRI', ascending=False)

    return {
        "year": target_year,
        "threshold": threshold,
        "high_risk_states_count": len(state_summary),
        "national_avg_sri": float(df['SRI'].mean()),
        "states": state_summary.to_dict('records'),
        "detailed_data": high_risk.to_dict('records')
    }


@app.get("/sri/statistics/{year}", tags=["Analytics"])
async def get_sri_statistics(year: int):
    """
    Get statistical summary of SRI data for a year

    Returns aggregated statistics and insights
    """
    df = load_sri_data(year)

    stats = {
        "year": year,
        "total_records": len(df),
        "national_statistics": {
            "avg_sri": float(df['SRI'].mean()),
            "median_sri": float(df['SRI'].median()),
            "min_sri": float(df['SRI'].min()),
            "max_sri": float(df['SRI'].max()),
            "std_sri": float(df['SRI'].std())
        },
        "risk_distribution": {
            "low": int(len(df[df['SRI'] < 25])),
            "moderate": int(len(df[(df['SRI'] >= 25) & (df['SRI'] < 50)])),
            "high": int(len(df[(df['SRI'] >= 50) & (df['SRI'] < 75)])),
            "very_high": int(len(df[df['SRI'] >= 75]))
        },
        "by_commodity": {},
        "top_5_high_risk_states": [],
        "top_5_low_risk_states": []
    }

    # Statistics by commodity
    for commodity in df['commodity'].unique():
        commodity_data = df[df['commodity'] == commodity]
        stats['by_commodity'][commodity] = {
            "avg_sri": float(commodity_data['SRI'].mean()),
            "high_risk_states": int(len(commodity_data[commodity_data['SRI'] > 50]))
        }

    # Top high-risk states
    state_avg = df.groupby('state_name')['SRI'].mean().sort_values(ascending=False)
    stats['top_5_high_risk_states'] = [
        {"state": state, "avg_sri": float(sri)}
        for state, sri in state_avg.head(5).items()
    ]

    # Top low-risk states
    stats['top_5_low_risk_states'] = [
        {"state": state, "avg_sri": float(sri)}
        for state, sri in state_avg.tail(5).items()
    ]

    return stats


@app.get("/reports/{year}/summary", tags=["Reports"])
async def get_market_summary(year: int):
    """
    Get market summary report for a specific year

    Returns HTML summary report
    """
    report_path = os.path.join(REPORTS_DIR, str(year), 'market_summary.html')

    if not os.path.exists(report_path):
        raise HTTPException(
            status_code=404,
            detail=f"Market summary report not found for year {year}"
        )

    return FileResponse(
        report_path,
        media_type="text/html",
        filename=f"market_summary_{year}.html"
    )


@app.get("/reports/{year}/download", tags=["Reports"])
async def download_sri_data(year: int):
    """
    Download full SRI data as CSV

    Returns CSV file for download
    """
    csv_path = os.path.join(DATA_DIR, str(year), 'sri_results.csv')

    if not os.path.exists(csv_path):
        raise HTTPException(
            status_code=404,
            detail=f"SRI data file not found for year {year}"
        )

    return FileResponse(
        csv_path,
        media_type="text/csv",
        filename=f"sri_results_{year}.csv"
    )


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "detail": str(exc.detail) if hasattr(exc, 'detail') else "Resource not found",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# =============================================================================
# STARTUP EVENT
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Log API startup"""
    logger.info("🚀 Agricultural SRI Market Data API starting...")
    available_years = get_available_years()
    logger.info(f"📊 Data available for years: {available_years}")
    logger.info("✅ API ready to serve requests")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
