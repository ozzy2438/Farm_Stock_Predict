"""
Create GIF from Annotated Altair Dashboards
Captures the interactive charts with arrows and "pay attention" markers
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image, ImageDraw, ImageFont
import time
import os

print("🎬 Creating GIF from Annotated Dashboards...")
print("=" * 80)

chrome_options = Options()
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=2400,1600')
chrome_options.add_argument('--force-device-scale-factor=2')
chrome_options.add_argument('--hide-scrollbars')

# Annotated dashboards with descriptions
dashboards = [
    ('annotated_1_distribution.html',
     '📊 RISK DISTRIBUTION',
     'Arrows show average risk & critical zones'),

    ('annotated_2_top_states.html',
     '🗺️ TOP PRIORITY STATES',
     '#1 most at-risk state marked with arrow'),

    ('annotated_3_commodities.html',
     '🌾 COMMODITY FOCUS',
     'Highest/lowest risk crops highlighted'),
]

base_path = '/Users/osmanorka/Farm_Stock_Predit'
screenshots = []

try:
    print("\n🌐 Starting browser...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    for i, (filename, title, desc) in enumerate(dashboards, 1):
        filepath = os.path.join(base_path, filename)

        print(f"\n📸 [{i}/{len(dashboards)}] {title}")
        print(f"   {desc}")

        driver.get(f'file://{filepath}')
        time.sleep(6)  # Wait for Altair to render

        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        screenshot_path = os.path.join(base_path, f'annotated_frame_{i}.png')
        driver.save_screenshot(screenshot_path)

        size_mb = os.path.getsize(screenshot_path) / (1024*1024)
        print(f"   ✓ Captured: {size_mb:.2f} MB")
        screenshots.append((screenshot_path, title, desc))

    driver.quit()
    print("\n✅ Screenshots complete!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Process screenshots
print("\n🎨 Processing screenshots...")

processed = []

for i, (path, title, desc) in enumerate(screenshots, 1):
    print(f"\n[{i}/{len(screenshots)}] {title}")

    img = Image.open(path)

    # Resize
    final_width = 2000
    aspect = img.height / img.width
    final_height = int(final_width * aspect)
    img = img.resize((final_width, final_height), Image.Resampling.LANCZOS)

    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        desc_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
        counter_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    except:
        title_font = ImageFont.load_default()
        desc_font = ImageFont.load_default()
        counter_font = ImageFont.load_default()

    # Thin transparent banner
    banner_height = 70
    banner = Image.new('RGBA', (img.width, banner_height), (44, 95, 45, 140))
    img.paste(banner, (0, 0), banner)

    # Title
    draw.text((20, 12), title, font=title_font, fill=(255, 255, 255))

    # Frame counter
    counter_text = f"{i}/{len(screenshots)}"
    bbox = draw.textbbox((0, 0), counter_text, font=counter_font)
    text_w = bbox[2] - bbox[0]

    counter_bg = Image.new('RGBA', (text_w + 40, 60), (0, 0, 0, 200))
    img.paste(counter_bg, (img.width - text_w - 60, img.height - 80), counter_bg)
    draw.text((img.width - text_w - 40, img.height - 65),
              counter_text, font=counter_font, fill=(124, 179, 66))

    processed.append(img)
    print(f"   ✓ {img.width}x{img.height}px")

    # Cleanup
    os.remove(path)

# Create GIF
print("\n🎞️ Creating animated GIF...")

# Add first frame at end for loop
processed.append(processed[0].copy())

gif_path = os.path.join(base_path, 'agricultural_dashboard_animated.gif')

processed[0].save(
    gif_path,
    save_all=True,
    append_images=processed[1:],
    duration=5000,  # 5 seconds per frame
    loop=0,
    optimize=True,
    quality=95
)

size_mb = os.path.getsize(gif_path) / (1024 * 1024)

print("\n" + "=" * 80)
print("✅ ANNOTATED GIF CREATED!")
print("=" * 80)

print(f"\n📍 File: {gif_path}")
print(f"📐 Resolution: {processed[0].width}x{processed[0].height}px")
print(f"📊 Frames: {len(screenshots)} (+ 1 loop)")
print(f"⏱️  Duration: {len(screenshots) * 5}s total")
print(f"💾 File size: {size_mb:.2f} MB")

print("\n🎯 Annotations included:")
print("  ✓ Arrows pointing to key insights")
print("  ✓ 'PAY ATTENTION' markers on critical areas")
print("  ✓ Priority rankings (#1 most at-risk state)")
print("  ✓ Focus guidance for audience")
print("  ✓ Statistical callouts (mean, max, min)")

print("\n📂 Dashboards featured:")
for i, (_, title, desc) in enumerate(dashboards, 1):
    print(f"  {i}. {title} - {desc}")

print("\n✨ This GIF uses Altair with PyNarrative-style annotations")
print("   to guide audience focus to critical insights!")

print("\n💡 Next: View with 'open agricultural_dashboard_animated.gif'")

print("\n✅ Done!")
