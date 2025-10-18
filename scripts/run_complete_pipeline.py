#!/usr/bin/env python
"""
Complete Pipeline Runner - Farm Stock Prediction System

Executes the entire SRI model pipeline from data fetching to validation.

Steps:
1. Fetch crop yield data (USDA)
2. Fetch weather data (Visual Crossing or mock)
3. Fetch drought data (USDM or mock)
4. Run exploratory analysis
5. Create visualizations
6. Merge all datasets
7. Calculate SRI scores
8. Validate model

Usage:
    python run_complete_pipeline.py
"""

import subprocess
import sys
import time
from datetime import datetime

print("="*80)
print("🚀 FARM STOCK PREDICTION - COMPLETE PIPELINE")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("")

# Pipeline steps
STEPS = [
    {
        'name': '1. Fetch Crop Yield Data',
        'script': 'main.py',
        'description': 'Downloading USDA crop yield data (2010-2024)',
        'estimated_time': '15-20 seconds'
    },
    {
        'name': '2. Fetch Weather Data',
        'script': 'fetch_weather_real.py',
        'description': 'Getting weather data (temp, precipitation, GDD)',
        'estimated_time': '5 seconds (mock) or 2-5 minutes (API)'
    },
    {
        'name': '3. Fetch Drought Data',
        'script': 'fetch_drought_real.py',
        'description': 'Collecting drought severity indices',
        'estimated_time': '5 seconds'
    },
    {
        'name': '4. Exploratory Analysis',
        'script': 'eda_analysis.py',
        'description': 'Running statistical analysis on crop yields',
        'estimated_time': '5 seconds'
    },
    {
        'name': '5. Create Visualizations',
        'script': 'visualizations.py',
        'description': 'Generating charts and graphs',
        'estimated_time': '10 seconds'
    },
    {
        'name': '6. Merge Datasets',
        'script': 'merge_datasets.py',
        'description': 'Combining crop, weather, and drought data',
        'estimated_time': '5 seconds'
    },
    {
        'name': '7. Calculate SRI Scores',
        'script': 'sri_model.py',
        'description': 'Computing Stock Risk Index for all records',
        'estimated_time': '10 seconds'
    },
    {
        'name': '8. Validate Model',
        'script': 'validate_sri.py',
        'description': 'Testing model accuracy and performance',
        'estimated_time': '5 seconds'
    }
]

# Track results
results = []
start_time = time.time()

print("📋 PIPELINE STEPS:")
for i, step in enumerate(STEPS, 1):
    print(f"   {i}. {step['name']}")
print("")
print("⏱️  Estimated total time: ~1-6 minutes (depending on API usage)")
print("-" * 80)
print("")

# Execute each step
for i, step in enumerate(STEPS, 1):
    step_start = time.time()

    print(f"\n{'='*80}")
    print(f"STEP {i}/{len(STEPS)}: {step['name']}")
    print(f"{'='*80}")
    print(f"📝 {step['description']}")
    print(f"⏱️  Estimated: {step['estimated_time']}")
    print("")

    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, step['script']],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        step_time = time.time() - step_start

        if result.returncode == 0:
            print("\n" + "="*80)
            print(f"✅ STEP {i} COMPLETED SUCCESSFULLY")
            print(f"⏱️  Time taken: {step_time:.1f} seconds")
            print("="*80)

            results.append({
                'step': i,
                'name': step['name'],
                'status': 'SUCCESS',
                'time': step_time
            })
        else:
            print("\n" + "="*80)
            print(f"❌ STEP {i} FAILED")
            print(f"⏱️  Time taken: {step_time:.1f} seconds")
            print("="*80)
            print("\nError output:")
            print(result.stderr[:500])  # Show first 500 chars of error

            results.append({
                'step': i,
                'name': step['name'],
                'status': 'FAILED',
                'time': step_time
            })

            # Ask user if they want to continue
            print("\n⚠️  This step failed. Continue with remaining steps? (y/n): ", end="")
            response = input().strip().lower()
            if response != 'y':
                print("\n🛑 Pipeline stopped by user")
                break

    except subprocess.TimeoutExpired:
        print(f"\n❌ STEP {i} TIMEOUT")
        print(f"   Script took longer than 10 minutes")
        results.append({
            'step': i,
            'name': step['name'],
            'status': 'TIMEOUT',
            'time': 600
        })
        break

    except Exception as e:
        print(f"\n❌ STEP {i} ERROR")
        print(f"   {str(e)}")
        results.append({
            'step': i,
            'name': step['name'],
            'status': 'ERROR',
            'time': time.time() - step_start
        })
        break

# Final Summary
total_time = time.time() - start_time

print("\n\n" + "="*80)
print("📊 PIPELINE EXECUTION SUMMARY")
print("="*80)

success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
failed_count = sum(1 for r in results if r['status'] in ['FAILED', 'ERROR', 'TIMEOUT'])

print(f"\n📈 Results:")
print(f"   Total steps: {len(results)}/{len(STEPS)}")
print(f"   ✅ Successful: {success_count}")
print(f"   ❌ Failed: {failed_count}")
print(f"   ⏱️  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")

print(f"\n📋 Step-by-step results:")
for r in results:
    status_icon = "✅" if r['status'] == 'SUCCESS' else "❌"
    print(f"   {status_icon} Step {r['step']}: {r['name']}")
    print(f"      Status: {r['status']} | Time: {r['time']:.1f}s")

# Check if all steps succeeded
if success_count == len(STEPS):
    print("\n" + "="*80)
    print("🎉 ALL STEPS COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\n📂 Generated Files:")
    print("   Data:")
    print("   - usda_crop_yield_2010_2024.csv")
    print("   - weather_data_real_2010_2024.csv")
    print("   - drought_data_real_2010_2024.csv")
    print("   - merged_farm_data.csv")
    print("   - sri_results.csv")
    print("\n   Visualizations:")
    print("   - crop_yield_analysis.png")
    print("   - corn_yield_heatmap.png")
    print("   - sri_analysis.png")
    print("   - sri_validation.png")
    print("\n🎯 Next Steps:")
    print("   1. Review visualizations: open *.png")
    print("   2. Examine SRI results: head -20 sri_results.csv")
    print("   3. Check validation report: sri_validation.png")
    print("   4. Read documentation: README.md")

else:
    print("\n" + "="*80)
    print("⚠️  PIPELINE COMPLETED WITH ERRORS")
    print("="*80)
    print("\n💡 Troubleshooting:")
    print("   1. Check error messages above")
    print("   2. Ensure all dependencies installed: pip install -r requirements.txt")
    print("   3. Verify API keys in .env file (if using real data)")
    print("   4. Run failed steps individually for more details")

print("\n" + "="*80)
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
