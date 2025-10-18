"""
Data Validator - Production Module

Validates data quality for crop, weather, drought, and economic data
before processing and SRI calculation.
"""

import pandas as pd
import os
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def validate_crop_data(file_path: str) -> Tuple[bool, Dict]:
    """
    Validate crop yield data

    Checks:
    - File exists and is readable
    - Required columns present
    - Data completeness (no excessive nulls)
    - Data ranges (yield values are reasonable)

    Args:
        file_path: Path to crop data CSV

    Returns:
        (is_valid, validation_details)
    """
    logger.info("  Validating crop yield data...")

    validation = {
        'dataset': 'crop_yield',
        'passed': False,
        'errors': [],
        'warnings': [],
        'stats': {}
    }

    # Check file exists
    if not os.path.exists(file_path):
        validation['errors'].append(f"File not found: {file_path}")
        return False, validation

    try:
        df = pd.read_csv(file_path)

        # Check required columns
        required_columns = ['year', 'state_name', 'commodity', 'yield_per_acre']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            validation['errors'].append(f"Missing columns: {missing_columns}")
            return False, validation

        # Check data completeness
        null_counts = df[required_columns].isnull().sum()
        null_pct = (null_counts / len(df)) * 100

        for col, pct in null_pct.items():
            if pct > 20:  # More than 20% null is a problem
                validation['errors'].append(f"Column '{col}' has {pct:.1f}% null values")
            elif pct > 5:  # 5-20% null is a warning
                validation['warnings'].append(f"Column '{col}' has {pct:.1f}% null values")

        # Check yield values are reasonable (typically 20-300 bu/acre)
        yield_data = df['yield_per_acre'].dropna()

        if len(yield_data) == 0:
            validation['errors'].append("No valid yield data")
            return False, validation

        min_yield = yield_data.min()
        max_yield = yield_data.max()
        mean_yield = yield_data.mean()

        # Sanity checks
        if min_yield < 0:
            validation['errors'].append(f"Negative yield values found: {min_yield}")
        elif min_yield < 10:
            validation['warnings'].append(f"Very low minimum yield: {min_yield}")

        if max_yield > 500:
            validation['warnings'].append(f"Very high maximum yield: {max_yield}")

        # Check state coverage
        states_count = df['state_name'].nunique()
        commodities_count = df['commodity'].nunique()

        validation['stats'] = {
            'total_records': len(df),
            'states': states_count,
            'commodities': commodities_count,
            'min_yield': float(min_yield),
            'max_yield': float(max_yield),
            'mean_yield': float(mean_yield)
        }

        if states_count < 40:
            validation['warnings'].append(f"Low state coverage: {states_count} states (expected ~50)")

        # Determine pass/fail
        validation['passed'] = len(validation['errors']) == 0

        if validation['passed']:
            logger.info(f"    ✓ Crop data valid: {len(df)} records, {states_count} states")
        else:
            logger.error(f"    ❌ Crop data validation failed: {len(validation['errors'])} errors")

        return validation['passed'], validation

    except Exception as e:
        validation['errors'].append(f"Error reading file: {str(e)}")
        return False, validation


def validate_weather_data(file_path: str) -> Tuple[bool, Dict]:
    """
    Validate weather data

    Args:
        file_path: Path to weather data CSV

    Returns:
        (is_valid, validation_details)
    """
    logger.info("  Validating weather data...")

    validation = {
        'dataset': 'weather',
        'passed': False,
        'errors': [],
        'warnings': [],
        'stats': {}
    }

    if not os.path.exists(file_path):
        validation['errors'].append(f"File not found: {file_path}")
        return False, validation

    try:
        df = pd.read_csv(file_path)

        # Check required columns
        required_columns = ['state_name', 'year', 'avg_temp', 'total_precip', 'total_gdd']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            validation['errors'].append(f"Missing columns: {missing_columns}")
            return False, validation

        # Check temperature ranges (reasonable for US: -50 to 120°F)
        temp_data = df['avg_temp'].dropna()
        if len(temp_data) > 0:
            if temp_data.min() < -50 or temp_data.max() > 120:
                validation['warnings'].append(f"Temperature out of expected range: {temp_data.min():.1f} to {temp_data.max():.1f}°F")

        # Check precipitation (0-100 inches typical)
        precip_data = df['total_precip'].dropna()
        if len(precip_data) > 0:
            if precip_data.min() < 0:
                validation['errors'].append("Negative precipitation values")
            if precip_data.max() > 150:
                validation['warnings'].append(f"Very high precipitation: {precip_data.max():.1f} inches")

        # Check state coverage
        states_count = df['state_name'].nunique()

        validation['stats'] = {
            'total_records': len(df),
            'states': states_count,
            'avg_temp_mean': float(temp_data.mean()) if len(temp_data) > 0 else None,
            'avg_precip_mean': float(precip_data.mean()) if len(precip_data) > 0 else None
        }

        if states_count < 40:
            validation['warnings'].append(f"Low state coverage: {states_count} states")

        validation['passed'] = len(validation['errors']) == 0

        if validation['passed']:
            logger.info(f"    ✓ Weather data valid: {len(df)} records, {states_count} states")
        else:
            logger.error(f"    ❌ Weather data validation failed")

        return validation['passed'], validation

    except Exception as e:
        validation['errors'].append(f"Error reading file: {str(e)}")
        return False, validation


