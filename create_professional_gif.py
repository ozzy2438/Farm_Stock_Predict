"""
Create Professional High-Quality Animated Dashboard GIF
High resolution, slower transitions, with title overlays
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image, ImageDraw, ImageFont
import time
import os

print("🎬 Creating PROFESSIONAL High-Quality Dashboard GIF...")
print("=" * 80)

# Setup Chrome options for high-quality capture
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=2560,1600')  # Much larger resolution
chrome_options.add_argument('--force-device-scale-factor=2')  # Retina quality
chrome_options.add_argument('--hide-scrollbars')

# Dashboard files with better titles
dashboards = [
    ('dashboard_1_trends_annotated.html',
     '📈 RISK TRENDS OVER TIME',
     'Historical patterns with critical event markers (2012 drought, COVID-19, Supply Chain Crisis)'),

    ('dashboard_2_states_annotated.html',
     '🗺️ GEOGRAPHIC RISK ANALYSIS',
     'Top 20 high-risk states - Priority states highlighted with bold borders'),

    ('dashboard_3_commodities_annotated.html',
     '📦 COMMODITY DISTRIBUTION',
     'Risk patterns across CORN, SOYBEANS, WHEAT with statistical overlays'),

    ('dashboard_4_drought_annotated.html',
     '💧 DROUGHT IMPACT CORRELATION',
     'Strong correlation between drought severity and agricultural risk')
]

screenshots = []
base_path = '/Users/osmanorka/Farm_Stock_Predit'

try:
    print("\n🌐 Initializing high-resolution browser...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    for i, (filename, title, description) in enumerate(dashboards, 1):
        file_path = os.path.join(base_path, filename)

        print(f"\n📸 Capturing {i}/{len(dashboards)}: {title}")
        print(f"   {description[:60]}...")

        # Load the HTML file
        driver.get(f'file://{file_path}')

        # Wait longer for Altair/Vega to fully render
        time.sleep(5)

        # Scroll to ensure everything is loaded
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        # Take high-res screenshot
        screenshot_path = os.path.join(base_path, f'temp_screenshot_{i}.png')
        driver.save_screenshot(screenshot_path)

        print(f"   ✓ Captured: {os.path.getsize(screenshot_path) / (1024*1024):.2f} MB")
        screenshots.append((screenshot_path, title, description))

    driver.quit()
    print("\n✅ All high-resolution screenshots captured!")

except Exception as e:
    print(f"\n❌ Error during capture: {e}")
    exit(1)

# Process screenshots and add professional overlays
print("\n🎨 Processing screenshots and adding overlays...")

processed_images = []

for i, (screenshot_path, title, description) in enumerate(screenshots, 1):
    print(f"\n📐 Processing frame {i}/{len(screenshots)}: {title}")

    # Open image
    img = Image.open(screenshot_path)

    # Resize to reasonable size while maintaining quality
    target_width = 1920
    aspect_ratio = img.height / img.width
    target_height = int(target_width * aspect_ratio)
    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Create drawing context
    draw = ImageDraw.Draw(img)

    # Try to load a nice font, fallback to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        desc_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        frame_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        title_font = ImageFont.load_default()
        desc_font = ImageFont.load_default()
        frame_font = ImageFont.load_default()

    # Add semi-transparent header overlay
    header_height = 180
    overlay = Image.new('RGBA', (img.width, header_height), (44, 95, 45, 240))  # Dark green
    img.paste(overlay, (0, 0), overlay)

    # Add title text
    draw.text((30, 30), title, font=title_font, fill=(255, 255, 255))

    # Add description text
    draw.text((30, 100), description, font=desc_font, fill=(200, 255, 200))

    # Add frame counter in bottom right
    frame_text = f"Frame {i} of {len(screenshots)}"
    frame_bbox = draw.textbbox((0, 0), frame_text, font=frame_font)
    frame_width = frame_bbox[2] - frame_bbox[0]

    # Semi-transparent background for frame counter
    counter_bg = Image.new('RGBA', (frame_width + 60, 80), (0, 0, 0, 180))
    img.paste(counter_bg, (img.width - frame_width - 90, img.height - 110), counter_bg)

    draw.text((img.width - frame_width - 60, img.height - 90),
              frame_text, font=frame_font, fill=(255, 255, 255))

    # Add footer with branding
    footer_height = 100
    footer_overlay = Image.new('RGBA', (img.width, footer_height), (0, 0, 0, 200))
    img.paste(footer_overlay, (0, img.height - footer_height), footer_overlay)

    footer_text = "🌾 Agricultural Risk Dashboard | Interactive Analytics Platform"
    draw.text((30, img.height - 70), footer_text, font=desc_font, fill=(124, 179, 66))

    processed_images.append(img)
    print(f"   ✓ Processed: {img.width}x{img.height}px")

# Cleanup temp files
print("\n🧹 Cleaning up temporary files...")
for screenshot_path, _, _ in screenshots:
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)
        print(f"   ✓ Removed: {os.path.basename(screenshot_path)}")

# Create high-quality GIF
print("\n🎞️ Creating high-quality animated GIF...")

# Add first frame at the end for smooth loop
processed_images.append(processed_images[0])

gif_path = '/Users/osmanorka/Farm_Stock_Predit/agricultural_dashboard_animated.gif'

# Save with better settings
processed_images[0].save(
    gif_path,
    save_all=True,
    append_images=processed_images[1:],
    duration=4000,  # 4 seconds per frame (slower for readability)
    loop=0,
    optimize=True,
    quality=95
)

file_size = os.path.getsize(gif_path) / (1024 * 1024)

print("\n" + "=" * 80)
print("✅ PROFESSIONAL GIF CREATED SUCCESSFULLY!")
print("=" * 80)
print(f"\n📍 Location: {gif_path}")
print(f"📊 Frames: {len(screenshots)}")
print(f"⏱️  Duration: {len(screenshots) * 4} seconds total")
print(f"🎬 Frame Duration: 4 seconds each")
print(f"📐 Resolution: {processed_images[0].width}x{processed_images[0].height}px")
print(f"💾 File Size: {file_size:.2f} MB")
print(f"✨ Quality: High (optimized)")

print("\n🎯 Improvements Made:")
print("  ✓ Higher resolution (1920px width)")
print("  ✓ Slower transitions (4s per frame)")
print("  ✓ Professional title overlays")
print("  ✓ Frame counter for navigation")
print("  ✓ Descriptive text on each frame")
print("  ✓ Branded header and footer")
print("  ✓ Semi-transparent overlays")
print("  ✓ Better color contrast")

print("\n📂 Dashboard Files:")
for filename, title, _ in dashboards:
    print(f"  • {filename} - {title}")

print("\n💡 Next Steps:")
print("  1. View the GIF: open agricultural_dashboard_animated.gif")
print("  2. If satisfied, commit and push to GitHub")
print("  3. The GIF will display on README.md")

print("\n✨ Done!")
