"""
Create GIF from Production Matplotlib Visualizations
Uses high-quality PNG files with added PyNarrative-style text overlays
"""

from PIL import Image, ImageDraw, ImageFont
import os

print("🎬 Creating GIF from Production Visualizations...")
print("=" * 80)

viz_dir = '/Users/osmanorka/Farm_Stock_Predit/visualizations_2025_enhanced'

# Production visualizations with storytelling annotations
visualizations = [
    ('sri_distribution_2025.png',
     '📊 RISK DISTRIBUTION',
     '⚠️ Average: 23.7 | 👉 227 states in LOW RISK zone | Focus procurement here'),

    ('top_states_2025.png',
     '🗺️ TOP 15 HIGH-RISK STATES',
     '🔥 TEXAS #1 (36.2) | WYOMING #2 (35.6) | Prioritize these states immediately'),

    ('state_heatmap_2025.png',
     '🌡️ GEOGRAPHIC HEATMAP',
     '30 States × 3 Commodities | Red = Critical | Green = Stable | Spot patterns'),

    ('commodity_comparison_2025.png',
     '🌾 COMMODITY COMPARISON',
     'Violin + Box plots | Diamond = Mean | Compare risk across CORN/SOYBEANS/WHEAT'),

    ('risk_component_breakdown_2025.png',
     '⚙️ RISK COMPONENTS',
     'Yield 35% | Weather 25% | Drought 25% | Economic 15% | Weighted breakdown'),
]

print(f"\n📂 Loading {len(visualizations)} production visualizations...")

images = []

for i, (filename, title, annotation) in enumerate(visualizations, 1):
    filepath = os.path.join(viz_dir, filename)

    if not os.path.exists(filepath):
        print(f"\n❌ Missing: {filename}")
        continue

    print(f"\n📸 [{i}/{len(visualizations)}] {title}")

    # Load production PNG
    img = Image.open(filepath)
    original_size = (img.width, img.height)

    # Resize to consistent width for GIF
    target_width = 2000
    aspect_ratio = img.height / img.width
    target_height = int(target_width * aspect_ratio)

    if img.width != target_width:
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        print(f"   Resized: {original_size} → {img.size}")
    else:
        print(f"   Size: {img.size}")

    # Convert to RGB
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Add PyNarrative-style overlays
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 52)
        anno_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        counter_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
    except:
        title_font = ImageFont.load_default()
        anno_font = ImageFont.load_default()
        counter_font = ImageFont.load_default()

    # TOP BANNER - Thinner and more transparent
    banner_height = 75
    banner = Image.new('RGBA', (img.width, banner_height), (28, 48, 29, 140))
    img.paste(banner, (0, 0), banner)

    # Title
    draw.text((20, 12), title, font=title_font, fill=(255, 255, 255))

    # BOTTOM ANNOTATION BANNER - For key insights
    bottom_banner_height = 110
    bottom_banner = Image.new('RGBA', (img.width, bottom_banner_height), (0, 0, 0, 180))
    img.paste(bottom_banner, (0, img.height - bottom_banner_height), bottom_banner)

    # Annotation text - PyNarrative style
    draw.text((20, img.height - bottom_banner_height + 15),
              annotation,
              font=anno_font,
              fill=(255, 215, 0))  # Golden color for emphasis

    # Frame counter - top right
    counter_text = f"{i}/{len(visualizations)}"
    bbox = draw.textbbox((0, 0), counter_text, font=counter_font)
    text_w = bbox[2] - bbox[0]

    counter_bg = Image.new('RGBA', (text_w + 40, 60), (0, 0, 0, 200))
    img.paste(counter_bg, (img.width - text_w - 60, 90), counter_bg)
    draw.text((img.width - text_w - 40, 100),
              counter_text, font=counter_font, fill=(124, 179, 66))

    images.append(img)
    print(f"   ✓ Processed with annotations")

if not images:
    print("\n❌ No images found!")
    exit(1)

print(f"\n✅ Processed {len(images)} visualizations")

# Add first frame at end for smooth loop
images.append(images[0].copy())

# Create GIF
output_path = '/Users/osmanorka/Farm_Stock_Predit/agricultural_dashboard_animated.gif'

print(f"\n🎞️ Creating animated GIF...")

images[0].save(
    output_path,
    save_all=True,
    append_images=images[1:],
    duration=5000,  # 5 seconds per frame
    loop=0,
    optimize=True,
    quality=95
)

file_size = os.path.getsize(output_path) / (1024 * 1024)

print("\n" + "=" * 80)
print("✅ PRODUCTION-QUALITY GIF CREATED!")
print("=" * 80)

print(f"\n📍 Location: {output_path}")
print(f"📐 Resolution: {images[0].width}x{images[0].height}px")
print(f"📊 Frames: {len(visualizations)} (+ 1 loop)")
print(f"⏱️  Duration: {len(visualizations) * 5}s total ({len(visualizations)} frames × 5s)")
print(f"💾 File Size: {file_size:.2f} MB")

print("\n🎯 Visualizations included:")
for i, (filename, title, annotation) in enumerate(visualizations, 1):
    print(f"  {i}. {title}")
    print(f"     💬 {annotation}")
    print(f"     📁 {filename}")
    print()

print("✨ Features:")
print("  ✓ Production matplotlib quality (not Altair)")
print("  ✓ Professional heatmaps and rankings")
print("  ✓ PyNarrative-style text annotations")
print("  ✓ Golden highlighting for key insights")
print("  ✓ Thin transparent banners")
print("  ✓ Bottom annotation bar for context")

print("\n💡 These are the REAL production visualizations!")
print("   Generated by the Airflow SRI pipeline with comprehensive analysis.")

print("\n📂 Next: View with 'open agricultural_dashboard_animated.gif'")

print("\n✅ Done!")
