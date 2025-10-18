"""
Stock Risk Index (SRI) Model for Agricultural Commodities

The SRI is a composite risk score (0-100) that combines:
1. Yield Risk (40%) - Based on historical yield volatility and trends
2. Weather Risk (30%) - Temperature stress and precipitation anomalies
3. Drought Risk (30%) - Drought severity and persistence

Higher SRI = Higher risk of supply disruption
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns

print("="*70)
print("📊 STOCK RISK INDEX (SRI) MODEL")
print("="*70)

# Load merged data
df = pd.read_csv('merged_farm_data.csv')
print(f"\n✓ Loaded data: {len(df):,} records")

# Remove rows with missing values for modeling
df_clean = df.dropna()
print(f"✓ Clean data (no missing values): {len(df_clean):,} records")

# ============================================================================
# COMPONENT 1: YIELD RISK (40%)
# ============================================================================
print("\n1️⃣ CALCULATING YIELD RISK COMPONENT (40% weight)")
print("-" * 70)

# Calculate yield volatility (rolling standard deviation)
df_clean = df_clean.sort_values(['state_name', 'commodity', 'year'])
df_clean['yield_volatility'] = df_clean.groupby(['state_name', 'commodity'])['Value'].transform(
    lambda x: x.rolling(window=3, min_periods=1).std()
)

# Yield decline indicator (negative YoY change)
df_clean['yield_decline'] = df_clean['yield_yoy_change'].apply(lambda x: abs(x) if x < 0 else 0)

# Normalize to 0-100 scale
scaler = MinMaxScaler(feature_range=(0, 100))
df_clean['yield_volatility_score'] = scaler.fit_transform(df_clean[['yield_volatility']])
df_clean['yield_decline_score'] = scaler.fit_transform(df_clean[['yield_decline']])

# Combine (equal weight)
df_clean['yield_risk'] = (
    0.5 * df_clean['yield_volatility_score'] +
    0.5 * df_clean['yield_decline_score']
)

print(f"  ✓ Yield volatility calculated (3-year rolling std)")
print(f"  ✓ Yield decline score calculated")
print(f"  ✓ Yield risk component: mean = {df_clean['yield_risk'].mean():.1f}")

# ============================================================================
# COMPONENT 2: WEATHER RISK (30%)
# ============================================================================
print("\n2️⃣ CALCULATING WEATHER RISK COMPONENT (30% weight)")
print("-" * 70)

# Temperature stress (higher = more stress)
df_clean['temp_stress_score'] = scaler.fit_transform(df_clean[['temp_stress']])

# Precipitation anomaly risk (extreme deviations in either direction)
df_clean['precip_risk'] = df_clean['precip_anomaly'].abs()
df_clean['precip_risk_score'] = scaler.fit_transform(df_clean[['precip_risk']])

# Combine (equal weight)
df_clean['weather_risk'] = (
    0.5 * df_clean['temp_stress_score'] +
    0.5 * df_clean['precip_risk_score']
)

print(f"  ✓ Temperature stress score calculated")
print(f"  ✓ Precipitation risk score calculated")
print(f"  ✓ Weather risk component: mean = {df_clean['weather_risk'].mean():.1f}")

# ============================================================================
# COMPONENT 3: DROUGHT RISK (30%)
# ============================================================================
print("\n3️⃣ CALCULATING DROUGHT RISK COMPONENT (30% weight)")
print("-" * 70)

# Already have drought_risk_score (0-100)
# Add drought persistence (number of consecutive years with high drought)
df_clean['drought_high'] = (df_clean['drought_risk_score'] > 50).astype(int)
df_clean['drought_persistence'] = df_clean.groupby(['state_name', 'commodity'])['drought_high'].transform(
    lambda x: x.rolling(window=3, min_periods=1).sum()
)
df_clean['drought_persistence_score'] = (df_clean['drought_persistence'] / 3) * 100

# Combine (70% current, 30% persistence)
df_clean['drought_risk'] = (
    0.7 * df_clean['drought_risk_score'] +
    0.3 * df_clean['drought_persistence_score']
)

print(f"  ✓ Drought severity score calculated")
print(f"  ✓ Drought persistence calculated (3-year window)")
print(f"  ✓ Drought risk component: mean = {df_clean['drought_risk'].mean():.1f}")

# ============================================================================
# FINAL SRI CALCULATION
# ============================================================================
print("\n4️⃣ CALCULATING FINAL STOCK RISK INDEX (SRI)")
print("-" * 70)

# Weighted combination
df_clean['SRI'] = (
    0.40 * df_clean['yield_risk'] +
    0.30 * df_clean['weather_risk'] +
    0.30 * df_clean['drought_risk']
)

# Classify risk levels
def classify_risk(sri):
    if sri < 25:
        return 'Low'
    elif sri < 50:
        return 'Moderate'
    elif sri < 75:
        return 'High'
    else:
        return 'Very High'

df_clean['risk_level'] = df_clean['SRI'].apply(classify_risk)

print(f"  ✓ SRI calculated (weighted combination)")
print(f"  ✓ Overall SRI mean: {df_clean['SRI'].mean():.1f}")
print(f"  ✓ Overall SRI range: {df_clean['SRI'].min():.1f} - {df_clean['SRI'].max():.1f}")

# Save results
output_file = 'sri_results.csv'
df_clean.to_csv(output_file, index=False)
print(f"\n💾 Saved results: {output_file}")

# ============================================================================
# ANALYSIS & SUMMARY
# ============================================================================
print("\n" + "="*70)
print("📈 SRI SUMMARY STATISTICS")
print("="*70)

print("\n🎯 Risk Level Distribution:")
print(df_clean['risk_level'].value_counts().sort_index())

print("\n📊 SRI by Commodity:")
sri_by_commodity = df_clean.groupby('commodity')['SRI'].agg(['mean', 'std', 'min', 'max'])
print(sri_by_commodity.round(2))

print("\n🏆 Top 10 Highest Risk States (2024, CORN):")
high_risk_2024 = df_clean[(df_clean['year'] == 2024) & (df_clean['commodity'] == 'CORN')].nlargest(10, 'SRI')
for i, row in enumerate(high_risk_2024.iterrows(), 1):
    print(f"  {i:2d}. {row[1]['state_name']:20s} SRI: {row[1]['SRI']:5.1f} ({row[1]['risk_level']})")

print("\n🌟 Top 10 Lowest Risk States (2024, CORN):")
low_risk_2024 = df_clean[(df_clean['year'] == 2024) & (df_clean['commodity'] == 'CORN')].nsmallest(10, 'SRI')
for i, row in enumerate(low_risk_2024.iterrows(), 1):
    print(f"  {i:2d}. {row[1]['state_name']:20s} SRI: {row[1]['SRI']:5.1f} ({row[1]['risk_level']})")

print("\n📉 SRI Trend (Last 5 Years):")
recent_years = df_clean[df_clean['year'] >= 2020].groupby(['year', 'commodity'])['SRI'].mean().reset_index()
pivot = recent_years.pivot(index='year', columns='commodity', values='SRI')
print(pivot.round(2))

print("\n" + "="*70)
print("✓ SRI MODEL COMPLETE!")
print("="*70)

# Create visualization
print("\n📊 Creating SRI visualizations...")

fig = plt.figure(figsize=(16, 10))

# 1. SRI distribution
ax1 = plt.subplot(2, 3, 1)
df_clean['SRI'].hist(bins=30, ax=ax1, color='steelblue', edgecolor='black')
ax1.set_xlabel('Stock Risk Index (SRI)', fontsize=11)
ax1.set_ylabel('Frequency', fontsize=11)
ax1.set_title('SRI Distribution', fontsize=13, fontweight='bold')
ax1.axvline(df_clean['SRI'].mean(), color='red', linestyle='--', label='Mean')
ax1.legend()

# 2. SRI by commodity
ax2 = plt.subplot(2, 3, 2)
df_clean.boxplot(column='SRI', by='commodity', ax=ax2)
ax2.set_xlabel('Commodity', fontsize=11)
ax2.set_ylabel('Stock Risk Index', fontsize=11)
ax2.set_title('SRI by Commodity', fontsize=13, fontweight='bold')
plt.suptitle('')

# 3. SRI over time
ax3 = plt.subplot(2, 3, 3)
yearly_sri = df_clean.groupby(['year', 'commodity'])['SRI'].mean().reset_index()
for commodity in df_clean['commodity'].unique():
    data = yearly_sri[yearly_sri['commodity'] == commodity]
    ax3.plot(data['year'], data['SRI'], marker='o', label=commodity, linewidth=2)
ax3.set_xlabel('Year', fontsize=11)
ax3.set_ylabel('Average SRI', fontsize=11)
ax3.set_title('SRI Trend Over Time', fontsize=13, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. Risk components breakdown
ax4 = plt.subplot(2, 3, 4)
components = df_clean[['yield_risk', 'weather_risk', 'drought_risk']].mean()
ax4.bar(components.index, components.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
ax4.set_ylabel('Average Risk Score', fontsize=11)
ax4.set_title('Risk Component Breakdown', fontsize=13, fontweight='bold')
ax4.set_xticklabels(['Yield\nRisk', 'Weather\nRisk', 'Drought\nRisk'])
for i, v in enumerate(components.values):
    ax4.text(i, v + 1, f'{v:.1f}', ha='center', fontweight='bold')

# 5. Risk level distribution
ax5 = plt.subplot(2, 3, 5)
risk_counts = df_clean['risk_level'].value_counts()
colors = {'Low': '#2ECC71', 'Moderate': '#F39C12', 'High': '#E74C3C', 'Very High': '#8E44AD'}
bars = ax5.bar(risk_counts.index, risk_counts.values,
               color=[colors.get(x, 'gray') for x in risk_counts.index])
ax5.set_ylabel('Count', fontsize=11)
ax5.set_title('Risk Level Distribution', fontsize=13, fontweight='bold')
ax5.set_xticklabels(risk_counts.index, rotation=45)
for bar in bars:
    height = bar.get_height()
    ax5.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}', ha='center', va='bottom', fontsize=9)

# 6. Correlation heatmap
ax6 = plt.subplot(2, 3, 6)
corr_features = ['Value', 'SRI', 'yield_risk', 'weather_risk', 'drought_risk',
                 'temp_stress', 'precip_anomaly']
corr_matrix = df_clean[corr_features].corr()
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax6,
            square=True, linewidths=1)
ax6.set_title('Feature Correlation Matrix', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig('sri_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: sri_analysis.png")

print("\n🎉 All done! Check the files:")
print("   - sri_results.csv")
print("   - sri_analysis.png")
