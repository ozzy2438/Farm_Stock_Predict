"""
Crop Data Collector - Production Module

Fetches crop yield data from USDA NASS QuickStats API
for Corn, Soybeans, and Wheat across all 50 US states.
"""

import requests
import pandas as pd
import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# USDA NASS API Configuration
USDA_API_BASE_URL = "https://quickstats.nass.usda.gov/api/api_GET/"
COMMODITIES = ["CORN", "SOYBEANS", "WHEAT"]


def fetch_all_crop_data(year: int, output_dir: str, api_key: str = None) -> Dict:
    """
    Fetch crop yield data for all commodities

    Args:
        year: Year to fetch data for
        output_dir: Directory to save output file
        api_key: USDA API key (defaults to env variable)

    Returns:
        dict with file_path and statistics
    """
    logger.info(f"🌾 Fetching crop yield data for {year}")

    # Get API key
    if api_key is None:
        api_key = os.getenv('USDA_API_KEY', '2EEF90B1-825E-322B-8B27-098A9C92D575')

    all_data = []
    stats = {
        'year': year,
        'commodities': {},
        'total_records': 0
    }

    for commodity in COMMODITIES:
        logger.info(f"  Fetching {commodity}...")

        params = {
            'key': api_key,
            'commodity_desc': commodity,
            'statisticcat_desc': 'YIELD',
            'agg_level_desc': 'STATE',
            'year': str(year),
            'format': 'JSON'
        }

        try:
            response = requests.get(USDA_API_BASE_URL, params=params, timeout=60)

            if response.status_code == 200:
                data = response.json().get('data', [])

                if data:
                    df = pd.DataFrame(data)

                    # Filter out aggregates
                    df = df[df['state_name'] != 'OTHER STATES']

                    # Select columns
                    df = df[['year', 'state_name', 'Value']]
                    df['commodity'] = commodity

                    # Clean Value column
                    df['Value'] = (
                        df['Value']
                        .astype(str)
                        .str.replace(',', '', regex=False)
                        .str.strip()
                    )

                    # Remove disclosure codes
                    df = df[~df['Value'].isin(['(D)', '(NA)', '(Z)', '(X)', ''])]

                    # Convert to numeric
                    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
                    df = df.dropna(subset=['Value'])

                    # Rename for clarity
                    df = df.rename(columns={'Value': 'yield_per_acre'})

                    all_data.append(df)

                    stats['commodities'][commodity] = len(df)
                    logger.info(f"    ✓ {commodity}: {len(df)} records")
                else:
                    logger.warning(f"    ⚠️ {commodity}: No data returned")
                    stats['commodities'][commodity] = 0

            elif response.status_code == 413:
                logger.error(f"    ❌ {commodity}: Payload too large (413)")
                stats['commodities'][commodity] = 0
            else:
                logger.error(f"    ❌ {commodity}: HTTP {response.status_code}")
                stats['commodities'][commodity] = 0

        except Exception as e:
            logger.error(f"    ❌ {commodity}: {str(e)}")
            stats['commodities'][commodity] = 0

    # Combine all data
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df = final_df.sort_values(['commodity', 'state_name']).reset_index(drop=True)

        # Save to file
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'crop_yield_{year}.csv')
        final_df.to_csv(output_file, index=False)

        stats['total_records'] = len(final_df)
        stats['states'] = final_df['state_name'].nunique()

        logger.info(f"✅ Saved {len(final_df):,} records to {output_file}")

        return {
            'success': True,
            'file_path': output_file,
            'records': len(final_df),
            'stats': stats
        }
    else:
        logger.error("❌ No crop data collected")
        return {
            'success': False,
            'file_path': None,
            'records': 0,
            'stats': stats
        }


if __name__ == "__main__":
    # Test the module
    import sys
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './test_output'

    logging.basicConfig(level=logging.INFO)
    result = fetch_all_crop_data(year=year, output_dir=output_dir)
    print(f"\nResult: {result}")
