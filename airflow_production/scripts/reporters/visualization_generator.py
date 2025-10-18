"""
Visualization Generator - Production Module

Generates stunning, professional-quality charts and visualizations from SRI results.
Designed for executive presentations and stakeholder reports.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import os
import logging
from typing import Dict
from matplotlib import patheffects

logger = logging.getLogger(__name__)

# Professional Color Palette
COLORS = {
    'primary': '#2c5f2d',      # Dark green
    'secondary': '#4a7c59',    # Medium green
    'accent': '#7cb342',       # Light green
    'critical': '#d32f2f',     # Red
    'warning': '#f57c00',      # Orange
    'caution': '#fbc02d',      # Yellow
    'success': '#388e3c',      # Green
    'info': '#1976d2',         # Blue
    'background': '#f8f9fa',   # Light gray
    'text': '#2d3436',         # Dark gray
}

# Gradient color maps
GRADIENT_RISK = ['#388e3c', '#7cb342', '#fbc02d', '#f57c00', '#d32f2f']  # Green to Red
GRADIENT_BLUE = ['#e3f2fd', '#90caf9', '#42a5f5', '#1e88e5', '#1565c0']  # Light to Dark Blue

# Set professional visualization style
sns.set_style("white")
plt.rcParams['figure.figsize'] = (14, 9)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 18
plt.rcParams['figure.titleweight'] = 'bold'


def generate_sri_distribution_chart(df: pd.DataFrame, output_path: str, year: int):
    """
    Generate stunning SRI distribution chart with professional styling

    Args:
        df: DataFrame with SRI results
        output_path: Path to save chart
        year: Year of data
    """
    fig, ax = plt.subplots(figsize=(14, 8), facecolor='white')

    # Create histogram with gradient colors
    n, bins, patches = ax.hist(df['SRI'], bins=25, edgecolor='white', linewidth=1.5, alpha=0.9)

    # Color bars by risk level (gradient from green to red)
    for i, patch in enumerate(patches):
        bin_center = (bins[i] + bins[i+1]) / 2
        if bin_center < 25:
            patch.set_facecolor(COLORS['success'])
        elif bin_center < 50:
            patch.set_facecolor(COLORS['caution'])
        elif bin_center < 75:
            patch.set_facecolor(COLORS['warning'])
        else:
            patch.set_facecolor(COLORS['critical'])

    # Add mean and median lines with professional styling
    mean_val = df['SRI'].mean()
    median_val = df['SRI'].median()

    mean_line = ax.axvline(mean_val, color=COLORS['critical'], linestyle='--', linewidth=3,
                           label=f'Mean: {mean_val:.1f}', alpha=0.8)
    median_line = ax.axvline(median_val, color=COLORS['info'], linestyle='--', linewidth=3,
                             label=f'Median: {median_val:.1f}', alpha=0.8)

    # Add risk zone shading
    ax.axvspan(0, 25, alpha=0.1, color=COLORS['success'], label='Low Risk Zone')
    ax.axvspan(25, 50, alpha=0.1, color=COLORS['caution'], label='Moderate Risk Zone')
    ax.axvspan(50, 75, alpha=0.1, color=COLORS['warning'], label='High Risk Zone')
    ax.axvspan(75, 100, alpha=0.1, color=COLORS['critical'], label='Critical Zone')

    # Styling
    ax.set_xlabel('Stock Risk Index (SRI)', fontsize=14, fontweight='bold', color=COLORS['text'])
    ax.set_ylabel('Number of State-Commodity Combinations', fontsize=14, fontweight='bold', color=COLORS['text'])
    ax.set_title(f'Agricultural Risk Distribution Analysis - {year}',
                 fontsize=18, fontweight='bold', color=COLORS['primary'], pad=20)

    # Add subtitle
    subtitle = f'Analysis of {len(df)} state-commodity combinations | Lower scores indicate better conditions'
    ax.text(0.5, 1.02, subtitle, transform=ax.transAxes,
            fontsize=11, ha='center', style='italic', color=COLORS['text'], alpha=0.7)

    # Legend with professional styling
    ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True,
              framealpha=0.95, fontsize=11)

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)

    # Clean spines
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color(COLORS['text'])
        ax.spines[spine].set_linewidth(1.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()

    logger.info(f"  ✓ SRI distribution chart saved")


def generate_state_heatmap(df: pd.DataFrame, output_path: str, year: int):
    """
    Generate stunning state × commodity risk heatmap

    Args:
        df: DataFrame with SRI results
        output_path: Path to save chart
        year: Year of data
    """
    # Pivot data for heatmap
    heatmap_data = df.pivot_table(
        values='SRI',
        index='state_name',
        columns='commodity',
        aggfunc='mean'
    )

    # Sort by average SRI
    heatmap_data['avg'] = heatmap_data.mean(axis=1)
    heatmap_data = heatmap_data.sort_values('avg', ascending=False).drop('avg', axis=1)

    # Take top 30 states for readability
    heatmap_data = heatmap_data.head(30)

    fig, ax = plt.subplots(figsize=(12, 16), facecolor='white')

    # Create custom colormap (green to red)
    from matplotlib.colors import LinearSegmentedColormap
    colors_list = ['#388e3c', '#7cb342', '#fbc02d', '#f57c00', '#d32f2f']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('risk', colors_list, N=n_bins)

    # Create heatmap with professional styling
    sns.heatmap(
        heatmap_data,
        cmap=cmap,
        annot=True,
        fmt='.1f',
        linewidths=2,
        linecolor='white',
        cbar_kws={
            'label': 'Stock Risk Index (SRI)',
            'shrink': 0.8,
            'aspect': 30,
            'pad': 0.02
        },
        vmin=0,
        vmax=100,
        annot_kws={'size': 9, 'weight': 'bold'},
        ax=ax
    )

    # Styling
    ax.set_title(f'Geographic Risk Heatmap - Top 30 States by Average SRI ({year})',
                 fontsize=18, fontweight='bold', color=COLORS['primary'], pad=20)

    # Add subtitle
    subtitle = 'Higher values (red) indicate greater supply risk | Lower values (green) indicate stable conditions'
    ax.text(0.5, 1.015, subtitle, transform=ax.transAxes,
            fontsize=11, ha='center', style='italic', color=COLORS['text'], alpha=0.7)

    ax.set_xlabel('Commodity Type', fontsize=14, fontweight='bold', color=COLORS['text'], labelpad=10)
    ax.set_ylabel('State', fontsize=14, fontweight='bold', color=COLORS['text'], labelpad=10)

    # Rotate labels for better readability
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, ha='center', fontsize=11, fontweight='bold')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=10)

    # Colorbar styling
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=10)
    cbar.set_label('Stock Risk Index (SRI)', fontsize=12, fontweight='bold', labelpad=15)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()

    logger.info(f"  ✓ State heatmap saved")


def generate_commodity_comparison(df: pd.DataFrame, output_path: str, year: int):
    """
    Generate stunning commodity comparison visualization

    Args:
        df: DataFrame with SRI results
        output_path: Path to save chart
        year: Year of data
    """
    fig, ax = plt.subplots(figsize=(14, 8), facecolor='white')

    # Create sophisticated violin plot with box plot overlay
    commodities = sorted(df['commodity'].unique())
    palette = [COLORS['accent'], COLORS['secondary'], COLORS['primary']]

    # Violin plot for distribution shape
    parts = ax.violinplot(
        [df[df['commodity'] == c]['SRI'].values for c in commodities],
        positions=range(len(commodities)),
        widths=0.7,
        showmeans=True,
        showmedians=True
    )

    # Color the violins
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(palette[i % len(palette)])
        pc.set_alpha(0.7)
        pc.set_edgecolor('white')
        pc.set_linewidth(2)

    # Style the violin plot elements
    for partname in ('cbars', 'cmins', 'cmaxes', 'cmedians', 'cmeans'):
        if partname in parts:
            vp = parts[partname]
            vp.set_edgecolor(COLORS['text'])
            vp.set_linewidth(2)

    # Overlay box plot for quartiles
    bp = ax.boxplot(
        [df[df['commodity'] == c]['SRI'].values for c in commodities],
        positions=range(len(commodities)),
        widths=0.3,
        patch_artist=True,
        showfliers=True,
        boxprops=dict(facecolor='white', edgecolor=COLORS['text'], linewidth=2, alpha=0.8),
        whiskerprops=dict(color=COLORS['text'], linewidth=1.5),
        capprops=dict(color=COLORS['text'], linewidth=1.5),
        medianprops=dict(color=COLORS['critical'], linewidth=3),
        flierprops=dict(marker='D', markerfacecolor=COLORS['warning'], markersize=6,
                       markeredgecolor=COLORS['text'], markeredgewidth=1)
    )

    # Add mean values as annotations
    for i, commodity in enumerate(commodities):
        mean_val = df[df['commodity'] == commodity]['SRI'].mean()
        count = len(df[df['commodity'] == commodity])

        # Mean annotation
        ax.text(i, mean_val, f'{mean_val:.1f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold',
                color=COLORS['primary'],
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                         edgecolor=palette[i % len(palette)], linewidth=2))

        # Count annotation at bottom
        ax.text(i, -5, f'n={count}',
                ha='center', va='top', fontsize=9, style='italic',
                color=COLORS['text'], alpha=0.7)

    # Risk zone background shading
    ax.axhspan(0, 25, alpha=0.08, color=COLORS['success'], zorder=0)
    ax.axhspan(25, 50, alpha=0.08, color=COLORS['caution'], zorder=0)
    ax.axhspan(50, 75, alpha=0.08, color=COLORS['warning'], zorder=0)
    ax.axhspan(75, 100, alpha=0.08, color=COLORS['critical'], zorder=0)

    # Styling
    ax.set_xticks(range(len(commodities)))
    ax.set_xticklabels(commodities, fontsize=13, fontweight='bold')
    ax.set_xlabel('Commodity Type', fontsize=14, fontweight='bold', color=COLORS['text'], labelpad=15)
    ax.set_ylabel('Stock Risk Index (SRI)', fontsize=14, fontweight='bold', color=COLORS['text'])
    ax.set_title(f'Commodity Risk Analysis & Distribution - {year}',
                 fontsize=18, fontweight='bold', color=COLORS['primary'], pad=20)

    # Add subtitle
    subtitle = 'Violin plot shows distribution shape | Box plot shows quartiles | Diamond markers indicate outliers'
    ax.text(0.5, 1.02, subtitle, transform=ax.transAxes,
            fontsize=11, ha='center', style='italic', color=COLORS['text'], alpha=0.7)

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='y')
    ax.set_axisbelow(True)

    # Set y-axis limits with padding
    ax.set_ylim(-8, 105)

    # Clean spines
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color(COLORS['text'])
        ax.spines[spine].set_linewidth(1.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()

    logger.info(f"  ✓ Commodity comparison chart saved")


def generate_risk_component_breakdown(df: pd.DataFrame, output_path: str, year: int):
    """
    Generate stunning risk component breakdown chart

    Args:
        df: DataFrame with SRI results
        output_path: Path to save chart
        year: Year of data
    """
    # Check if component columns exist
    components = ['yield_risk', 'weather_risk', 'drought_risk', 'economic_risk']
    available_components = [col for col in components if col in df.columns]

    if len(available_components) < 4:
        logger.warning("  ⚠️ Not all risk components available, skipping breakdown chart")
        return

    # Calculate component statistics
    component_data = {
        'Yield\nRisk': {
            'avg': df['yield_risk'].mean(),
            'weight': 35,
            'color': COLORS['critical']
        },
        'Weather\nRisk': {
            'avg': df['weather_risk'].mean(),
            'weight': 25,
            'color': COLORS['warning']
        },
        'Drought\nRisk': {
            'avg': df['drought_risk'].mean(),
            'weight': 25,
            'color': COLORS['caution']
        },
        'Economic\nRisk': {
            'avg': df['economic_risk'].mean(),
            'weight': 15,
            'color': COLORS['info']
        }
    }

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), facecolor='white')

    # LEFT CHART: Average Risk Scores
    components_list = list(component_data.keys())
    avgs = [component_data[c]['avg'] for c in components_list]
    colors = [component_data[c]['color'] for c in components_list]

    bars = ax1.bar(range(len(components_list)), avgs, color=colors,
                   edgecolor='white', linewidth=3, alpha=0.85, width=0.7)

    # Add gradient effect to bars
    for bar, color in zip(bars, colors):
        bar.set_zorder(3)

    # Add value labels on bars
    for i, (component, value) in enumerate(zip(components_list, avgs)):
        ax1.text(i, value + 3, f'{value:.1f}',
                ha='center', va='bottom', fontsize=14, fontweight='bold',
                color=COLORS['text'],
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                         edgecolor=colors[i], linewidth=2.5))

        # Add weight percentage at bottom
        weight = component_data[component]['weight']
        ax1.text(i, -7, f'{weight}%\nWeight',
                ha='center', va='top', fontsize=10, fontweight='bold',
                color=colors[i], alpha=0.8)

    # Styling for left chart
    ax1.set_ylabel('Average Risk Score (0-100)', fontsize=13, fontweight='bold', color=COLORS['text'])
    ax1.set_title('Risk Component Analysis', fontsize=16, fontweight='bold',
                  color=COLORS['primary'], pad=15)
    ax1.set_xticks(range(len(components_list)))
    ax1.set_xticklabels(components_list, fontsize=12, fontweight='bold')
    ax1.set_ylim(-10, 110)
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='y', zorder=0)
    ax1.set_axisbelow(True)

    # Risk zone shading
    ax1.axhspan(0, 25, alpha=0.08, color=COLORS['success'], zorder=1)
    ax1.axhspan(25, 50, alpha=0.08, color=COLORS['caution'], zorder=1)
    ax1.axhspan(50, 75, alpha=0.08, color=COLORS['warning'], zorder=1)
    ax1.axhspan(75, 100, alpha=0.08, color=COLORS['critical'], zorder=1)

    # Clean spines
    for spine in ['top', 'right']:
        ax1.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax1.spines[spine].set_color(COLORS['text'])
        ax1.spines[spine].set_linewidth(1.5)

    # RIGHT CHART: Contribution to Total SRI (Weighted)
    weighted_contributions = [component_data[c]['avg'] * component_data[c]['weight'] / 100
                              for c in components_list]

    # Create donut chart
    wedges, texts, autotexts = ax2.pie(
        weighted_contributions,
        labels=[c.replace('\n', ' ') for c in components_list],
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.85,
        explode=[0.05] * len(components_list),
        textprops={'fontsize': 11, 'fontweight': 'bold', 'color': COLORS['text']},
        wedgeprops={'edgecolor': 'white', 'linewidth': 3, 'alpha': 0.85}
    )

    # Style percentage text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(13)
        autotext.set_fontweight('bold')

    # Draw circle in center to create donut effect
    centre_circle = plt.Circle((0, 0), 0.65, fc='white', linewidth=2, edgecolor=COLORS['text'])
    ax2.add_artist(centre_circle)

    # Add center text
    ax2.text(0, 0, f'Total SRI\n{df["SRI"].mean():.1f}',
             ha='center', va='center', fontsize=18, fontweight='bold',
             color=COLORS['primary'])

    ax2.set_title('Weighted Contribution to SRI', fontsize=16, fontweight='bold',
                  color=COLORS['primary'], pad=15)

    # Overall title
    fig.suptitle(f'Risk Component Breakdown & Contribution Analysis - {year}',
                 fontsize=20, fontweight='bold', color=COLORS['primary'], y=0.98)

    # Add subtitle
    subtitle = 'Left: Raw component scores | Right: Weighted contribution to final SRI score'
    fig.text(0.5, 0.92, subtitle, ha='center', fontsize=12, style='italic',
             color=COLORS['text'], alpha=0.7)

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()

    logger.info(f"  ✓ Risk component breakdown chart saved")


def generate_top_states_chart(df: pd.DataFrame, output_path: str, year: int):
    """
    Generate stunning top 15 high-risk states visualization

    Args:
        df: DataFrame with SRI results
        output_path: Path to save chart
        year: Year of data
    """
    # Get average SRI by state with additional info
    state_stats = df.groupby('state_name').agg({
        'SRI': 'mean',
        'commodity': lambda x: ', '.join(sorted(set(x)))
    }).sort_values('SRI', ascending=False).head(15)

    state_stats = state_stats.reset_index()

    fig, ax = plt.subplots(figsize=(14, 10), facecolor='white')

    # Reverse order for bottom-to-top display
    state_stats = state_stats.iloc[::-1]

    # Color bars by risk level
    colors = []
    for sri in state_stats['SRI']:
        if sri >= 75:
            colors.append(COLORS['critical'])
        elif sri >= 50:
            colors.append(COLORS['warning'])
        elif sri >= 25:
            colors.append(COLORS['caution'])
        else:
            colors.append(COLORS['success'])

    # Create horizontal bars
    bars = ax.barh(range(len(state_stats)), state_stats['SRI'],
                   color=colors, edgecolor='white', linewidth=2.5,
                   alpha=0.85, height=0.7)

    # Add gradient/shadow effect
    for i, bar in enumerate(bars):
        bar.set_zorder(3)

    # Risk zone background
    ax.axvspan(0, 25, alpha=0.08, color=COLORS['success'], zorder=0)
    ax.axvspan(25, 50, alpha=0.08, color=COLORS['caution'], zorder=0)
    ax.axvspan(50, 75, alpha=0.08, color=COLORS['warning'], zorder=0)
    ax.axvspan(75, 100, alpha=0.08, color=COLORS['critical'], zorder=0)

    # Add value labels on bars
    for i, (idx, row) in enumerate(state_stats.iterrows()):
        sri_value = row['SRI']
        state_name = row['state_name']
        commodities = row['commodity']

        # SRI value label
        ax.text(sri_value + 2, i, f'{sri_value:.1f}',
                va='center', ha='left', fontsize=12, fontweight='bold',
                color=COLORS['text'],
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                         edgecolor=colors[i], linewidth=2))

        # Rank number on the left
        ax.text(-3, i, f'#{len(state_stats)-i}',
                va='center', ha='right', fontsize=11, fontweight='bold',
                color=colors[i], alpha=0.7)

    # Styling
    ax.set_yticks(range(len(state_stats)))
    ax.set_yticklabels(state_stats['state_name'], fontsize=11, fontweight='bold')
    ax.set_xlabel('Average Stock Risk Index (SRI)', fontsize=14, fontweight='bold',
                  color=COLORS['text'], labelpad=10)
    ax.set_title(f'Top 15 High-Risk States for Agricultural Supply - {year}',
                 fontsize=18, fontweight='bold', color=COLORS['primary'], pad=20)

    # Add subtitle
    subtitle = 'States ranked by average SRI score | Focus procurement efforts on top-ranked states'
    ax.text(0.5, 1.02, subtitle, transform=ax.transAxes,
            fontsize=11, ha='center', style='italic', color=COLORS['text'], alpha=0.7)

    # Set x-axis limits
    ax.set_xlim(-5, 110)

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='x', zorder=1)
    ax.set_axisbelow(True)

    # Add risk zone labels at top
    zone_labels = [
        (12.5, 'Low\nRisk', COLORS['success']),
        (37.5, 'Moderate\nRisk', COLORS['caution']),
        (62.5, 'High\nRisk', COLORS['warning']),
        (87.5, 'Critical\nRisk', COLORS['critical'])
    ]

    for x, label, color in zone_labels:
        ax.text(x, len(state_stats) + 0.5, label,
                ha='center', va='bottom', fontsize=9, fontweight='bold',
                color=color, alpha=0.6)

    # Clean spines
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color(COLORS['text'])
        ax.spines[spine].set_linewidth(1.5)

    # Add legend for risk zones
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['success'], edgecolor='white', label='Low Risk (0-25)', alpha=0.85),
        mpatches.Patch(facecolor=COLORS['caution'], edgecolor='white', label='Moderate Risk (25-50)', alpha=0.85),
        mpatches.Patch(facecolor=COLORS['warning'], edgecolor='white', label='High Risk (50-75)', alpha=0.85),
        mpatches.Patch(facecolor=COLORS['critical'], edgecolor='white', label='Critical Risk (75-100)', alpha=0.85)
    ]
    ax.legend(handles=legend_elements, loc='lower right', frameon=True,
              fancybox=True, shadow=True, framealpha=0.95, fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()

    logger.info(f"  ✓ Top states chart saved")


def generate_all_visualizations(sri_file: str, output_dir: str, year: int) -> Dict:
    """
    Generate all visualization charts

    Args:
        sri_file: Path to SRI results CSV
        output_dir: Directory to save visualizations
        year: Year of the report

    Returns:
        dict with file paths and statistics
    """
    logger.info("📊 Generating visualizations...")

    try:
        # Load SRI data
        df = pd.read_csv(sri_file)
        logger.info(f"  Loaded {len(df)} SRI records")

        # Create visualizations directory
        viz_dir = os.path.join(output_dir, 'visualizations')
        os.makedirs(viz_dir, exist_ok=True)

        generated_files = []

        # Generate each chart
        charts = [
            ('sri_distribution', generate_sri_distribution_chart),
            ('state_heatmap', generate_state_heatmap),
            ('commodity_comparison', generate_commodity_comparison),
            ('risk_component_breakdown', generate_risk_component_breakdown),
            ('top_states', generate_top_states_chart)
        ]

        for chart_name, chart_func in charts:
            try:
                output_path = os.path.join(viz_dir, f'{chart_name}_{year}.png')
                chart_func(df, output_path, year)
                generated_files.append(output_path)
            except Exception as e:
                logger.warning(f"  ⚠️ Could not generate {chart_name}: {str(e)}")

        logger.info(f"✅ Generated {len(generated_files)} visualizations")
        logger.info(f"   Saved to: {viz_dir}")

        return {
            'success': True,
            'output_dir': viz_dir,
            'files_generated': len(generated_files),
            'file_paths': generated_files
        }

    except Exception as e:
        logger.error(f"❌ Error generating visualizations: {str(e)}")
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
        print("Usage: python visualization_generator.py <sri_file> <output_dir>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    result = generate_all_visualizations(
        sri_file=sys.argv[1],
        output_dir=sys.argv[2],
        year=2024
    )
    print(f"\nVisualization Result: {result}")
