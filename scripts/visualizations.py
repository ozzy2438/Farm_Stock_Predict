import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
sns.set_palette("husl")

# Load data
df = pd.read_csv("usda_crop_yield_2010_2024.csv")

print("Creating visualizations...")

# Create figure with subplots
fig = plt.figure(figsize=(18, 12))

# 1. Time series - Average yields over time
ax1 = plt.subplot(2, 3, 1)
yearly_avg = df.groupby(['year', 'commodity'])['Value'].mean().reset_index()
for commodity in df['commodity'].unique():
    data = yearly_avg[yearly_avg['commodity'] == commodity]
    ax1.plot(data['year'], data['Value'], marker='o', linewidth=2, label=commodity)
ax1.set_xlabel('Year', fontsize=11)
ax1.set_ylabel('Average Yield (bushels/acre)', fontsize=11)
ax1.set_title('📈 Crop Yields Over Time (2010-2025)', fontsize=13, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. Box plot - Distribution by commodity
ax2 = plt.subplot(2, 3, 2)
df.boxplot(column='Value', by='commodity', ax=ax2)
ax2.set_xlabel('Commodity', fontsize=11)
ax2.set_ylabel('Yield (bushels/acre)', fontsize=11)
ax2.set_title('📊 Yield Distribution by Commodity', fontsize=13, fontweight='bold')
plt.suptitle('')  # Remove default title

# 3. Top 10 states - Corn
ax3 = plt.subplot(2, 3, 3)
top_corn = df[df['commodity'] == 'CORN'].groupby('state_name')['Value'].mean().sort_values(ascending=False).head(10)
top_corn.plot(kind='barh', ax=ax3, color='gold')
ax3.set_xlabel('Average Yield (bushels/acre)', fontsize=11)
ax3.set_ylabel('State', fontsize=11)
ax3.set_title('🌽 Top 10 States - CORN', fontsize=13, fontweight='bold')
ax3.invert_yaxis()

# 4. Top 10 states - Soybeans
ax4 = plt.subplot(2, 3, 4)
top_soy = df[df['commodity'] == 'SOYBEANS'].groupby('state_name')['Value'].mean().sort_values(ascending=False).head(10)
top_soy.plot(kind='barh', ax=ax4, color='green')
ax4.set_xlabel('Average Yield (bushels/acre)', fontsize=11)
ax4.set_ylabel('State', fontsize=11)
ax4.set_title('🌱 Top 10 States - SOYBEANS', fontsize=13, fontweight='bold')
ax4.invert_yaxis()

# 5. Top 10 states - Wheat
ax5 = plt.subplot(2, 3, 5)
top_wheat = df[df['commodity'] == 'WHEAT'].groupby('state_name')['Value'].mean().sort_values(ascending=False).head(10)
top_wheat.plot(kind='barh', ax=ax5, color='wheat')
ax5.set_xlabel('Average Yield (bushels/acre)', fontsize=11)
ax5.set_ylabel('State', fontsize=11)
ax5.set_title('🌾 Top 10 States - WHEAT', fontsize=13, fontweight='bold')
ax5.invert_yaxis()

# 6. Growth comparison (2010 vs 2024)
ax6 = plt.subplot(2, 3, 6)
growth_data = []
for commodity in df['commodity'].unique():
    y2010 = df[(df['year'] == 2010) & (df['commodity'] == commodity)]['Value'].mean()
    y2024 = df[(df['year'] == 2024) & (df['commodity'] == commodity)]['Value'].mean()
    if not np.isnan(y2024) and not np.isnan(y2010):
        growth = ((y2024 - y2010) / y2010) * 100
        growth_data.append({'commodity': commodity, 'growth': growth})

growth_df = pd.DataFrame(growth_data)
bars = ax6.bar(growth_df['commodity'], growth_df['growth'], color=['gold', 'green', 'wheat'])
ax6.set_xlabel('Commodity', fontsize=11)
ax6.set_ylabel('Growth (%)', fontsize=11)
ax6.set_title('📊 Yield Growth (2010 vs 2024)', fontsize=13, fontweight='bold')
ax6.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax6.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax6.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}%',
            ha='center', va='bottom' if height > 0 else 'top', fontsize=10)

plt.tight_layout()
plt.savefig('crop_yield_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: crop_yield_analysis.png")

# Create a second figure - Heatmap of yields by state and year (for Corn only)
fig2, ax = plt.subplots(figsize=(16, 10))

# Pivot data for heatmap (Corn only, top 20 states)
corn_data = df[df['commodity'] == 'CORN']
top_20_states = corn_data.groupby('state_name')['Value'].mean().sort_values(ascending=False).head(20).index
corn_subset = corn_data[corn_data['state_name'].isin(top_20_states)]
heatmap_data = corn_subset.pivot_table(values='Value', index='state_name', columns='year', aggfunc='mean')

sns.heatmap(heatmap_data, annot=False, fmt='.0f', cmap='YlGn', ax=ax, cbar_kws={'label': 'Yield (bushels/acre)'})
ax.set_title('🌽 Corn Yield Heatmap - Top 20 States (2010-2025)', fontsize=14, fontweight='bold', pad=20)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('State', fontsize=12)

plt.tight_layout()
plt.savefig('corn_yield_heatmap.png', dpi=300, bbox_inches='tight')
print("✓ Saved: corn_yield_heatmap.png")

print("\n✓ All visualizations created successfully!")
print("  - crop_yield_analysis.png")
print("  - corn_yield_heatmap.png")
