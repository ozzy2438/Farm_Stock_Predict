"""
Create Altair Dashboard with PyNarrative-style Annotations
Adds arrows and "pay attention" markers to guide audience focus
"""

import pandas as pd
import altair as alt
import numpy as np

print("🎨 Creating Annotated Dashboard with Focus Arrows...")
print("=" * 80)

# Load the data
df = pd.read_csv('/Users/osmanorka/Farm_Stock_Predit/sri_results_2025.csv')

print(f"✓ Loaded {len(df)} records")

# Enable large datasets
alt.data_transformers.disable_max_rows()

# ============================================================================
# CHART 1: Risk Distribution with Attention Arrows
# ============================================================================

print("\n📊 Chart 1: Risk Distribution with annotations...")

# Calculate statistics for annotations
mean_sri = df['SRI'].mean()
median_sri = df['SRI'].median()

# Create histogram data
hist_data = df.copy()

# Add risk category for coloring
hist_data['risk_category'] = pd.cut(
    hist_data['SRI'],
    bins=[0, 25, 50, 75, 100],
    labels=['Low', 'Moderate', 'High', 'Critical']
)

# Base histogram
histogram = alt.Chart(hist_data).mark_bar(opacity=0.8).encode(
    x=alt.X('SRI:Q',
            bin=alt.Bin(maxbins=30),
            title='Stock Risk Index (SRI)',
            axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
    y=alt.Y('count():Q',
            title='Number of State-Commodity Combinations',
            axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
    color=alt.Color('risk_category:N',
                    scale=alt.Scale(
                        domain=['Low', 'Moderate', 'High', 'Critical'],
                        range=['#388e3c', '#fbc02d', '#f57c00', '#d32f2f']
                    ),
                    legend=alt.Legend(title='Risk Level', titleFontSize=14, labelFontSize=12)),
    tooltip=[
        alt.Tooltip('SRI:Q', title='Risk Index', bin=True),
        alt.Tooltip('count():Q', title='Count'),
        alt.Tooltip('risk_category:N', title='Risk Level')
    ]
).properties(
    width=1400,
    height=500,
    title={
        'text': '📊 RISK DISTRIBUTION: Where Should We Focus?',
        'fontSize': 24,
        'fontWeight': 'bold',
        'color': '#2c5f2d'
    }
)

# Mean line
mean_line = alt.Chart(pd.DataFrame({'x': [mean_sri]})).mark_rule(
    strokeWidth=3,
    strokeDash=[8, 4],
    color='#d32f2f'
).encode(
    x='x:Q'
)

# ANNOTATION 1: Arrow pointing to mean with "PAY ATTENTION"
arrow_mean = alt.Chart(pd.DataFrame([{
    'x': mean_sri,
    'y': 45,
    'x2': mean_sri,
    'y2': 35
}])).mark_line(
    strokeWidth=4,
    color='#d32f2f'
).encode(
    x='x:Q',
    y='y:Q',
    x2='x2:Q',
    y2='y2:Q'
)

arrow_head_mean = alt.Chart(pd.DataFrame([{
    'x': mean_sri,
    'y': 35,
    'angle': 270,
    'text': '▼'
}])).mark_text(
    fontSize=30,
    color='#d32f2f',
    fontWeight='bold'
).encode(
    x='x:Q',
    y='y:Q',
    text='text:N'
)

text_mean = alt.Chart(pd.DataFrame([{
    'x': mean_sri + 5,
    'y': 50,
    'text': f'⚠️ AVERAGE RISK: {mean_sri:.1f}\nMost states cluster here'
}])).mark_text(
    fontSize=16,
    fontWeight='bold',
    color='#d32f2f',
    align='left',
    dx=10
).encode(
    x='x:Q',
    y='y:Q',
    text='text:N'
)

# ANNOTATION 2: Arrow pointing to low risk area
low_risk_count = len(df[df['SRI'] < 25])
arrow_low = alt.Chart(pd.DataFrame([{
    'x': 12,
    'y': 40,
    'text': f'✅ LOW RISK ZONE\n{low_risk_count} combinations\n👉 FOCUS HERE for stable supply'
}])).mark_text(
    fontSize=14,
    fontWeight='bold',
    color='#388e3c',
    align='center',
    baseline='bottom'
).encode(
    x='x:Q',
    y='y:Q',
    text='text:N'
)

# ANNOTATION 3: Arrow pointing to critical zone
critical_count = len(df[df['SRI'] > 75])
if critical_count > 0:
    arrow_critical = alt.Chart(pd.DataFrame([{
        'x': 87,
        'y': 15,
        'text': f'🔥 CRITICAL!\n{critical_count} at risk\n⚠️ Immediate action needed'
    }])).mark_text(
        fontSize=14,
        fontWeight='bold',
        color='#d32f2f',
        align='center'
    ).encode(
        x='x:Q',
        y='y:Q',
        text='text:N'
    )
    chart1 = (histogram + mean_line + arrow_mean + arrow_head_mean + text_mean + arrow_low + arrow_critical)
else:
    chart1 = (histogram + mean_line + arrow_mean + arrow_head_mean + text_mean + arrow_low)

chart1 = chart1.configure_view(strokeWidth=0).configure_axis(grid=True, gridOpacity=0.3)

# ============================================================================
# CHART 2: Top States with "Most at Risk" Annotation
# ============================================================================

print("\n🗺️ Chart 2: Top states with focus arrows...")

# Get top 15 states
top_states = df.groupby('state_name').agg({
    'SRI': 'mean'
}).sort_values('SRI', ascending=False).head(15).reset_index()

# Add rank
top_states['rank'] = range(1, len(top_states) + 1)

# Bar chart
bars = alt.Chart(top_states).mark_bar().encode(
    y=alt.Y('state_name:N',
            sort='-x',
            title='State',
            axis=alt.Axis(labelFontSize=13, titleFontSize=16)),
    x=alt.X('SRI:Q',
            title='Average Stock Risk Index',
            scale=alt.Scale(domain=[0, 100]),
            axis=alt.Axis(labelFontSize=13, titleFontSize=16)),
    color=alt.Color('SRI:Q',
                    scale=alt.Scale(
                        domain=[0, 25, 50, 75, 100],
                        range=['#388e3c', '#7cb342', '#fbc02d', '#f57c00', '#d32f2f']
                    ),
                    legend=None),
    tooltip=[
        alt.Tooltip('rank:Q', title='Rank'),
        alt.Tooltip('state_name:N', title='State'),
        alt.Tooltip('SRI:Q', title='Risk Index', format='.1f')
    ]
).properties(
    width=1400,
    height=600,
    title={
        'text': '🗺️ TOP 15 HIGH-RISK STATES: Priority Action Areas',
        'fontSize': 24,
        'fontWeight': 'bold',
        'color': '#2c5f2d'
    }
)

# ANNOTATION: Arrow pointing to #1 state
top_state = top_states.iloc[0]
arrow_top_state = alt.Chart(pd.DataFrame([{
    'x': top_state['SRI'] + 8,
    'y': top_state['state_name'],
    'text': f'👈 MOST AT RISK!\n{top_state["state_name"]}\nSRI: {top_state["SRI"]:.1f}\n⚠️ Priority #1'
}])).mark_text(
    fontSize=16,
    fontWeight='bold',
    color='#d32f2f',
    align='left',
    dx=15
).encode(
    x='x:Q',
    y='y:N',
    text='text:N'
)

# ANNOTATION: Arrow pointing to lowest in top 15
bottom_of_top15 = top_states.iloc[-1]
arrow_bottom = alt.Chart(pd.DataFrame([{
    'x': bottom_of_top15['SRI'] - 5,
    'y': bottom_of_top15['state_name'],
    'text': f'Still at risk →\nbut less urgent'
}])).mark_text(
    fontSize=12,
    fontStyle='italic',
    color='#666',
    align='right',
    dx=-10
).encode(
    x='x:Q',
    y='y:N',
    text='text:N'
)

chart2 = (bars + arrow_top_state + arrow_bottom).configure_view(
    strokeWidth=0
).configure_axis(
    grid=True,
    gridOpacity=0.3
)

# ============================================================================
# CHART 3: Commodity Comparison with Focus Areas
# ============================================================================

print("\n🌾 Chart 3: Commodity comparison with annotations...")

commodity_data = df.copy()

# Box plot
boxplot = alt.Chart(commodity_data).mark_boxplot(
    size=100,
    color='#2c5f2d'
).encode(
    x=alt.X('commodity:N',
            title='Commodity Type',
            axis=alt.Axis(labelFontSize=14, titleFontSize=16, labelAngle=0)),
    y=alt.Y('SRI:Q',
            title='Stock Risk Index',
            scale=alt.Scale(domain=[0, 100]),
            axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
    tooltip=[
        alt.Tooltip('commodity:N', title='Commodity'),
        alt.Tooltip('SRI:Q', title='Risk Index')
    ]
).properties(
    width=1400,
    height=500,
    title={
        'text': '🌾 COMMODITY RISK COMPARISON: Which Crops Need Attention?',
        'fontSize': 24,
        'fontWeight': 'bold',
        'color': '#2c5f2d'
    }
)

# Calculate commodity stats for annotations
commodity_stats = commodity_data.groupby('commodity').agg({
    'SRI': ['mean', 'median', 'max']
}).reset_index()
commodity_stats.columns = ['commodity', 'mean', 'median', 'max']

# Find highest risk commodity
highest_risk_commodity = commodity_stats.loc[commodity_stats['mean'].idxmax()]

# ANNOTATION: Point to highest risk commodity
annotation_highest = alt.Chart(pd.DataFrame([{
    'x': highest_risk_commodity['commodity'],
    'y': 95,
    'text': f'⚠️ HIGHEST AVERAGE RISK\n{highest_risk_commodity["mean"]:.1f}\n👇 Monitor closely'
}])).mark_text(
    fontSize=16,
    fontWeight='bold',
    color='#d32f2f',
    align='center'
).encode(
    x='x:N',
    y='y:Q',
    text='text:N'
)

# Find lowest risk commodity
lowest_risk_commodity = commodity_stats.loc[commodity_stats['mean'].idxmin()]

annotation_lowest = alt.Chart(pd.DataFrame([{
    'x': lowest_risk_commodity['commodity'],
    'y': -5,
    'text': f'✅ Most Stable\nAvg: {lowest_risk_commodity["mean"]:.1f}'
}])).mark_text(
    fontSize=14,
    fontWeight='bold',
    color='#388e3c',
    align='center'
).encode(
    x='x:N',
    y='y:Q',
    text='text:N'
)

chart3 = (boxplot + annotation_highest + annotation_lowest).configure_view(
    strokeWidth=0
).configure_axis(
    grid=True,
    gridOpacity=0.3
)

# ============================================================================
# Save Charts
# ============================================================================

print("\n💾 Saving annotated dashboards...")

chart1.save('/Users/osmanorka/Farm_Stock_Predit/annotated_1_distribution.html')
print("  ✓ Chart 1: Risk Distribution with arrows")

chart2.save('/Users/osmanorka/Farm_Stock_Predit/annotated_2_top_states.html')
print("  ✓ Chart 2: Top States with priority markers")

chart3.save('/Users/osmanorka/Farm_Stock_Predit/annotated_3_commodities.html')
print("  ✓ Chart 3: Commodity comparison with focus areas")

print("\n" + "=" * 80)
print("✅ ANNOTATED DASHBOARDS CREATED!")
print("=" * 80)

print("\n🎯 Features added:")
print("  ✓ Arrows pointing to key areas")
print("  ✓ 'PAY ATTENTION' markers")
print("  ✓ Priority rankings")
print("  ✓ Focus guidance for audience")
print("  ✓ Color-coded urgency levels")
print("  ✓ Statistical callouts")

print("\n📂 Files created:")
print("  • annotated_1_distribution.html - Where to focus on risk zones")
print("  • annotated_2_top_states.html - Priority states with rankings")
print("  • annotated_3_commodities.html - Which crops need attention")

print("\n💡 These use Altair with PyNarrative-style annotations")
print("   to guide audience attention to critical insights!")

print("\n✨ Done!")
