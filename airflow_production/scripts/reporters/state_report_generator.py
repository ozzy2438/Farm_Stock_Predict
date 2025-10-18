"""
State Report Generator - Production Module

Generates individual state-level CSV reports from SRI results.
"""

import pandas as pd
import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def generate_state_reports(sri_file: str, output_dir: str, year: int) -> Dict:
    """
    Generate individual CSV reports for each state

    Args:
        sri_file: Path to SRI results CSV
        output_dir: Directory to save state reports
        year: Year of the report

    Returns:
        dict with file paths and statistics
    """
    logger.info("📁 Generating state-level reports...")

    try:
        # Load SRI data
        df = pd.read_csv(sri_file)
        logger.info(f"  Loaded {len(df)} SRI records")

        # Create states directory
        states_dir = os.path.join(output_dir, 'states')
        os.makedirs(states_dir, exist_ok=True)

        states = df['state_name'].unique()
        generated_files = []

        for state in states:
            # Filter data for this state
            state_data = df[df['state_name'] == state].copy()

            # Sort by SRI descending
            state_data = state_data.sort_values('SRI', ascending=False)

            # Select relevant columns
            columns = [
                'year',
                'state_name',
                'commodity',
                'yield_per_acre',
                'SRI',
                'risk_category',
                'recommendation',
                'yield_risk',
                'weather_risk',
                'drought_risk',
                'economic_risk'
            ]

            # Filter to available columns
            available_columns = [col for col in columns if col in state_data.columns]
            state_report = state_data[available_columns]

            # Add state summary at the top
            summary_row = {
                'year': year,
                'state_name': f"{state} - SUMMARY",
                'commodity': 'ALL',
                'SRI': state_data['SRI'].mean(),
                'risk_category': f"Avg: {state_data['SRI'].mean():.1f}",
            }

            # Create summary DataFrame
            summary_df = pd.DataFrame([summary_row])

            # Combine summary and detail
            final_report = pd.concat([summary_df, state_report], ignore_index=True)

            # Save to CSV
            safe_state_name = state.replace(' ', '_')
            output_file = os.path.join(states_dir, f'{safe_state_name}_{year}.csv')
            final_report.to_csv(output_file, index=False)

            generated_files.append(output_file)

        logger.info(f"✅ Generated {len(generated_files)} state reports")
        logger.info(f"   Saved to: {states_dir}")

        return {
            'success': True,
            'output_dir': states_dir,
            'files_generated': len(generated_files),
            'file_paths': generated_files
        }

    except Exception as e:
        logger.error(f"❌ Error generating state reports: {str(e)}")
        return {
            'success': False,
            'output_dir': None,
            'files_generated': 0,
            'error': str(e)
        }


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) != 3:
        print("Usage: python state_report_generator.py <sri_file> <output_dir>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    result = generate_state_reports(
        sri_file=sys.argv[1],
        output_dir=sys.argv[2],
        year=2024
    )
    print(f"\nState Reports Result: {result}")
