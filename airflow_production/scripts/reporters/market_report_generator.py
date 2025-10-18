"""
Market Report Generator - Production Module

Generates comprehensive market summary report from SRI results.
"""

import pandas as pd
import os
import logging
import base64
from typing import Dict
from jinja2 import Template
from datetime import datetime

logger = logging.getLogger(__name__)


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode image file to base64 string for embedding in HTML

    Args:
        image_path: Path to image file

    Returns:
        Base64 encoded string with data URI prefix
    """
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/png;base64,{base64_data}"
    except Exception as e:
        logger.warning(f"Could not encode image {image_path}: {str(e)}")
        return ""


def generate_executive_summary(df: pd.DataFrame) -> Dict:
    """
    Generate executive summary statistics

    Args:
        df: DataFrame with SRI results

    Returns:
        dict with summary statistics
    """
    summary = {
        'national_avg_sri': float(df['SRI'].mean()),
        'median_sri': float(df['SRI'].median()),
        'total_states': df['state_name'].nunique(),
        'total_commodities': df['commodity'].nunique(),
        'risk_distribution': {
            'low': int((df['risk_category'] == 'Low').sum()),
            'moderate': int((df['risk_category'] == 'Moderate').sum()),
            'high': int((df['risk_category'] == 'High').sum()),
            'very_high': int((df['risk_category'] == 'Very High').sum())
        },
        'high_risk_states': df[df['SRI'] >= 50]['state_name'].nunique(),
        'very_high_risk_records': int((df['SRI'] >= 75).sum())
    }

    # Determine overall risk level
    if summary['national_avg_sri'] < 25:
        summary['overall_risk_level'] = 'Low'
    elif summary['national_avg_sri'] < 50:
        summary['overall_risk_level'] = 'Moderate'
    elif summary['national_avg_sri'] < 75:
        summary['overall_risk_level'] = 'High'
    else:
        summary['overall_risk_level'] = 'Very High'

    # Calculate recommended national stockpile adjustment
    if summary['national_avg_sri'] < 25:
        summary['recommended_stockpile_change'] = 'Normal inventory levels'
    elif summary['national_avg_sri'] < 35:
        summary['recommended_stockpile_change'] = '+5% increase recommended'
    elif summary['national_avg_sri'] < 50:
        summary['recommended_stockpile_change'] = '+10-15% increase recommended'
    elif summary['national_avg_sri'] < 75:
        summary['recommended_stockpile_change'] = '+15-20% increase recommended'
    else:
        summary['recommended_stockpile_change'] = '+20-25% increase CRITICAL'

    return summary


def get_top_risk_states(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """
    Get top N high-risk states

    Args:
        df: DataFrame with SRI results
        n: Number of top states to return

    Returns:
        DataFrame with top risk states
    """
    # Group by state and get average SRI
    state_avg = df.groupby('state_name').agg({
        'SRI': 'mean',
        'commodity': lambda x: ', '.join(x.unique())
    }).reset_index()

    state_avg = state_avg.rename(columns={'commodity': 'commodities'})
    state_avg = state_avg.sort_values('SRI', ascending=False).head(n)

    # Add recommendation
    def get_recommendation(sri):
        if sri >= 75:
            return '+25% stockpile'
        elif sri >= 50:
            return '+15% stockpile'
        elif sri >= 35:
            return '+10% stockpile'
        else:
            return 'Monitor'

    state_avg['recommendation'] = state_avg['SRI'].apply(get_recommendation)

    return state_avg


def get_commodity_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get commodity-level statistics

    Args:
        df: DataFrame with SRI results

    Returns:
        DataFrame with commodity statistics
    """
    commodity_stats = df.groupby('commodity').agg({
        'SRI': ['mean', 'median', 'min', 'max'],
        'state_name': 'count'
    }).reset_index()

    commodity_stats.columns = ['commodity', 'avg_sri', 'median_sri', 'min_sri', 'max_sri', 'state_count']

    commodity_stats = commodity_stats.sort_values('avg_sri', ascending=False)

    return commodity_stats


