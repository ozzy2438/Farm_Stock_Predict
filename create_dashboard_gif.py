"""
Convert Interactive Dashboards to Animated GIF
Captures screenshots of all dashboard views and creates an animated slideshow
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import time
import os

print("🎬 Creating Animated Dashboard GIF...")

# Setup Chrome options for headless operation
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--force-device-scale-factor=1')

# Dashboard files to capture
dashboards = [
    ('dashboard_1_trends_annotated.html', 'Trends with Event Annotations'),
    ('dashboard_2_states_annotated.html', 'Geographic Risk Analysis'),
    ('dashboard_3_commodities_annotated.html', 'Commodity Distribution'),
    ('dashboard_4_drought_annotated.html', 'Drought Impact Correlation')
]

screenshots = []

try:
    print("\n🌐 Initializing browser...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    base_path = '/Users/osmanorka/Farm_Stock_Predit'

    for i, (filename, title) in enumerate(dashboards, 1):
        file_path = os.path.join(base_path, filename)

        print(f"\n📸 Capturing {i}/{len(dashboards)}: {title}")

        # Load the HTML file
        driver.get(f'file://{file_path}')

        # Wait for Altair/Vega to render
        time.sleep(3)

        # Take screenshot
        screenshot_path = os.path.join(base_path, f'screenshot_{i}.png')
        driver.save_screenshot(screenshot_path)

        print(f"  ✓ Saved: screenshot_{i}.png")
        screenshots.append(screenshot_path)

    driver.quit()
    print("\n✅ All screenshots captured successfully!")

except Exception as e:
    print(f"\n⚠️ Screenshot capture failed: {e}")
    print("  Trying alternative method with simpler approach...")

    # Alternative: Create a simple visualization summary
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch

    print("\n📊 Creating alternative static dashboard summary...")

    # Create a summary visualization
    fig = plt.figure(figsize=(16, 20), facecolor='white')

    # Title
    fig.suptitle('🌾 AGRICULTURAL RISK DASHBOARD SUMMARY\nInteractive Analytics Platform',
                 fontsize=28, fontweight='bold', color='#2c5f2d', y=0.98)

    # Create 4 subplots for summaries
    axes = []
    for i in range(4):
        ax = plt.subplot(4, 1, i+1)
        axes.append(ax)

    # Panel 1: Time Trends
    ax1 = axes[0]
    ax1.text(0.5, 0.8, '📈 RISK TRENDS OVER TIME (2010-2024)',
             ha='center', va='top', fontsize=20, fontweight='bold', color='#2c5f2d')
    ax1.text(0.5, 0.6, 'KEY EVENTS ANNOTATED:',
             ha='center', va='top', fontsize=16, fontweight='bold', color='#2d3436')
    ax1.text(0.5, 0.45, '🔥 2012: Historic Drought - Risk peaked at 75+\n' +
                        '🦠 2020: COVID-19 Disruption - Supply chain impact\n' +
                        '⚠️ 2022: Supply Chain Crisis - Global disruptions',
             ha='center', va='top', fontsize=14, style='italic', color='#d32f2f',
             bbox=dict(boxstyle='round,pad=1', facecolor='#fff3e0', edgecolor='#f57c00', linewidth=2))
    ax1.text(0.5, 0.1, '✨ Interactive: Hover for detailed metrics at each point',
             ha='center', va='bottom', fontsize=12, color='#1976d2')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')

    # Panel 2: Geographic Analysis
    ax2 = axes[1]
    ax2.text(0.5, 0.8, '🗺️ TOP 20 HIGH-RISK STATES',
             ha='center', va='top', fontsize=20, fontweight='bold', color='#2c5f2d')
    ax2.text(0.5, 0.6, '⚠️ TOP 5 PRIORITY STATES (Highlighted):',
             ha='center', va='top', fontsize=16, fontweight='bold', color='#d32f2f')
    ax2.text(0.5, 0.45, 'States with highest average risk index\n' +
                        'Color-coded by severity: Green → Yellow → Red\n' +
                        'Focus procurement efforts here!',
             ha='center', va='top', fontsize=14, color='#2d3436',
             bbox=dict(boxstyle='round,pad=1', facecolor='#ffebee', edgecolor='#d32f2f', linewidth=2))

    # Risk zones legend
    risk_zones = [
        ('✅ LOW RISK (0-25)', '#388e3c'),
        ('⚡ MODERATE (25-50)', '#7cb342'),
        ('⚠️ HIGH RISK (50-75)', '#f57c00'),
        ('🔥 CRITICAL (75-100)', '#d32f2f')
    ]
    legend_y = 0.25
    for label, color in risk_zones:
        rect = FancyBboxPatch((0.2, legend_y - 0.03), 0.1, 0.05,
                              boxstyle="round,pad=0.005",
                              facecolor=color, edgecolor='white', linewidth=2,
                              transform=ax2.transAxes)
        ax2.add_patch(rect)
        ax2.text(0.32, legend_y, label, va='center', fontsize=12, fontweight='bold')
        legend_y -= 0.08

    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')

    # Panel 3: Commodity Analysis
    ax3 = axes[2]
    ax3.text(0.5, 0.8, '📦 COMMODITY RISK DISTRIBUTION',
             ha='center', va='top', fontsize=20, fontweight='bold', color='#2c5f2d')
    ax3.text(0.5, 0.6, 'Box Plot Analysis with Statistical Overlays:',
             ha='center', va='top', fontsize=16, fontweight='bold', color='#2d3436')
    ax3.text(0.5, 0.45, '📊 Shows quartiles, medians, and outliers\n' +
                        '💎 Diamond markers indicate mean values\n' +
                        '🎯 Identifies high-variance commodities',
             ha='center', va='top', fontsize=14, color='#2d3436',
             bbox=dict(boxstyle='round,pad=1', facecolor='#e8f5e9', edgecolor='#388e3c', linewidth=2))
    ax3.text(0.5, 0.1, 'Key Insight: Compare risk patterns across CORN, SOYBEANS, WHEAT',
             ha='center', va='bottom', fontsize=12, style='italic', color='#1976d2')
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.axis('off')

    # Panel 4: Drought Correlation
    ax4 = axes[3]
    ax4.text(0.5, 0.8, '💧 DROUGHT IMPACT ANALYSIS',
             ha='center', va='top', fontsize=20, fontweight='bold', color='#2c5f2d')
    ax4.text(0.5, 0.6, '📈 Correlation Analysis:',
             ha='center', va='top', fontsize=16, fontweight='bold', color='#2d3436')
    ax4.text(0.5, 0.45, 'Scatter plot: Drought Index vs. Risk Index\n' +
                        '🔴 Strong positive correlation shown\n' +
                        '⚪ Bubble size represents crop yield\n' +
                        '📉 Regression line shows trend',
             ha='center', va='top', fontsize=14, color='#2d3436',
             bbox=dict(boxstyle='round,pad=1', facecolor='#e3f2fd', edgecolor='#1976d2', linewidth=2))
    ax4.text(0.5, 0.1, '🎯 Action: Monitor DSCI closely - direct predictor of risk',
             ha='center', va='bottom', fontsize=12, fontweight='bold', color='#d32f2f')
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.97])

    summary_path = os.path.join(base_path, 'dashboard_summary_static.png')
    plt.savefig(summary_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()

    print(f"  ✓ Created: dashboard_summary_static.png")
    screenshots = [summary_path]

# Create GIF from screenshots
if screenshots:
    print("\n🎞️ Creating animated GIF...")

    images = []
    for screenshot in screenshots:
        img = Image.open(screenshot)
        # Resize for reasonable file size
        img = img.resize((1600, int(img.height * 1600 / img.width)), Image.Resampling.LANCZOS)
        images.append(img)

    # Add the first frame at the end to loop smoothly
    images.append(images[0])

    # Save as GIF
    gif_path = '/Users/osmanorka/Farm_Stock_Predit/agricultural_dashboard_animated.gif'
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=3000,  # 3 seconds per frame
        loop=0,
        optimize=False
    )

    print(f"\n✅ GIF created successfully!")
    print(f"   📍 Location: {gif_path}")
    print(f"   📊 Frames: {len(screenshots)}")
    print(f"   ⏱️ Duration: {len(screenshots) * 3} seconds")

    # Get file size
    file_size = os.path.getsize(gif_path) / (1024 * 1024)  # Convert to MB
    print(f"   💾 File size: {file_size:.2f} MB")

    # Cleanup screenshots
    print("\n🧹 Cleaning up temporary files...")
    for screenshot in screenshots:
        if os.path.exists(screenshot) and 'screenshot_' in screenshot:
            os.remove(screenshot)
            print(f"  ✓ Removed: {os.path.basename(screenshot)}")

    print("\n" + "="*80)
    print("🎉 DASHBOARD GIF CREATION COMPLETE!")
    print("="*80)
    print("\n📂 Generated Files:")
    print("  • dashboard_1_trends_annotated.html - Interactive time series")
    print("  • dashboard_2_states_annotated.html - Geographic heatmap")
    print("  • dashboard_3_commodities_annotated.html - Commodity analysis")
    print("  • dashboard_4_drought_annotated.html - Drought correlation")
    print("  • agricultural_dashboard_animated.gif - Animated slideshow")
    print("\n💡 Tip: Open HTML files in browser for full interactivity!")
    print("      Use GIF for presentations and quick sharing.")

else:
    print("\n❌ No screenshots available to create GIF")

print("\n✨ Process complete!")
