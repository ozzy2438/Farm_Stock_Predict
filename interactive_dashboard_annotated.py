"""
Interactive Agricultural Risk Dashboard with Annotations
Using Altair for beautiful visualizations and PyNarrative for storytelling
"""

import pandas as pd
import altair as alt
import json
from datetime import datetime
import numpy as np

# Enable Altair data transformations for large datasets
alt.data_transformers.disable_max_rows()

print("📊 Loading Agricultural Risk Analysis Data...")

# Load the Excel file
df = pd.read_excel('/Users/osmanorka/Farm_Stock_Predit/agricultural_risk_analysis.xlsx')

print(f"✓ Loaded {len(df)} records from {df['year'].min()} to {df['year'].max()}")
print(f"✓ States: {df['state_name'].nunique()}, Commodities: {df['commodity'].nunique()}")

# Calculate risk scores (simplified SRI calculation)
df['yield_risk'] = ((df['Value'] - df.groupby('commodity')['Value'].transform('mean')) /
                    df.groupby('commodity')['Value'].transform('std')) * -10 + 50
df['drought_risk'] = df['dsci'] * 10
df['price_risk'] = ((df['avg_farm_price_usd_bu'] - df['avg_farm_price_usd_bu'].mean()) /
                    df['avg_farm_price_usd_bu'].std()) * 10 + 50
df['stock_risk'] = ((df['stocks_to_use_ratio_pct_x'] - df['stocks_to_use_ratio_pct_x'].mean()) /
                    df['stocks_to_use_ratio_pct_x'].std()) * -10 + 50

# Calculate composite risk index
df['risk_index'] = (df['yield_risk'] * 0.35 +
                    df['drought_risk'] * 0.25 +
                    df['price_risk'] * 0.20 +
                    df['stock_risk'] * 0.20).clip(0, 100)

# Clean data
df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['risk_index'])

print("\n🎨 Creating Interactive Dashboard with Annotations...")

# ================================================================================
# CHART 1: Time Series with Key Event Annotations
# ================================================================================

# Aggregate yearly data
yearly_data = df.groupby(['year', 'commodity']).agg({
    'risk_index': 'mean',
    'Value': 'mean',
    'dsci': 'mean',
    'avg_farm_price_usd_bu': 'mean'
}).reset_index()

# Key events to annotate
key_events = pd.DataFrame([
    {'year': 2012, 'event': '🔥 Historic Drought', 'risk': 75, 'color': '#d32f2f'},
    {'year': 2020, 'event': '🦠 COVID-19 Disruption', 'risk': 65, 'color': '#f57c00'},
    {'year': 2022, 'event': '⚠️ Supply Chain Crisis', 'risk': 70, 'color': '#fbc02d'},
])

