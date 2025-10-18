"""
SRI Calculator - Production Module

Calculates Stock Risk Index (SRI) based on merged agricultural data.

SRI Formula:
SRI = w1*YieldRisk + w2*WeatherRisk + w3*DroughtRisk + w4*EconomicRisk

Where:
- YieldRisk: Based on yield deviation from average
- WeatherRisk: Based on temperature stress and precipitation deficit
- DroughtRisk: Based on DSCI score
- EconomicRisk: Based on supply risk indicators
"""

import pandas as pd
import numpy as np
import os
import logging
from typing import Dict
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)

# SRI Component Weights
WEIGHTS = {
    'yield_risk': 0.35,      # 35% - Most important
    'weather_risk': 0.25,    # 25%
    'drought_risk': 0.25,    # 25%
    'economic_risk': 0.15    # 15%
}


def calculate_yield_risk(df: pd.DataFrame) -> pd.Series:
    """
    Calculate yield risk component

    Lower yield = higher risk
    Uses z-score: negative z-score means below average yield

    Args:
        df: DataFrame with 'yield_zscore' column

    Returns:
        Series with yield risk scores (0-100)
    """
    # Invert z-score: negative z-score (low yield) = high risk
    # Convert to 0-100 scale
    yield_risk = df['yield_zscore'].apply(lambda z: max(0, min(100, 50 - (z * 20))))

    return yield_risk


def calculate_weather_risk(df: pd.DataFrame) -> pd.Series:
    """
    Calculate weather risk component

    Based on:
    - Temperature stress (deviation from optimal)
    - Precipitation deficit
    - Low GDD (growing degree days)

    Args:
        df: DataFrame with weather columns

    Returns:
        Series with weather risk scores (0-100)
    """
    # Temperature stress (0-20 range, normalize to 0-40)
    temp_risk = (df['temp_stress'] / 20) * 40

    # Precipitation deficit (0-30 inches, normalize to 0-40)
    precip_risk = (df['precip_deficit'] / 30) * 40

    # GDD risk (low GDD = high risk)
    # Typical GDD range: 1000-4000, below 1500 is concerning
    gdd_risk = df['total_gdd'].apply(
        lambda gdd: max(0, min(20, (1500 - gdd) / 50)) if pd.notna(gdd) else 10
    )

    # Combine (60% temp/precip, 40% GDD)
    weather_risk = (temp_risk * 0.3) + (precip_risk * 0.3) + (gdd_risk * 0.4)

    # Ensure 0-100 range
    weather_risk = weather_risk.clip(0, 100)

    return weather_risk


def calculate_drought_risk(df: pd.DataFrame) -> pd.Series:
    """
    Calculate drought risk component

    Based on DSCI (Drought Severity and Coverage Index)
    DSCI is already 0-100, so use directly

    Args:
        df: DataFrame with 'avg_dsci' column

    Returns:
        Series with drought risk scores (0-100)
    """
    # DSCI is already a risk score (0-100)
    drought_risk = df['avg_dsci'].fillna(0)

    return drought_risk


def calculate_economic_risk(df: pd.DataFrame) -> pd.Series:
    """
    Calculate economic risk component

    Based on:
    - Supply risk score from economic data
    - Price index (high prices may indicate supply concerns)

    Args:
        df: DataFrame with economic columns

    Returns:
        Series with economic risk scores (0-100)
    """
    # Supply risk score (already 0-100)
    supply_risk = df['supply_risk_score'].fillna(50)

    # Price risk (prices above 120 or below 80 indicate market stress)
    price_risk = df['price_index'].apply(
        lambda p: abs(p - 100) / 2 if pd.notna(p) else 0
    ).clip(0, 50)

    # Combine (70% supply, 30% price)
    economic_risk = (supply_risk * 0.7) + (price_risk * 0.3)

    return economic_risk


