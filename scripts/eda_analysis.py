import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# Load data
df = pd.read_csv("usda_crop_yield_2010_2024.csv")

print("="*70)
print("📊 CROP YIELD DATA - EXPLORATORY ANALYSIS")
print("="*70)

# Basic info
print("\n1️⃣ DATASET OVERVIEW")
print("-" * 70)
print(f"Total records: {len(df):,}")
print(f"Date range: {df['year'].min()} - {df['year'].max()}")
print(f"Commodities: {', '.join(df['commodity'].unique())}")
print(f"States: {df['state_name'].nunique()}")
print(f"\nShape: {df.shape}")

# Check for missing values
print("\n2️⃣ DATA QUALITY")
print("-" * 70)
print("Missing values:")
print(df.isnull().sum())

# Statistics by commodity
print("\n3️⃣ YIELD STATISTICS BY COMMODITY (bushels/acre)")
print("-" * 70)
stats = df.groupby('commodity')['Value'].agg(['count', 'mean', 'std', 'min', 'max'])
print(stats.round(2))

# Top 10 producing states per commodity
print("\n4️⃣ TOP 10 STATES BY AVERAGE YIELD")
print("-" * 70)
for commodity in df['commodity'].unique():
    top_states = df[df['commodity'] == commodity].groupby('state_name')['Value'].mean().sort_values(ascending=False).head(10)
    print(f"\n{commodity}:")
    for i, (state, value) in enumerate(top_states.items(), 1):
        print(f"  {i:2d}. {state:20s} {value:6.1f} bushels/acre")

# Year-over-year trends
print("\n5️⃣ YEAR-OVER-YEAR AVERAGE YIELDS")
print("-" * 70)
yearly_avg = df.groupby(['year', 'commodity'])['Value'].mean().reset_index()
pivot = yearly_avg.pivot(index='year', columns='commodity', values='Value')
print(pivot.round(1))

# Calculate growth rates
print("\n6️⃣ YIELD GROWTH ANALYSIS (2010 vs 2024)")
print("-" * 70)
for commodity in df['commodity'].unique():
    y2010 = df[(df['year'] == 2010) & (df['commodity'] == commodity)]['Value'].mean()
    y2024 = df[(df['year'] == 2024) & (df['commodity'] == commodity)]['Value'].mean()
    if not np.isnan(y2024) and not np.isnan(y2010):
        growth = ((y2024 - y2010) / y2010) * 100
        print(f"{commodity:12s}: {y2010:6.1f} → {y2024:6.1f} bushels/acre ({growth:+.1f}%)")

print("\n" + "="*70)
print("✓ Analysis complete!")
print("="*70)