def generate_market_report(sri_file: str, output_dir: str, year: int, template_path: str = None, viz_dir: str = None) -> Dict:
    """
    Generate comprehensive market summary report

    Args:
        sri_file: Path to SRI results CSV
        output_dir: Directory to save report
        year: Year of the report
        template_path: Path to HTML template (optional)
        viz_dir: Directory containing visualization images (optional)

    Returns:
        dict with report file path and statistics
    """
    logger.info("📄 Generating market summary report...")

    try:
        # Load SRI data
        df = pd.read_csv(sri_file)
        logger.info(f"  Loaded {len(df)} SRI records")

        # Generate components
        executive_summary = generate_executive_summary(df)
        logger.info("  ✓ Executive summary generated")

        top_risk_states = get_top_risk_states(df, n=15)
        logger.info("  ✓ Top risk states identified")

        commodity_breakdown = get_commodity_breakdown(df)
        logger.info("  ✓ Commodity breakdown calculated")

        # Get critical alerts (SRI >= 75)
        critical_alerts = df[df['SRI'] >= 75].sort_values('SRI', ascending=False)[
            ['state_name', 'commodity', 'SRI', 'recommendation']
        ].head(20)

        # Load and encode visualization images
        visualizations = {}
        if viz_dir and os.path.exists(viz_dir):
            logger.info("  Loading visualizations...")
            viz_files = {
                'sri_distribution': os.path.join(viz_dir, f'sri_distribution_{year}.png'),
                'state_heatmap': os.path.join(viz_dir, f'state_heatmap_{year}.png'),
                'commodity_comparison': os.path.join(viz_dir, f'commodity_comparison_{year}.png'),
                'risk_component_breakdown': os.path.join(viz_dir, f'risk_component_breakdown_{year}.png'),
                'top_states': os.path.join(viz_dir, f'top_states_{year}.png')
            }

            for viz_name, viz_path in viz_files.items():
                if os.path.exists(viz_path):
                    visualizations[viz_name] = encode_image_to_base64(viz_path)
                    logger.info(f"    ✓ Loaded {viz_name}")
                else:
                    logger.warning(f"    ⚠️ Visualization not found: {viz_path}")
                    visualizations[viz_name] = ""

        # Prepare report data
        report_data = {
            'year': year,
            'generated_date': datetime.now().strftime('%B %d, %Y'),
            'executive_summary': executive_summary,
            'top_risk_states': top_risk_states.to_dict('records'),
            'commodity_breakdown': commodity_breakdown.to_dict('records'),
            'critical_alerts': critical_alerts.to_dict('records'),
            'total_records': len(df),
            'visualizations': visualizations
        }

        # Generate HTML report
        if template_path and os.path.exists(template_path):
            with open(template_path, 'r') as f:
                template = Template(f.read())
            html_content = template.render(**report_data)
        else:
            # Use simple built-in template
            html_content = generate_simple_html_report(report_data)

        # Save HTML report
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'market_summary_{year}.html')

        with open(output_file, 'w') as f:
            f.write(html_content)

        logger.info(f"✅ Market report saved to: {output_file}")

        return {
            'success': True,
            'file_path': output_file,
            'stats': {
                'year': year,
                'national_avg_sri': executive_summary['national_avg_sri'],
                'high_risk_states': executive_summary['high_risk_states'],
                'critical_alerts': len(critical_alerts)
            }
        }

    except Exception as e:
        logger.error(f"❌ Error generating market report: {str(e)}")
        return {
            'success': False,
            'file_path': None,
            'error': str(e)
        }


