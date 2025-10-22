"""
Create Professional GIF from Enhanced Visualizations (2025)
Uses the actual high-quality PNG visualizations from production pipeline
"""

from PIL import Image, ImageDraw, ImageFont
import os

print("🎬 Creating GIF from Enhanced Visualizations (2025)...")
print("=" * 80)

viz_dir = '/Users/osmanorka/Farm_Stock_Predit/visualizations_2025_enhanced'

# The actual visualizations in order of storytelling
visualizations = [
    ('sri_distribution_2025.png',
     '📊 RISK DISTRIBUTION ANALYSIS',
     '380 state-commodity combinations | Most fall in LOW-MODERATE risk zones'),

    ('top_states_2025.png',
     '🗺️ TOP 15 HIGH-RISK STATES',
     'Priority states for procurement focus | Color-coded by severity level'),

    ('state_heatmap_2025.png',
     '🌡️ GEOGRAPHIC RISK HEATMAP',
     'Top 30 states × commodities | Red = Critical Risk | Green = Stable Conditions'),

    ('commodity_comparison_2025.png',
     '🌾 COMMODITY RISK COMPARISON',
     'Violin + Box plots showing distribution | Diamond markers = Mean values'),

    ('risk_component_breakdown_2025.png',
     '⚙️ RISK COMPONENT BREAKDOWN',
     'Left: Individual risk scores | Right: Weighted contribution to SRI'),
]

print(f"\n📂 Loading {len(visualizations)} visualizations from:")
print(f"   {viz_dir}")

images = []

for i, (filename, title, description) in enumerate(visualizations, 1):
    filepath = os.path.join(viz_dir, filename)

    if not os.path.exists(filepath):
        print(f"\n❌ Missing: {filename}")
        continue

    print(f"\n📸 [{i}/{len(visualizations)}] {filename}")

    # Load the high-quality PNG
    img = Image.open(filepath)
    original_size = (img.width, img.height)

    # These are already high-quality, just ensure consistent sizing
    target_width = 2000  # Keep them large
    aspect_ratio = img.height / img.width
    target_height = int(target_width * aspect_ratio)

    if img.width != target_width:
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        print(f"   Resized: {original_size} → {img.size}")
    else:
        print(f"   Size: {img.size}")

    # Convert to RGB if needed (for GIF compatibility)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Add minimal professional overlay
    draw = ImageDraw.Draw(img)

    # Try to load font
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 50)
        desc_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        counter_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
    except:
        title_font = ImageFont.load_default()
        desc_font = ImageFont.load_default()
        counter_font = ImageFont.load_default()

    # Add semi-transparent top banner (minimal)
    banner_height = 140
    overlay = Image.new('RGBA', (img.width, banner_height), (44, 95, 45, 235))

    # Paste overlay on original image
    img_with_overlay = img.copy()
    img_with_overlay.paste(overlay, (0, 0), overlay)

    # Now draw text
    draw = ImageDraw.Draw(img_with_overlay)

    # Title
    draw.text((25, 25), title, font=title_font, fill=(255, 255, 255))

    # Description
    draw.text((25, 85), description, font=desc_font, fill=(200, 255, 200))

    # Frame counter - bottom right corner
    counter_text = f"{i}/{len(visualizations)}"

    # Get text size for background
    bbox = draw.textbbox((0, 0), counter_text, font=counter_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Add semi-transparent background for counter
    counter_bg = Image.new('RGBA', (text_width + 50, text_height + 40), (0, 0, 0, 200))
    img_with_overlay.paste(counter_bg,
                           (img.width - text_width - 75, img.height - text_height - 65),
                           counter_bg)

    # Draw counter text
    draw.text((img.width - text_width - 50, img.height - text_height - 50),
              counter_text, font=counter_font, fill=(124, 179, 66))

    images.append(img_with_overlay)
    print(f"   ✓ Processed")

if not images:
    print("\n❌ No images found!")
    exit(1)

print(f"\n✅ Loaded {len(images)} visualizations")

# Add first frame at end for smooth looping
images.append(images[0].copy())

# Create high-quality GIF
output_path = '/Users/osmanorka/Farm_Stock_Predit/agricultural_dashboard_animated.gif'

print(f"\n🎞️ Creating animated GIF...")
print(f"   Output: {output_path}")

images[0].save(
    output_path,
    save_all=True,
    append_images=images[1:],
    duration=5000,  # 5 seconds per frame - enough time to read
    loop=0,
    optimize=True,
    quality=95
)

file_size = os.path.getsize(output_path) / (1024 * 1024)

print("\n" + "=" * 80)
print("✅ HIGH-QUALITY GIF CREATED!")
print("=" * 80)

print(f"\n📍 Location: {output_path}")
print(f"📐 Resolution: {images[0].width}x{images[0].height}px")
print(f"📊 Frames: {len(visualizations)} (+ 1 loop frame)")
print(f"⏱️  Total Duration: {len(visualizations) * 5}s ({len(visualizations)} frames × 5s)")
print(f"💾 File Size: {file_size:.2f} MB")

print("\n🎯 Visualizations included:")
for i, (filename, title, _) in enumerate(visualizations, 1):
    print(f"  {i}. {title}")
    print(f"     Source: {filename}")

print("\n✨ Features:")
print("  ✓ Uses production-quality visualizations from pipeline")
print("  ✓ Professional matplotlib styling preserved")
print("  ✓ Clean captions with context")
print("  ✓ 5 seconds per frame (readable)")
print("  ✓ High resolution maintained")
print("  ✓ Smooth looping animation")

print("\n💡 These are the REAL visualizations from your SRI analysis!")
print("   They show actual 2025 data with professional styling.")

print("\n📂 Next steps:")
print("  1. View: open agricultural_dashboard_animated.gif")
print("  2. Verify quality and annotations visibility")
print("  3. Commit: git add agricultural_dashboard_animated.gif")
print("  4. Push to GitHub")

print("\n✨ Done!")
