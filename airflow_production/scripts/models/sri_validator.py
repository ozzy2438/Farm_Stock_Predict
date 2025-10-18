"""
SRI Validator - Production Module

Validates SRI calculation results for quality and reasonableness.
"""

import pandas as pd
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


def validate_sri_results(sri_file: str) -> Tuple[bool, Dict]:
    """
    Validate SRI calculation results

    Checks:
    - SRI values in valid range (0-100)
    - Risk components present and valid
    - Distribution is reasonable
    - No excessive outliers
    - State coverage adequate

    Args:
        sri_file: Path to SRI results CSV

    Returns:
        (is_valid, validation_details)
    """
    logger.info("🔍 Validating SRI results...")

    validation = {
        'passed': False,
        'errors': [],
        'warnings': [],
        'stats': {}
    }

    try:
        df = pd.read_csv(sri_file)

        # Check required columns
        required_columns = ['SRI', 'state_name', 'commodity', 'risk_category']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            validation['errors'].append(f"Missing columns: {missing_columns}")
            return False, validation

        # Check SRI range
        sri_data = df['SRI'].dropna()

        if len(sri_data) == 0:
            validation['errors'].append("No valid SRI values")
            return False, validation

        if sri_data.min() < 0 or sri_data.max() > 100:
            validation['errors'].append(f"SRI values out of range (0-100): {sri_data.min():.1f} to {sri_data.max():.1f}")

        # Check for NaN values
        nan_count = df['SRI'].isnull().sum()
        if nan_count > 0:
            validation['warnings'].append(f"{nan_count} records with missing SRI values")

        # Check risk component columns
        risk_components = ['yield_risk', 'weather_risk', 'drought_risk', 'economic_risk']
        available_components = [col for col in risk_components if col in df.columns]

        if len(available_components) < 4:
            validation['warnings'].append(f"Not all risk components present: {available_components}")

        # Validate component ranges
        for component in available_components:
            comp_data = df[component].dropna()
            if len(comp_data) > 0:
                if comp_data.min() < 0 or comp_data.max() > 100:
                    validation['warnings'].append(f"{component} has values outside 0-100 range")

        # Check distribution
        avg_sri = sri_data.mean()
        median_sri = sri_data.median()
        std_sri = sri_data.std()

        validation['stats'] = {
            'total_records': len(df),
            'avg_sri': float(avg_sri),
            'median_sri': float(median_sri),
            'std_sri': float(std_sri),
            'min_sri': float(sri_data.min()),
            'max_sri': float(sri_data.max())
        }

        # Sanity checks on distribution
        if avg_sri < 5 or avg_sri > 95:
            validation['warnings'].append(f"Unusual average SRI: {avg_sri:.1f} (expected 10-80)")

        if std_sri < 5:
            validation['warnings'].append(f"Very low SRI variance: {std_sri:.1f} (may indicate calculation issue)")

        # Check risk categories
        if 'risk_category' in df.columns:
            category_counts = df['risk_category'].value_counts().to_dict()
            validation['stats']['risk_categories'] = category_counts

            # All records in one category is suspicious
            if len(category_counts) == 1:
                validation['warnings'].append("All records in single risk category (unusual)")

        # Check state coverage
        states_count = df['state_name'].nunique()
        validation['stats']['states'] = states_count

        if states_count < 40:
            validation['warnings'].append(f"Low state coverage: {states_count} states (expected ~50)")

        # Check commodity coverage
        commodities_count = df['commodity'].nunique()
        validation['stats']['commodities'] = commodities_count

        if commodities_count < 3:
            validation['warnings'].append(f"Low commodity coverage: {commodities_count} commodities (expected 3)")

        # Check for outliers (SRI > 3 standard deviations from mean)
        outlier_threshold = avg_sri + (3 * std_sri)
        outliers = df[df['SRI'] > outlier_threshold]

        if len(outliers) > 0:
            validation['stats']['outliers'] = len(outliers)
            if len(outliers) > len(df) * 0.05:  # More than 5% outliers
                validation['warnings'].append(f"High number of outliers: {len(outliers)} records")

        # Overall pass/fail
        validation['passed'] = len(validation['errors']) == 0

        if validation['passed']:
            logger.info(f"  ✅ SRI validation passed")
            logger.info(f"     Average SRI: {avg_sri:.1f}, Range: {sri_data.min():.1f}-{sri_data.max():.1f}")
            logger.info(f"     {len(validation['warnings'])} warnings")
        else:
            logger.error(f"  ❌ SRI validation failed: {len(validation['errors'])} errors")

        return validation['passed'], validation

    except Exception as e:
        validation['errors'].append(f"Error validating SRI: {str(e)}")
        return False, validation


def check_sri_reasonableness(sri_file: str, expected_avg_range: Tuple[float, float] = (20, 40)) -> Dict:
    """
    Check if SRI results are reasonable based on historical context

    Args:
        sri_file: Path to SRI results CSV
        expected_avg_range: Expected range for average SRI

    Returns:
        dict with reasonableness check results
    """
    logger.info("  Checking SRI reasonableness...")

    results = {
        'reasonable': False,
        'issues': [],
        'metrics': {}
    }

    try:
        df = pd.read_csv(sri_file)
        avg_sri = df['SRI'].mean()

        results['metrics']['avg_sri'] = float(avg_sri)
        results['metrics']['expected_range'] = expected_avg_range

        # Check if average is in expected range
        if avg_sri < expected_avg_range[0]:
            results['issues'].append(f"Average SRI ({avg_sri:.1f}) below expected minimum ({expected_avg_range[0]})")
        elif avg_sri > expected_avg_range[1]:
            results['issues'].append(f"Average SRI ({avg_sri:.1f}) above expected maximum ({expected_avg_range[1]})")

        # Check high-risk percentage
        high_risk_pct = (df['SRI'] >= 50).sum() / len(df) * 100
        results['metrics']['high_risk_pct'] = float(high_risk_pct)

        if high_risk_pct > 30:
            results['issues'].append(f"High percentage of high-risk records: {high_risk_pct:.1f}% (expected < 30%)")
        elif high_risk_pct < 5:
            results['issues'].append(f"Very low percentage of high-risk records: {high_risk_pct:.1f}% (unusual)")

        # Check if any commodity is consistently high/low risk
        commodity_avg = df.groupby('commodity')['SRI'].mean()
        for commodity, avg in commodity_avg.items():
            if avg > 70:
                results['issues'].append(f"{commodity} has very high average SRI: {avg:.1f}")
            elif avg < 10:
                results['issues'].append(f"{commodity} has very low average SRI: {avg:.1f}")

        results['reasonable'] = len(results['issues']) == 0

        if results['reasonable']:
            logger.info("    ✓ SRI results appear reasonable")
        else:
            logger.warning(f"    ⚠️ {len(results['issues'])} reasonableness concerns")

        return results

    except Exception as e:
        results['issues'].append(f"Error: {str(e)}")
        return results


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) != 2:
        print("Usage: python sri_validator.py <sri_file>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)

    # Run validation
    passed, validation = validate_sri_results(sys.argv[1])
    print(f"\nValidation Result: {'PASSED' if passed else 'FAILED'}")
    print(f"Stats: {validation['stats']}")
    print(f"Errors: {validation['errors']}")
    print(f"Warnings: {validation['warnings']}")

    # Run reasonableness check
    reasonableness = check_sri_reasonableness(sys.argv[1])
    print(f"\nReasonableness: {'OK' if reasonableness['reasonable'] else 'ISSUES FOUND'}")
    print(f"Issues: {reasonableness['issues']}")
