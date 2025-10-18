"""
SRI Comparator - Production Module

Compares current year SRI results with previous year to identify trends.
"""

import pandas as pd
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def compare_sri_years(current_file: str, previous_file: str, output_dir: str, current_year: int) -> Dict:
    """
    Compare current year SRI with previous year

    Args:
        current_file: Path to current year SRI results CSV
        previous_file: Path to previous year SRI results CSV
        output_dir: Directory to save comparison results
        current_year: Current year

    Returns:
        dict with comparison results and file path
    """
    logger.info(f"📊 Comparing SRI: {current_year} vs {current_year-1}...")

    try:
        # Load both years
        df_current = pd.read_csv(current_file)
        df_previous = pd.read_csv(previous_file)

        logger.info(f"  Current year: {len(df_current)} records")
        logger.info(f"  Previous year: {len(df_previous)} records")

        # Merge on state and commodity
        comparison = df_current[['state_name', 'commodity', 'SRI', 'risk_category']].merge(
            df_previous[['state_name', 'commodity', 'SRI', 'risk_category']],
            on=['state_name', 'commodity'],
            how='left',
            suffixes=(f'_{current_year}', f'_{current_year-1}')
        )

        # Calculate changes
        comparison[f'SRI_{current_year}'] = comparison[f'SRI_{current_year}'].fillna(0)
        comparison[f'SRI_{current_year-1}'] = comparison[f'SRI_{current_year-1}'].fillna(0)

        comparison['SRI_change'] = comparison[f'SRI_{current_year}'] - comparison[f'SRI_{current_year-1}']
        comparison['SRI_change_pct'] = (
            (comparison['SRI_change'] / comparison[f'SRI_{current_year-1}']) * 100
        ).replace([float('inf'), -float('inf')], 0)

        # Categorize trend
        def categorize_trend(change):
            if abs(change) < 5:
                return 'Stable'
            elif change >= 5:
                return 'Increasing Risk'
            else:
                return 'Decreasing Risk'

        comparison['trend'] = comparison['SRI_change'].apply(categorize_trend)

        # Identify significant changes
        comparison['significant_change'] = abs(comparison['SRI_change']) >= 10

        # Sort by change (biggest increases first)
        comparison = comparison.sort_values('SRI_change', ascending=False).reset_index(drop=True)

        # Save comparison
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'sri_comparison_{current_year}.csv')
        comparison.to_csv(output_file, index=False)

        # Generate statistics
        stats = {
            'current_year': current_year,
            'previous_year': current_year - 1,
            'total_comparisons': len(comparison),
            'national_avg_current': float(comparison[f'SRI_{current_year}'].mean()),
            'national_avg_previous': float(comparison[f'SRI_{current_year-1}'].mean()),
            'national_avg_change': float(comparison['SRI_change'].mean()),
            'trend_distribution': {
                'increasing_risk': int((comparison['trend'] == 'Increasing Risk').sum()),
                'stable': int((comparison['trend'] == 'Stable').sum()),
                'decreasing_risk': int((comparison['trend'] == 'Decreasing Risk').sum())
            },
            'significant_changes': int(comparison['significant_change'].sum())
        }

        # Identify top increasing and decreasing risks
        top_increasing = comparison.nlargest(10, 'SRI_change')[
            ['state_name', 'commodity', f'SRI_{current_year}', f'SRI_{current_year-1}', 'SRI_change']
        ].to_dict('records')

        top_decreasing = comparison.nsmallest(10, 'SRI_change')[
            ['state_name', 'commodity', f'SRI_{current_year}', f'SRI_{current_year-1}', 'SRI_change']
        ].to_dict('records')

        stats['top_10_increasing'] = top_increasing
        stats['top_10_decreasing'] = top_decreasing

        logger.info(f"✅ Comparison complete")
        logger.info(f"   National avg change: {stats['national_avg_change']:+.1f} points")
        logger.info(f"   Increasing risk: {stats['trend_distribution']['increasing_risk']} records")
        logger.info(f"   Decreasing risk: {stats['trend_distribution']['decreasing_risk']} records")
        logger.info(f"   Results saved to: {output_file}")

        return {
            'success': True,
            'file_path': output_file,
            'stats': stats
        }

    except FileNotFoundError as e:
        logger.warning(f"⚠️ Previous year data not found: {str(e)}")
        return {
            'success': False,
            'file_path': None,
            'stats': None,
            'error': 'Previous year data not available (first run?)'
        }
    except Exception as e:
        logger.error(f"❌ Error comparing SRI: {str(e)}")
        return {
            'success': False,
            'file_path': None,
            'stats': None,
            'error': str(e)
        }


def generate_trend_summary(comparison_file: str) -> Dict:
    """
    Generate summary of SRI trends from comparison

    Args:
        comparison_file: Path to comparison results CSV

    Returns:
        dict with trend summary
    """
    logger.info("  Generating trend summary...")

    try:
        df = pd.read_csv(comparison_file)

        summary = {
            'states_with_increasing_risk': [],
            'states_with_decreasing_risk': [],
            'commodities_with_increasing_risk': [],
            'key_findings': []
        }

        # States with overall increasing risk
        state_avg = df.groupby('state_name')['SRI_change'].mean()
        increasing_states = state_avg[state_avg >= 5].sort_values(ascending=False)
        decreasing_states = state_avg[state_avg <= -5].sort_values()

        summary['states_with_increasing_risk'] = [
            {'state': state, 'avg_change': float(change)}
            for state, change in increasing_states.head(10).items()
        ]

        summary['states_with_decreasing_risk'] = [
            {'state': state, 'avg_change': float(change)}
            for state, change in decreasing_states.head(10).items()
        ]

        # Commodities with increasing risk
        commodity_avg = df.groupby('commodity')['SRI_change'].mean()
        summary['commodities_with_increasing_risk'] = [
            {'commodity': commodity, 'avg_change': float(change)}
            for commodity, change in commodity_avg.items()
        ]

        # Key findings
        if len(increasing_states) > len(decreasing_states):
            summary['key_findings'].append(f"More states showing increased risk ({len(increasing_states)}) than decreased ({len(decreasing_states)})")

        significant_increases = (df['SRI_change'] >= 20).sum()
        if significant_increases > 0:
            summary['key_findings'].append(f"{significant_increases} state-commodity combinations show major risk increases (>20 points)")

        logger.info("    ✓ Trend summary generated")

        return summary

    except Exception as e:
        logger.error(f"    ❌ Error generating trend summary: {str(e)}")
        return {
            'error': str(e)
        }


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) != 4:
        print("Usage: python sri_comparator.py <current_file> <previous_file> <output_dir>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    result = compare_sri_years(
        current_file=sys.argv[1],
        previous_file=sys.argv[2],
        output_dir=sys.argv[3],
        current_year=2024
    )
    print(f"\nComparison Result: {result}")

    if result['success']:
        summary = generate_trend_summary(result['file_path'])
        print(f"\nTrend Summary: {summary}")
