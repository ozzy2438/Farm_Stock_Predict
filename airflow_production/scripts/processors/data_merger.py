"""
Data Merger - Production Module

Merges validated crop, weather, drought, and economic data
into a single dataset for SRI calculation.
"""

import pandas as pd
import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def merge_all_data(
    crop_file: str,
    weather_file: str,
    drought_file: str,
    economic_file: str,
    output_dir: str,
    year: int
) -> Dict:
    """
    Merge all datasets into a single DataFrame

    Merge strategy:
    1. Start with crop data (state × commodity level)
    2. Left join weather data (state level)
    3. Left join drought data (state level)
    4. Left join economic data (commodity level)

    Args:
        crop_file: Path to crop data CSV
        weather_file: Path to weather data CSV
        drought_file: Path to drought data CSV
        economic_file: Path to economic data CSV
        output_dir: Directory to save merged data
        year: Year being processed

    Returns:
        dict with file_path and statistics
    """
    logger.info("🔗 Merging all datasets...")

    try:
        # Load all datasets
        logger.info("  Loading datasets...")
        df_crop = pd.read_csv(crop_file)
        df_weather = pd.read_csv(weather_file)
        df_drought = pd.read_csv(drought_file)
        df_economic = pd.read_csv(economic_file)

        logger.info(f"    Crop: {len(df_crop)} records")
        logger.info(f"    Weather: {len(df_weather)} records")
        logger.info(f"    Drought: {len(df_drought)} records")
        logger.info(f"    Economic: {len(df_economic)} records")

        # Standardize state names (ensure consistent capitalization)
        df_crop['state_name'] = df_crop['state_name'].str.strip()
        df_weather['state_name'] = df_weather['state_name'].str.strip()
        df_drought['state_name'] = df_drought['state_name'].str.strip()

        # Standardize commodity names
        df_crop['commodity'] = df_crop['commodity'].str.upper().str.strip()
        df_economic['commodity'] = df_economic['commodity'].str.upper().str.strip()

        # Start with crop data as base
        logger.info("  Merging datasets...")
        merged = df_crop.copy()

        # Merge weather data (state level)
        merged = merged.merge(
            df_weather,
            on=['state_name', 'year'],
            how='left',
            suffixes=('', '_weather')
        )

        logger.info(f"    After weather merge: {len(merged)} records")

        # Merge drought data (state level)
        merged = merged.merge(
            df_drought,
            on=['state_name', 'year'],
            how='left',
            suffixes=('', '_drought')
        )

        logger.info(f"    After drought merge: {len(merged)} records")

        # Merge economic data (commodity level)
        merged = merged.merge(
            df_economic[['commodity', 'year', 'price_index', 'supply_risk_score']],
            on=['commodity', 'year'],
            how='left',
            suffixes=('', '_economic')
        )

        logger.info(f"    After economic merge: {len(merged)} records")

        # Check for missing data after merge
        logger.info("  Checking data completeness...")

        # Key columns to check
        key_columns = [
            'yield_per_acre',
            'avg_temp',
            'total_precip',
            'total_gdd',
            'avg_dsci',
            'price_index'
        ]

        missing_counts = merged[key_columns].isnull().sum()
        total_rows = len(merged)

        for col, count in missing_counts.items():
            if count > 0:
                pct = (count / total_rows) * 100
                if pct > 10:
                    logger.warning(f"    ⚠️ {col}: {count} missing ({pct:.1f}%)")
                else:
                    logger.info(f"    {col}: {count} missing ({pct:.1f}%)")

        # Handle missing values
        logger.info("  Handling missing values...")

        # Fill missing weather data with state averages
        for col in ['avg_temp', 'total_precip', 'total_gdd', 'avg_humidity']:
            if col in merged.columns:
                state_means = merged.groupby('state_name')[col].transform('mean')
                merged[col] = merged[col].fillna(state_means)

        # Fill missing drought data with 0 (no drought)
        if 'avg_dsci' in merged.columns:
            merged['avg_dsci'] = merged['avg_dsci'].fillna(0)

        # Fill missing economic data with neutral values
        if 'price_index' in merged.columns:
            merged['price_index'] = merged['price_index'].fillna(100)
        if 'supply_risk_score' in merged.columns:
            merged['supply_risk_score'] = merged['supply_risk_score'].fillna(50)

        # Remove any rows with missing yield (critical data)
        before_drop = len(merged)
        merged = merged.dropna(subset=['yield_per_acre'])
        after_drop = len(merged)

        if before_drop > after_drop:
            logger.warning(f"    Dropped {before_drop - after_drop} rows with missing yield data")

        # Add derived features
        logger.info("  Creating derived features...")

        # Normalize yield by commodity (z-score within commodity)
        merged['yield_zscore'] = merged.groupby('commodity')['yield_per_acre'].transform(
            lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
        )

        # Temperature stress indicator (deviation from optimal 70-80°F)
        if 'avg_temp' in merged.columns:
            merged['temp_stress'] = merged['avg_temp'].apply(
                lambda x: abs(x - 75) if pd.notna(x) else 0
            )

        # Precipitation deficit indicator (< 20 inches is low)
        if 'total_precip' in merged.columns:
            merged['precip_deficit'] = merged['total_precip'].apply(
                lambda x: max(0, 20 - x) if pd.notna(x) else 0
            )

        # Sort by state and commodity
        merged = merged.sort_values(['state_name', 'commodity']).reset_index(drop=True)

        # Save merged data
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'merged_data_{year}.csv')
        merged.to_csv(output_file, index=False)

        # Generate statistics
        stats = {
            'year': year,
            'total_records': len(merged),
            'states': merged['state_name'].nunique(),
            'commodities': merged['commodity'].nunique(),
            'columns': list(merged.columns),
            'completeness': {
                col: float(100 - (merged[col].isnull().sum() / len(merged)) * 100)
                for col in key_columns
                if col in merged.columns
            }
        }

        logger.info(f"✅ Merged data saved to {output_file}")
        logger.info(f"   Final dataset: {len(merged)} records, {merged['state_name'].nunique()} states, {merged['commodity'].nunique()} commodities")

        return {
            'success': True,
            'file_path': output_file,
            'records': len(merged),
            'stats': stats
        }

    except Exception as e:
        logger.error(f"❌ Error merging data: {str(e)}")
        return {
            'success': False,
            'file_path': None,
            'records': 0,
            'error': str(e)
        }


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) != 6:
        print("Usage: python data_merger.py <crop_file> <weather_file> <drought_file> <economic_file> <output_dir>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    result = merge_all_data(
        crop_file=sys.argv[1],
        weather_file=sys.argv[2],
        drought_file=sys.argv[3],
        economic_file=sys.argv[4],
        output_dir=sys.argv[5],
        year=2024
    )
    print(f"\nMerge Result: {result}")