def calculate_sri(merged_file: str, output_dir: str, year: int) -> Dict:
    """
    Calculate SRI for all state-commodity combinations

    Args:
        merged_file: Path to merged data CSV
        output_dir: Directory to save SRI results
        year: Year being processed

    Returns:
        dict with file_path and statistics
    """
    logger.info("📊 Calculating Stock Risk Index (SRI)...")

    try:
        # Load merged data
        df = pd.read_csv(merged_file)
        logger.info(f"  Loaded {len(df)} records")

        # Calculate individual risk components
        logger.info("  Calculating risk components...")

        df['yield_risk'] = calculate_yield_risk(df)
        logger.info("    ✓ Yield risk calculated")

        df['weather_risk'] = calculate_weather_risk(df)
        logger.info("    ✓ Weather risk calculated")

        df['drought_risk'] = calculate_drought_risk(df)
        logger.info("    ✓ Drought risk calculated")

        df['economic_risk'] = calculate_economic_risk(df)
        logger.info("    ✓ Economic risk calculated")

        # Calculate weighted SRI
        logger.info("  Calculating SRI...")

        df['SRI'] = (
            df['yield_risk'] * WEIGHTS['yield_risk'] +
            df['weather_risk'] * WEIGHTS['weather_risk'] +
            df['drought_risk'] * WEIGHTS['drought_risk'] +
            df['economic_risk'] * WEIGHTS['economic_risk']
        )

        # Ensure SRI is in 0-100 range
        df['SRI'] = df['SRI'].clip(0, 100)

        # Add risk category
        def categorize_risk(sri):
            if sri < 25:
                return 'Low'
            elif sri < 50:
                return 'Moderate'
            elif sri < 75:
                return 'High'
            else:
                return 'Very High'

        df['risk_category'] = df['SRI'].apply(categorize_risk)

        # Add stockpile recommendation
        def recommend_stockpile(sri):
            if sri < 25:
                return 'Normal inventory'
            elif sri < 50:
                return 'Monitor closely, consider +5% stockpile'
            elif sri < 75:
                return 'Increase stockpile by +15%'
            else:
                return 'Critical: Increase stockpile by +25%'

        df['recommendation'] = df['SRI'].apply(recommend_stockpile)

        # Select output columns
        output_columns = [
            'year',
            'state_name',
            'commodity',
            'yield_per_acre',
            'yield_risk',
            'weather_risk',
            'drought_risk',
            'economic_risk',
            'SRI',
            'risk_category',
            'recommendation',
            'avg_temp',
            'total_precip',
            'avg_dsci'
        ]

        # Filter to available columns
        output_columns = [col for col in output_columns if col in df.columns]

        sri_results = df[output_columns].copy()

        # Sort by SRI descending (highest risk first)
        sri_results = sri_results.sort_values('SRI', ascending=False).reset_index(drop=True)

        # Save results
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'sri_results_{year}.csv')
        sri_results.to_csv(output_file, index=False)

        # Generate statistics
        stats = {
            'year': year,
            'total_records': len(sri_results),
            'avg_sri': float(sri_results['SRI'].mean()),
            'median_sri': float(sri_results['SRI'].median()),
            'min_sri': float(sri_results['SRI'].min()),
            'max_sri': float(sri_results['SRI'].max()),
            'risk_distribution': {
                'low': int((sri_results['risk_category'] == 'Low').sum()),
                'moderate': int((sri_results['risk_category'] == 'Moderate').sum()),
                'high': int((sri_results['risk_category'] == 'High').sum()),
                'very_high': int((sri_results['risk_category'] == 'Very High').sum())
            },
            'high_risk_states': sri_results[sri_results['SRI'] >= 50]['state_name'].nunique(),
            'component_averages': {
                'yield_risk': float(sri_results['yield_risk'].mean()),
                'weather_risk': float(sri_results['weather_risk'].mean()),
                'drought_risk': float(sri_results['drought_risk'].mean()),
                'economic_risk': float(sri_results['economic_risk'].mean())
            }
        }

        logger.info(f"✅ SRI calculated for {len(sri_results)} records")
        logger.info(f"   Average SRI: {stats['avg_sri']:.1f}")
        logger.info(f"   High-risk records: {stats['risk_distribution']['high'] + stats['risk_distribution']['very_high']}")
        logger.info(f"   Results saved to: {output_file}")

        return {
            'success': True,
            'file_path': output_file,
            'records': len(sri_results),
            'stats': stats
        }

    except Exception as e:
        logger.error(f"❌ Error calculating SRI: {str(e)}")
        return {
            'success': False,
            'file_path': None,
            'records': 0,
            'error': str(e)
        }


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) != 3:
        print("Usage: python sri_calculator.py <merged_file> <output_dir>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    result = calculate_sri(
        merged_file=sys.argv[1],
        output_dir=sys.argv[2],
        year=2024
    )
    print(f"\nSRI Calculation Result: {result}")