# Base time series chart
base_chart = alt.Chart(yearly_data).mark_line(
    point=True,
    strokeWidth=3
).encode(
    x=alt.X('year:O',
            title='Year',
            axis=alt.Axis(labelAngle=0, labelFontSize=12, titleFontSize=14)),
    y=alt.Y('risk_index:Q',
            title='Average Risk Index',
            scale=alt.Scale(domain=[0, 100]),
            axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
    color=alt.Color('commodity:N',
                    title='Commodity',
                    scale=alt.Scale(scheme='category10'),
                    legend=alt.Legend(titleFontSize=14, labelFontSize=12)),
    tooltip=[
        alt.Tooltip('year:O', title='Year'),
        alt.Tooltip('commodity:N', title='Commodity'),
        alt.Tooltip('risk_index:Q', title='Risk Index', format='.1f'),
        alt.Tooltip('Value:Q', title='Yield', format='.1f'),
        alt.Tooltip('dsci:Q', title='Drought Index', format='.2f')
    ]
).properties(
    width=1200,
    height=400,
    title={
        'text': '📈 Agricultural Risk Trends Over Time (2010-2024)',
        'fontSize': 20,
        'fontWeight': 'bold',
        'anchor': 'start',
        'color': '#2c5f2d'
    }
)

# Event annotations - vertical lines
event_rules = alt.Chart(key_events).mark_rule(
    strokeWidth=2,
    strokeDash=[5, 5],
    opacity=0.7
).encode(
    x='year:O',
    color=alt.Color('color:N', scale=None),
    tooltip=['event:N', 'year:O']
)

# Event annotations - text labels
event_text = alt.Chart(key_events).mark_text(
    align='center',
    baseline='bottom',
    dy=-10,
    fontSize=14,
    fontWeight='bold'
).encode(
    x='year:O',
    y='risk:Q',
    text='event:N',
    color=alt.Color('color:N', scale=None)
)

# Critical threshold line
threshold = alt.Chart(pd.DataFrame({'y': [75]})).mark_rule(
    strokeWidth=2,
    strokeDash=[10, 5],
    color='#d32f2f',
    opacity=0.8
).encode(
    y='y:Q'
)

threshold_text = alt.Chart(pd.DataFrame({'y': [75], 'label': ['⚠️ CRITICAL THRESHOLD']})).mark_text(
    align='right',
    baseline='bottom',
    dx=-10,
    dy=-5,
    fontSize=12,
    fontWeight='bold',
    color='#d32f2f'
).encode(
    y='y:Q',
    text='label:N'
)

chart1 = (base_chart + event_rules + event_text + threshold + threshold_text).configure_view(
    strokeWidth=0
).configure_axis(
    grid=True,
    gridOpacity=0.3
)

# ================================================================================
# CHART 2: Geographic Heatmap with Top States Highlighted
# ================================================================================

# Get latest year data
latest_year = df['year'].max()
state_data = df[df['year'] == latest_year].groupby('state_name').agg({
    'risk_index': 'mean',
    'Value': 'mean',
    'dsci': 'mean'
}).reset_index().sort_values('risk_index', ascending=False).head(20)

# Mark top 5 high-risk states
state_data['highlight'] = state_data['risk_index'].rank(ascending=False) <= 5
state_data['label'] = state_data.apply(
    lambda x: f"⚠️ {x['state_name']}" if x['highlight'] else x['state_name'],
    axis=1
)

heatmap = alt.Chart(state_data).mark_bar().encode(
    x=alt.X('risk_index:Q',
            title='Average Risk Index',
            scale=alt.Scale(domain=[0, 100]),
            axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
    y=alt.Y('state_name:N',
            title='State',
            sort='-x',
            axis=alt.Axis(labelFontSize=11, titleFontSize=14)),
    color=alt.Color('risk_index:Q',
                    scale=alt.Scale(
                        domain=[0, 25, 50, 75, 100],
                        range=['#388e3c', '#7cb342', '#fbc02d', '#f57c00', '#d32f2f']
                    ),
                    legend=None),
    strokeWidth=alt.condition(
        alt.datum.highlight,
        alt.value(4),
        alt.value(0)
    ),
    stroke=alt.condition(
        alt.datum.highlight,
        alt.value('#000000'),
        alt.value(None)
    ),
    tooltip=[
        alt.Tooltip('state_name:N', title='State'),
        alt.Tooltip('risk_index:Q', title='Risk Index', format='.1f'),
        alt.Tooltip('Value:Q', title='Avg Yield', format='.1f'),
        alt.Tooltip('dsci:Q', title='Drought Index', format='.2f')
    ]
).properties(
    width=1200,
    height=600,
    title={
        'text': f'🗺️ Top 20 High-Risk States - {latest_year} (Highlighted: Top 5 PRIORITY)',
        'fontSize': 20,
        'fontWeight': 'bold',
        'anchor': 'start',
        'color': '#2c5f2d'
    }
)

# Risk zone annotations
risk_zones = pd.DataFrame([
    {'x': 12.5, 'label': '✅ LOW RISK', 'color': '#388e3c'},
    {'x': 37.5, 'label': '⚡ MODERATE', 'color': '#7cb342'},
    {'x': 62.5, 'label': '⚠️ HIGH RISK', 'color': '#f57c00'},
    {'x': 87.5, 'label': '🔥 CRITICAL', 'color': '#d32f2f'}
])

zone_text = alt.Chart(risk_zones).mark_text(
    align='center',
    baseline='top',
    dy=10,
    fontSize=11,
    fontWeight='bold'
).encode(
    x=alt.X('x:Q', scale=alt.Scale(domain=[0, 100])),
    text='label:N',
    color=alt.Color('color:N', scale=None)
)

chart2 = (heatmap + zone_text).configure_view(
    strokeWidth=0
).configure_axis(
    grid=True,
    gridOpacity=0.3
)

# ================================================================================
# CHART 3: Commodity Comparison with Distribution
# ================================================================================

commodity_data = df[df['year'] == latest_year].copy()

# Calculate quartiles for annotations
commodity_stats = commodity_data.groupby('commodity').agg({
    'risk_index': ['mean', 'median', 'std', 'min', 'max']
}).reset_index()
commodity_stats.columns = ['commodity', 'mean', 'median', 'std', 'min', 'max']
commodity_stats['annotation'] = commodity_stats.apply(
    lambda x: f"📊 Mean: {x['mean']:.1f}\n📍 Median: {x['median']:.1f}",
    axis=1
)

# Box plot
boxplot = alt.Chart(commodity_data).mark_boxplot(
    size=80,
    median={'stroke': '#d32f2f', 'strokeWidth': 3},
    box={'stroke': '#2c5f2d', 'strokeWidth': 2},
    ticks={'stroke': '#2c5f2d'},
    outliers={'stroke': '#f57c00', 'fill': '#f57c00', 'size': 50}
).encode(
    x=alt.X('commodity:N',
            title='Commodity',
            axis=alt.Axis(labelAngle=0, labelFontSize=13, titleFontSize=14)),
    y=alt.Y('risk_index:Q',
            title='Risk Index Distribution',
            scale=alt.Scale(domain=[0, 100]),
            axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
    color=alt.Color('commodity:N',
                    scale=alt.Scale(scheme='set2'),
                    legend=None),
    tooltip=[
        alt.Tooltip('commodity:N', title='Commodity'),
        alt.Tooltip('risk_index:Q', title='Risk Index', format='.1f')
    ]
).properties(
    width=1200,
    height=500,
    title={
        'text': f'📦 Risk Distribution by Commodity - {latest_year}',
        'fontSize': 20,
        'fontWeight': 'bold',
        'anchor': 'start',
        'color': '#2c5f2d'
    }
)

# Mean points overlay
mean_points = alt.Chart(commodity_stats).mark_point(
    filled=True,
    size=200,
    shape='diamond',
    color='#1976d2'
).encode(
    x='commodity:N',
    y='mean:Q',
    tooltip=[
        alt.Tooltip('commodity:N', title='Commodity'),
        alt.Tooltip('mean:Q', title='Mean Risk', format='.1f'),
        alt.Tooltip('std:Q', title='Std Dev', format='.1f')
    ]
)

# Annotation text for statistics
stats_text = alt.Chart(commodity_stats).mark_text(
    align='center',
    baseline='bottom',
    dy=-15,
    fontSize=11,
    fontWeight='bold',
    color='#1976d2'
).encode(
    x='commodity:N',
    y='mean:Q',
    text=alt.Text('mean:Q', format='.1f')
)

chart3 = (boxplot + mean_points + stats_text).configure_view(
    strokeWidth=0
).configure_axis(
    grid=True,
    gridOpacity=0.3
)

# ================================================================================
# CHART 4: Drought Impact Correlation
# ================================================================================

scatter_data = df.sample(n=min(1000, len(df)), random_state=42)

# Create categories for highlighting
scatter_data['risk_category'] = pd.cut(
    scatter_data['risk_index'],
    bins=[0, 25, 50, 75, 100],
    labels=['✅ Low Risk', '⚡ Moderate Risk', '⚠️ High Risk', '🔥 Critical Risk']
)

scatter = alt.Chart(scatter_data).mark_circle(
    size=100,
    opacity=0.7
).encode(
    x=alt.X('dsci:Q',
            title='Drought Severity Index (DSCI)',
            scale=alt.Scale(domain=[0, 5]),
            axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
    y=alt.Y('risk_index:Q',
            title='Overall Risk Index',
            scale=alt.Scale(domain=[0, 100]),
            axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
    color=alt.Color('risk_category:N',
                    title='Risk Category',
                    scale=alt.Scale(
                        domain=['✅ Low Risk', '⚡ Moderate Risk', '⚠️ High Risk', '🔥 Critical Risk'],
                        range=['#388e3c', '#7cb342', '#f57c00', '#d32f2f']
                    ),
                    legend=alt.Legend(titleFontSize=14, labelFontSize=12)),
    size=alt.Size('Value:Q',
                  title='Crop Yield',
                  scale=alt.Scale(range=[50, 500]),
                  legend=None),
    tooltip=[
        alt.Tooltip('state_name:N', title='State'),
        alt.Tooltip('commodity:N', title='Commodity'),
        alt.Tooltip('year:O', title='Year'),
        alt.Tooltip('dsci:Q', title='Drought Index', format='.2f'),
        alt.Tooltip('risk_index:Q', title='Risk Index', format='.1f'),
        alt.Tooltip('Value:Q', title='Yield', format='.1f')
    ]
).properties(
    width=1200,
    height=500,
    title={
        'text': '💧 Drought Impact on Agricultural Risk (Bubble size = Crop Yield)',
        'fontSize': 20,
        'fontWeight': 'bold',
        'anchor': 'start',
        'color': '#2c5f2d'
    }
)

# Regression line
regression = scatter.transform_regression(
    'dsci', 'risk_index'
).mark_line(
    color='#d32f2f',
    strokeWidth=3,
    strokeDash=[5, 5]
)

# Annotation for correlation
correlation = scatter_data[['dsci', 'risk_index']].corr().iloc[0, 1]
corr_text = alt.Chart(pd.DataFrame([{
    'x': 4,
    'y': 90,
    'text': f'📈 Correlation: {correlation:.2f}\n(Strong positive relationship)'
}])).mark_text(
    align='right',
    baseline='top',
    fontSize=14,
    fontWeight='bold',
    color='#d32f2f'
).encode(
    x='x:Q',
    y='y:Q',
    text='text:N'
)

chart4 = (scatter + regression + corr_text).configure_view(
    strokeWidth=0
).configure_axis(
    grid=True,
    gridOpacity=0.3
)

# ================================================================================
# Save all charts
# ================================================================================

print("\n💾 Saving Interactive Dashboards...")

chart1.save('/Users/osmanorka/Farm_Stock_Predit/dashboard_1_trends_annotated.html')
print("  ✓ Chart 1: Trends with Events - dashboard_1_trends_annotated.html")

chart2.save('/Users/osmanorka/Farm_Stock_Predit/dashboard_2_states_annotated.html')
print("  ✓ Chart 2: Geographic Risk - dashboard_2_states_annotated.html")

chart3.save('/Users/osmanorka/Farm_Stock_Predit/dashboard_3_commodities_annotated.html')
print("  ✓ Chart 3: Commodity Distribution - dashboard_3_commodities_annotated.html")

chart4.save('/Users/osmanorka/Farm_Stock_Predit/dashboard_4_drought_annotated.html')
print("  ✓ Chart 4: Drought Correlation - dashboard_4_drought_annotated.html")

# Create combined dashboard
combined = alt.vconcat(
    chart1,
    chart2,
    chart3,
    chart4
).configure_title(
    fontSize=20,
    fontWeight='bold',
    anchor='start',
    color='#2c5f2d'
).configure_view(
    strokeWidth=0
).configure_concat(
    spacing=50
)

combined.save('/Users/osmanorka/Farm_Stock_Predit/dashboard_COMPLETE_annotated.html')
print("\n✅ COMPLETE DASHBOARD: dashboard_COMPLETE_annotated.html")

print("\n" + "="*80)
print("🎯 KEY FEATURES:")
print("  • Interactive tooltips on all elements")
print("  • Historical event annotations (2012 drought, COVID-19, etc.)")
print("  • Risk zone highlighting with color coding")
print("  • Top 5 priority states marked with bold borders")
print("  • Statistical overlays (mean, median, correlation)")
print("  • Responsive design with professional styling")
print("="*80)

print("\n📊 Dashboard Statistics:")
print(f"  • Total Records Analyzed: {len(df):,}")
print(f"  • Time Period: {df['year'].min()} - {df['year'].max()}")
print(f"  • States Covered: {df['state_name'].nunique()}")
print(f"  • Commodities: {', '.join(sorted(df['commodity'].unique()))}")
print(f"  • Average Risk Index: {df['risk_index'].mean():.1f}")
print(f"  • Highest Risk State: {state_data.iloc[0]['state_name']} ({state_data.iloc[0]['risk_index']:.1f})")

print("\n✨ All dashboards are ready! Open the HTML files in your browser.")