def validate_drought_data(file_path: str) -> Tuple[bool, Dict]:
    """
    Validate drought data

    Args:
        file_path: Path to drought data CSV

    Returns:
        (is_valid, validation_details)
    """
    logger.info("  Validating drought data...")

    validation = {
        'dataset': 'drought',
        'passed': False,
        'errors': [],
        'warnings': [],
        'stats': {}
    }

    if not os.path.exists(file_path):
        validation['errors'].append(f"File not found: {file_path}")
        return False, validation

    try:
        df = pd.read_csv(file_path)

        # Check required columns
        required_columns = ['state_name', 'year', 'avg_dsci']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            validation['errors'].append(f"Missing columns: {missing_columns}")
            return False, validation

        # Check DSCI ranges (0-100)
        dsci_data = df['avg_dsci'].dropna()
        if len(dsci_data) > 0:
            if dsci_data.min() < 0 or dsci_data.max() > 100:
                validation['errors'].append(f"DSCI out of valid range (0-100): {dsci_data.min():.1f} to {dsci_data.max():.1f}")

        # Check state coverage
        states_count = df['state_name'].nunique()

        validation['stats'] = {
            'total_records': len(df),
            'states': states_count,
            'avg_dsci_mean': float(dsci_data.mean()) if len(dsci_data) > 0 else None
        }

        if states_count < 40:
            validation['warnings'].append(f"Low state coverage: {states_count} states")

        validation['passed'] = len(validation['errors']) == 0

        if validation['passed']:
            logger.info(f"    ✓ Drought data valid: {len(df)} records, {states_count} states")
        else:
            logger.error(f"    ❌ Drought data validation failed")

        return validation['passed'], validation

    except Exception as e:
        validation['errors'].append(f"Error reading file: {str(e)}")
        return False, validation


def validate_economic_data(file_path: str) -> Tuple[bool, Dict]:
    """
    Validate economic data

    Args:
        file_path: Path to economic data CSV

    Returns:
        (is_valid, validation_details)
    """
    logger.info("  Validating economic data...")

    validation = {
        'dataset': 'economic',
        'passed': False,
        'errors': [],
        'warnings': [],
        'stats': {}
    }

    if not os.path.exists(file_path):
        validation['errors'].append(f"File not found: {file_path}")
        return False, validation

    try:
        df = pd.read_csv(file_path)

        # Check required columns
        required_columns = ['commodity', 'year', 'price_index']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            validation['errors'].append(f"Missing columns: {missing_columns}")
            return False, validation

        # Check commodity coverage
        commodities_count = df['commodity'].nunique()

        validation['stats'] = {
            'total_records': len(df),
            'commodities': commodities_count
        }

        if commodities_count < 3:
            validation['warnings'].append(f"Low commodity coverage: {commodities_count} commodities (expected 3)")

        validation['passed'] = len(validation['errors']) == 0

        if validation['passed']:
            logger.info(f"    ✓ Economic data valid: {len(df)} records, {commodities_count} commodities")
        else:
            logger.error(f"    ❌ Economic data validation failed")

        return validation['passed'], validation

    except Exception as e:
        validation['errors'].append(f"Error reading file: {str(e)}")
        return False, validation


def validate_all_data(crop_file: str, weather_file: str, drought_file: str, economic_file: str) -> Dict:
    """
    Validate all datasets

    Args:
        crop_file: Path to crop data CSV
        weather_file: Path to weather data CSV
        drought_file: Path to drought data CSV
        economic_file: Path to economic data CSV

    Returns:
        dict with overall validation results
    """
    logger.info("🔍 Validating all datasets...")

    results = {
        'overall_passed': False,
        'datasets': {},
        'total_errors': 0,
        'total_warnings': 0
    }

    # Validate each dataset
    datasets = [
        ('crop', crop_file, validate_crop_data),
        ('weather', weather_file, validate_weather_data),
        ('drought', drought_file, validate_drought_data),
        ('economic', economic_file, validate_economic_data)
    ]

    for dataset_name, file_path, validator_func in datasets:
        passed, validation = validator_func(file_path)
        results['datasets'][dataset_name] = validation
        results['total_errors'] += len(validation['errors'])
        results['total_warnings'] += len(validation['warnings'])

    # Overall pass = all datasets passed
    results['overall_passed'] = all(
        results['datasets'][name]['passed']
        for name in ['crop', 'weather', 'drought', 'economic']
    )

    if results['overall_passed']:
        logger.info(f"✅ All datasets valid ({results['total_warnings']} warnings)")
    else:
        logger.error(f"❌ Validation failed: {results['total_errors']} errors, {results['total_warnings']} warnings")

    return results


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) != 5:
        print("Usage: python data_validator.py <crop_file> <weather_file> <drought_file> <economic_file>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    result = validate_all_data(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print(f"\nValidation Result: {result}")
