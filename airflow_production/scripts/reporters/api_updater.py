"""
API Updater - Production Module

Updates the FastAPI database with latest SRI results for API access.
"""

import pandas as pd
import os
import shutil
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def update_api_data(sri_file: str, api_data_dir: str, year: int) -> Dict:
    """
    Update API data directory with latest SRI results

    This copies SRI results to the API's data directory where
    the FastAPI server can access it.

    Args:
        sri_file: Path to SRI results CSV
        api_data_dir: API data directory path
        year: Year of the data

    Returns:
        dict with update results
    """
    logger.info("🔄 Updating API data...")

    try:
        # Create API data directory structure
        year_dir = os.path.join(api_data_dir, str(year))
        os.makedirs(year_dir, exist_ok=True)

        # Copy SRI results to API directory
        api_sri_file = os.path.join(year_dir, 'sri_results.csv')
        shutil.copy2(sri_file, api_sri_file)

        logger.info(f"  ✓ Copied SRI results to API directory")

        # Load data for validation
        df = pd.read_csv(api_sri_file)

        # Create API metadata file
        metadata = {
            'year': year,
            'total_records': len(df),
            'states': df['state_name'].nunique(),
            'commodities': df['commodity'].nunique(),
            'avg_sri': float(df['SRI'].mean()),
            'high_risk_count': int((df['SRI'] >= 50).sum()),
            'data_file': 'sri_results.csv',
            'updated': pd.Timestamp.now().isoformat()
        }

        # Save metadata
        metadata_file = os.path.join(year_dir, 'metadata.json')
        import json
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"  ✓ Created metadata file")

        # Update "latest" symlink or copy
        latest_dir = os.path.join(api_data_dir, 'latest')

        # Remove existing latest directory if it exists
        if os.path.exists(latest_dir):
            if os.path.islink(latest_dir):
                os.unlink(latest_dir)
            else:
                shutil.rmtree(latest_dir)

        # Create symlink to latest year (or copy on Windows)
        try:
            os.symlink(year_dir, latest_dir)
            logger.info(f"  ✓ Created 'latest' symlink to {year}")
        except OSError:
            # Windows or filesystem doesn't support symlinks, copy instead
            shutil.copytree(year_dir, latest_dir)
            logger.info(f"  ✓ Copied data to 'latest' directory")

        logger.info(f"✅ API data updated successfully")
        logger.info(f"   API can now serve data at: /sri/latest and /sri/{year}")

        return {
            'success': True,
            'api_data_dir': api_data_dir,
            'year': year,
            'records': len(df),
            'metadata': metadata
        }

    except Exception as e:
        logger.error(f"❌ Error updating API data: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def update_api_index(api_data_dir: str) -> Dict:
    """
    Update API index with all available years

    Args:
        api_data_dir: API data directory path

    Returns:
        dict with index update results
    """
    logger.info("  Updating API index...")

    try:
        # Find all year directories
        years = []
        for item in os.listdir(api_data_dir):
            item_path = os.path.join(api_data_dir, item)
            if os.path.isdir(item_path) and item.isdigit():
                years.append(int(item))

        years = sorted(years, reverse=True)

        # Create index
        index = {
            'available_years': years,
            'latest_year': years[0] if years else None,
            'total_years': len(years),
            'updated': pd.Timestamp.now().isoformat()
        }

        # Save index
        index_file = os.path.join(api_data_dir, 'index.json')
        import json
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)

        logger.info(f"  ✓ API index updated: {len(years)} years available")

        return {
            'success': True,
            'available_years': years
        }

    except Exception as e:
        logger.error(f"  ❌ Error updating API index: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) != 3:
        print("Usage: python api_updater.py <sri_file> <api_data_dir>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    result = update_api_data(
        sri_file=sys.argv[1],
        api_data_dir=sys.argv[2],
        year=2024
    )
    print(f"\nAPI Update Result: {result}")

    if result['success']:
        index_result = update_api_index(sys.argv[2])
        print(f"Index Update Result: {index_result}")