def generate_simple_html_report(data: Dict) -> str:
    """
    Generate professional HTML report with embedded visualizations

    Args:
        data: Report data dictionary

    Returns:
        HTML string
    """
    visualizations = data.get('visualizations', {})

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agricultural Risk Report {data['year']}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; border-bottom: 4px solid #2c5f2d; padding-bottom: 20px; margin-bottom: 30px; }}
            h1 {{ color: #2c5f2d; font-size: 36px; margin: 0; }}
            h2 {{ color: #4a7c59; margin-top: 40px; font-size: 24px; border-left: 5px solid #4a7c59; padding-left: 15px; }}
            .summary {{ background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 30px; border-radius: 10px; margin: 30px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .stat {{ background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
            .stat-value {{ font-size: 42px; font-weight: bold; color: #2c5f2d; margin: 10px 0; }}
            .stat-label {{ font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 1px; }}
            .visualization {{ margin: 30px 0; text-align: center; background: #fafafa; padding: 20px; border-radius: 10px; }}
            .visualization img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
            .visualization h3 {{ color: #4a7c59; margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
            th {{ background: #4a7c59; color: white; padding: 15px; text-align: left; font-weight: 600; }}
            td {{ padding: 12px 15px; border-bottom: 1px solid #e0e0e0; }}
            tr:hover {{ background: #f5f5f5; }}
            tr:last-child td {{ border-bottom: none; }}
            .high-risk {{ color: #d32f2f; font-weight: bold; }}
            .moderate-risk {{ color: #f57c00; font-weight: 600; }}
            .low-risk {{ color: #388e3c; font-weight: 600; }}
            .alert {{ background: #ffebee; border-left: 5px solid #d32f2f; padding: 20px; margin: 20px 0; border-radius: 5px; }}
            .recommendation {{ background: #e3f2fd; border-left: 5px solid #1976d2; padding: 20px; margin: 20px 0; border-radius: 5px; font-size: 16px; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 50px; padding-top: 30px; border-top: 2px solid #e0e0e0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌾 Annual Agricultural Risk Report {data['year']}</h1>
                <p style="color: #666; font-size: 16px; margin: 10px 0 0 0;"><strong>Generated:</strong> {data['generated_date']}</p>
            </div>

            <div class="summary">
                <h2 style="margin-top: 0; border: none; padding: 0;">📊 Executive Summary</h2>
                <div class="stats-grid">
                    <div class="stat">
                        <div class="stat-value">{data['executive_summary']['national_avg_sri']:.1f}</div>
                        <div class="stat-label">National Avg SRI</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{data['executive_summary']['high_risk_states']}</div>
                        <div class="stat-label">High-Risk States</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{data['executive_summary']['overall_risk_level']}</div>
                        <div class="stat-label">Overall Risk Level</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{data['executive_summary']['total_states']}</div>
                        <div class="stat-label">States Analyzed</div>
                    </div>
                </div>
                <div class="recommendation">
                    <strong>📋 Strategic Recommendation:</strong> {data['executive_summary']['recommended_stockpile_change']}
                </div>
            </div>
    """

    # Add SRI Distribution Visualization
    if visualizations.get('sri_distribution'):
        html += f"""
            <div class="visualization">
                <h3>📈 Risk Score Distribution</h3>
                <img src="{visualizations['sri_distribution']}" alt="SRI Distribution">
                <p style="color: #666; margin-top: 10px;">This chart shows how risk scores are distributed across all state-commodity combinations. Lower scores indicate better conditions.</p>
            </div>
        """

    # Add Risk Component Breakdown Visualization
    if visualizations.get('risk_component_breakdown'):
        html += f"""
            <div class="visualization">
                <h3>⚖️ Risk Component Analysis</h3>
                <img src="{visualizations['risk_component_breakdown']}" alt="Risk Components">
                <p style="color: #666; margin-top: 10px;">Breaking down the four key risk factors: Yield Risk (35%), Weather Risk (25%), Drought Risk (25%), and Economic Risk (15%).</p>
            </div>
        """

    # Critical Alerts Section
    html += f"""
            <h2>⚠️ Critical Alerts (SRI ≥ 75)</h2>
    """

    if len(data['critical_alerts']) > 0:
        html += """
            <div class="alert">
                <strong>⚠️ URGENT ATTENTION REQUIRED</strong> - The following state-commodity combinations show critical risk levels requiring immediate action.
            </div>
            <table>
                <tr>
                    <th>State</th>
                    <th>Commodity</th>
                    <th>SRI Score</th>
                    <th>Recommendation</th>
                </tr>
        """
        for alert in data['critical_alerts']:
            html += f"""
                <tr>
                    <td>{alert['state_name']}</td>
                    <td>{alert['commodity']}</td>
                    <td class="high-risk">{alert['SRI']:.1f}</td>
                    <td>{alert['recommendation']}</td>
                </tr>
            """
        html += """
            </table>
        """
    else:
        html += """
            <div style="background: #e8f5e9; padding: 20px; border-radius: 5px; text-align: center;">
                <strong style="color: #388e3c;">✅ No Critical Alerts</strong> - All regions are within acceptable risk thresholds.
            </div>
        """

    # Add Top States Visualization
    if visualizations.get('top_states'):
        html += f"""
            <div class="visualization">
                <h3>🏆 Top 15 High-Risk States</h3>
                <img src="{visualizations['top_states']}" alt="Top Risk States">
                <p style="color: #666; margin-top: 10px;">States ranked by average SRI score. Focus procurement and logistics efforts on these regions.</p>
            </div>
        """

    # Top Risk States Table
    html += """
            <h2>📊 Top Risk States - Detailed Breakdown</h2>
            <table>
                <tr>
                    <th>State</th>
                    <th>Commodities</th>
                    <th>Avg SRI</th>
                    <th>Recommended Action</th>
                </tr>
    """

    for state in data['top_risk_states']:
        risk_class = 'high-risk' if state['SRI'] >= 50 else 'moderate-risk' if state['SRI'] >= 25 else 'low-risk'
        html += f"""
                <tr>
                    <td>{state['state_name']}</td>
                    <td>{state['commodities']}</td>
                    <td class="{risk_class}">{state['SRI']:.1f}</td>
                    <td>{state['recommendation']}</td>
                </tr>
        """

    html += """
            </table>
    """

    # Add Commodity Comparison Visualization
    if visualizations.get('commodity_comparison'):
        html += f"""
            <div class="visualization">
                <h3>🌽 Commodity Risk Comparison</h3>
                <img src="{visualizations['commodity_comparison']}" alt="Commodity Comparison">
                <p style="color: #666; margin-top: 10px;">Box plot comparison showing risk distribution across different crop types. Outliers indicate specific high-risk regions.</p>
            </div>
        """

    # Commodity Breakdown Table
    html += """
            <h2>🌽 Commodity-Level Analysis</h2>
            <table>
                <tr>
                    <th>Commodity</th>
                    <th>Avg SRI</th>
                    <th>Min SRI</th>
                    <th>Max SRI</th>
                    <th>States Covered</th>
                </tr>
    """

    for commodity in data['commodity_breakdown']:
        html += f"""
                <tr>
                    <td><strong>{commodity['commodity']}</strong></td>
                    <td>{commodity['avg_sri']:.1f}</td>
                    <td class="low-risk">{commodity['min_sri']:.1f}</td>
                    <td class="high-risk">{commodity['max_sri']:.1f}</td>
                    <td>{commodity['state_count']}</td>
                </tr>
        """

    html += """
            </table>
    """

    # Add State Heatmap Visualization
    if visualizations.get('state_heatmap'):
        html += f"""
            <div class="visualization">
                <h3>🗺️ Geographic Risk Heatmap</h3>
                <img src="{visualizations['state_heatmap']}" alt="State Heatmap">
                <p style="color: #666; margin-top: 10px;">Detailed heatmap showing risk levels across states and commodities. Red indicates higher risk, green indicates lower risk.</p>
            </div>
        """

    # Footer
    html += f"""
            <div class="footer">
                <p><strong>Agricultural SRI Production System</strong> | {data['year']} Annual Report</p>
                <p>This report analyzed {data['total_records']} state-commodity combinations</p>
                <p>For questions or support, contact: <a href="mailto:api@agcompany.com">api@agcompany.com</a></p>
                <p style="margin-top: 20px; font-size: 10px; color: #ccc;">Generated automatically using data from USDA, NOAA, and Visual Crossing Weather API</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) != 3:
        print("Usage: python market_report_generator.py <sri_file> <output_dir>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    result = generate_market_report(
        sri_file=sys.argv[1],
        output_dir=sys.argv[2],
        year=2024
    )
    print(f"\nReport Generation Result: {result}")
