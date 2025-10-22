"""
Create Final Professional Dashboard GIF
Focus on the visualizations, minimal but clear overlays
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image, ImageDraw, ImageFont
import time
import os

print("🎬 Creating FINAL Professional Dashboard GIF...")
print("=" * 80)

# Setup Chrome for maximum quality
chrome_options = Options()
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=2400,1800')  # Larger viewport
chrome_options.add_argument('--force-device-scale-factor=2')
chrome_options.add_argument('--hide-scrollbars')
chrome_options.add_argument('--disable-gpu')

dashboards = [
    ('dashboard_1_trends_annotated.html',
     '📈 Risk Trends: 2012 Drought, COVID-19, Supply Chain Crisis'),

    ('dashboard_2_states_annotated.html',
     '🗺️ Geographic Risk: Top 20 States (Bold = Priority)'),

    ('dashboard_3_commodities_annotated.html',
     '📦 Commodity Analysis: CORN, SOYBEANS, WHEAT'),

    ('dashboard_4_drought_annotated.html',
     '💧 Drought Correlation: Strong Predictive Relationship')
]

screenshots = []
base_path = '/Users/osmanorka/Farm_Stock_Predit'

try:
    print("\n🌐 Starting browser capture...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    for i, (filename, caption) in enumerate(dashboards, 1):
        file_path = os.path.join(base_path, filename)

        print(f"\n📸 [{i}/{len(dashboards)}] {caption}")

        driver.get(f'file://{file_path}')
        time.sleep(6)  # Wait for full render

        # Ensure we're at top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        screenshot_path = os.path.join(base_path, f'frame_{i}.png')
        driver.save_screenshot(screenshot_path)

        size_mb = os.path.getsize(screenshot_path) / (1024*1024)
        print(f"   ✓ Captured: {size_mb:.2f} MB")
        screenshots.append((screenshot_path, caption))

    driver.quit()
    print("\n✅ Screenshots complete!")

except Exception as e:
    print(f"\n❌ Capture failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Process with minimal, clean overlays
print("\n🎨 Adding professional overlays...")

processed = []

for i, (path, caption) in enumerate(screenshots, 1):
    print(f"\n[{i}/{len(screenshots)}] Processing {caption[:40]}...")

    img = Image.open(path)

    # Resize to final dimensions
    final_width = 1920
    aspect = img.height / img.width
    final_height = int(final_width * aspect)
    img = img.resize((final_width, final_height), Image.Resampling.LANCZOS)

    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        caption_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 44)
        counter_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    except:
        caption_font = ImageFont.load_default()
        counter_font = ImageFont.load_default()

    # MINIMAL TOP BANNER - just caption
    banner_height = 80
    banner = Image.new('RGBA', (img.width, banner_height), (28, 48, 29, 230))
    img.paste(banner, (0, 0), banner)
    draw.text((20, 18), caption, font=caption_font, fill=(255, 255, 255))

    # Frame counter - bottom right, small
    counter_text = f"{i}/{len(screenshots)}"
    counter_bbox = draw.textbbox((0, 0), counter_text, font=counter_font)
    counter_w = counter_bbox[2] - counter_bbox[0]

    counter_bg = Image.new('RGBA', (counter_w + 40, 60), (0, 0, 0, 200))
    img.paste(counter_bg, (img.width - counter_w - 60, img.height - 80), counter_bg)
    draw.text((img.width - counter_w - 40, img.height - 65),
              counter_text, font=counter_font, fill=(200, 255, 200))

    processed.append(img)
    print(f"   ✓ {img.width}x{img.height}px")

    # Cleanup
    os.remove(path)

# Create GIF
print("\n🎞️ Creating animated GIF...")

# Duplicate first frame at end for smooth loop
processed.append(processed[0].copy())

gif_path = os.path.join(base_path, 'agricultural_dashboard_animated.gif')

processed[0].save(
    gif_path,
    save_all=True,
    append_images=processed[1:],
    duration=5000,  # 5 seconds - enough time to read
    loop=0,
    optimize=True,
    quality=90
)

size_mb = os.path.getsize(gif_path) / (1024 * 1024)

print("\n" + "=" * 80)
print("✅ FINAL PROFESSIONAL GIF READY!")
print("=" * 80)
print(f"\n📍 File: {gif_path}")
print(f"📐 Size: {processed[0].width}x{processed[0].height}px")
print(f"📊 Frames: {len(screenshots)} (+ 1 loop frame)")
print(f"⏱️  Duration: {len(screenshots) * 5}s total, 5s per frame")
print(f"💾 File size: {size_mb:.2f} MB")

print("\n🎯 What's included:")
for i, (_, caption) in enumerate(screenshots, 1):
    print(f"  {i}. {caption}")

print("\n✨ Improvements:")
print("  ✓ Larger visualization area (minimal overlays)")
print("  ✓ 5 seconds per frame (readable)")
print("  ✓ Clean, professional captions")
print("  ✓ High resolution (1920px)")
print("  ✓ Optimized file size")

print("\n💡 Next: View with 'open agricultural_dashboard_animated.gif'")
print("         If good, commit and push!")

print("\n✅ Done!")
