# 🚀 Quick Start Guide - Agricultural SRI Production System

**Get your automated agricultural risk assessment pipeline running in 10 minutes!**

---

## ✅ What You Have

You now have a **complete production-grade Airflow system** that will:

1. **Automatically collect** agricultural data every October 1st
2. **Calculate risk scores** for all 50 US states
3. **Generate professional reports** for market stakeholders
4. **Send email alerts** to traders, policymakers, and executives
5. **Provide API access** for dashboards and integrations

---

## 🎯 Quick Start (3 Simple Steps)

### Step 1: Configure API Keys (2 minutes)
```bash
cd airflow_production/docker
cp .env.example .env
nano .env  # Edit with your keys
```

**Minimum required:**
```bash
AIRFLOW_ADMIN_PASSWORD=your_password_here
USDA_API_KEY=2EEF90B1-825E-322B-8B27-098A9C92D575  # Already provided!
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
```

**Get Gmail App Password:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Create App Password → Use that password

### Step 2: Start the System (1 minute)
```bash
docker-compose up -d
```

**Wait 60 seconds for initialization...**

### Step 3: Access & Trigger (1 minute)
```bash
# Open Airflow UI
http://localhost:8080

# Login: admin / (your password from Step 1)

# Unpause the DAG:
# Find: agricultural_sri_annual_report
# Toggle switch to ON (blue)

# Trigger manual run:
# Click "Play" button → "Trigger DAG"
```

**Done!** 🎉 Your pipeline is now running!

---

## 📊 What Happens Next?

### Real-Time Monitoring
Watch your pipeline execute:

```
Stage 1: Data Collection (5-10 minutes)
├─ ✓ Fetching crop yield data...
├─ ✓ Fetching weather data...
├─ ✓ Fetching drought data...
└─ ✓ Fetching economic data...

Stage 2: Data Processing (2-3 minutes)
├─ ✓ Validating data quality...
└─ ✓ Merging datasets...

Stage 3: SRI Calculation (3-5 minutes)
├─ ✓ Calculating risk scores...
├─ ✓ Validating model output...
└─ ✓ Comparing with previous year...

Stage 4: Report Generation (5 minutes)
├─ ✓ Generating market summary...
├─ ✓ Creating state reports...
└─ ✓ Building visualizations...

Stage 5: Distribution (2 minutes)
├─ ✓ Uploading to cloud...
├─ ✓ Updating API database...
└─ ✓ Sending email alerts...

✅ PIPELINE COMPLETE!
```

**Total runtime**: ~20-30 minutes

---

## 📂 Where to Find Your Results

### Generated Data Files
```bash
airflow_production/data/
├── raw/2024/                    # Raw API responses
│   ├── crop_yield_2024.csv
│   ├── weather_2024.csv
│   └── drought_2024.csv
│
├── processed/2024/              # Cleaned data
│   └── merged_data.csv
│
├── results/2024/                # SRI scores
│   └── sri_results.csv          # ⭐ Main output
│
└── reports/2024/                # Reports
    ├── market_summary.html      # Executive report
    ├── states/                  # State-specific CSVs
    └── visualizations/          # Charts & graphs
```

### View Reports
```bash
# Open market summary
open airflow_production/data/reports/2024/market_summary.html

# Or via API
curl http://localhost:8000/sri/latest
```

---

## 🌐 API Endpoints (Instant Access)

Your FastAPI server is running at http://localhost:8000

### Key Endpoints:
```bash
# Get latest SRI data
GET http://localhost:8000/sri/latest

# Get specific year
GET http://localhost:8000/sri/2024

# Get state-specific data
GET http://localhost:8000/sri/state/California

# Get high-risk states
GET http://localhost:8000/sri/high-risk?threshold=50

# Get statistics
GET http://localhost:8000/sri/statistics/2024

# Download CSV
GET http://localhost:8000/reports/2024/download

# Interactive docs
http://localhost:8000/docs
```

### Test It Now:
```bash
# Check if API is running
curl http://localhost:8000/health

# Get latest data (after pipeline runs)
curl http://localhost:8000/sri/latest | jq
```

---

## 📧 Email Report Example

After pipeline completes, stakeholders receive:

```
Subject: 🌾 Annual Agricultural Risk Report 2024

Dear Stakeholder,

The automated agricultural risk assessment has been completed for 2024.

KEY FINDINGS:
✓ National Average SRI: 24.3 (Moderate Risk)
✓ High-Risk States: 12 states require increased stockpiling
✓ Recommended Action: +15-25% inventory in high-risk regions

HIGH-RISK STATES:
• California (Wheat): SRI 78.2 → +25% stockpile
• Arizona (Corn): SRI 71.5 → +25% stockpile
• Missouri (Soybeans): SRI 63.8 → +20% stockpile

FULL REPORT: [View Market Summary]

---
Generated automatically by Agricultural SRI Pipeline
```

---

## 🔄 Scheduling (Production Mode)

### Default: Annual Run (October 1st)
```
The pipeline will automatically run every October 1st at midnight UTC.
No manual intervention needed!
```

### Change Schedule (Optional)
```bash
# Edit dags/agricultural_sri_pipeline.py

# Quarterly
schedule_interval='0 0 1 */3 *'

# Monthly
schedule_interval='0 0 1 * *'

# Weekly (Friday)
schedule_interval='0 0 * * 5'
```

---

## 📊 Understanding Your SRI Scores

### Risk Levels
```
SRI Score Range | Risk Level | Recommended Action
----------------|------------|-------------------
0 - 25          | Low        | Normal inventory
25 - 50         | Moderate   | Monitor closely
50 - 75         | High       | +15% stockpile
75 - 100        | Very High  | +25% stockpile
```

### What SRI Tells You
```
High SRI = Higher risk of supply shortage
         = Combination of:
           • Poor crop yields
           • Adverse weather
           • Severe drought

Use Case:
- Commodity traders → Price predictions
- Policymakers → Reserve planning
- Companies → Inventory optimization
```

---

## 🛠️ Common Tasks

### View Pipeline Logs
```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f airflow-scheduler

# Webserver
docker-compose logs -f airflow-webserver
```

### Stop the System
```bash
docker-compose down
```

### Restart the System
```bash
docker-compose restart
```

### Update Code
```bash
# Edit DAG or scripts
nano dags/agricultural_sri_pipeline.py

# No restart needed - Airflow auto-detects
# Or force restart:
docker-compose restart airflow-scheduler
```

---

## 🎯 Real-World Usage Examples

### For Commodity Traders
```bash
# Get high-risk states for price predictions
curl http://localhost:8000/sri/high-risk

# Check specific state trends
curl http://localhost:8000/sri/state/Iowa?years=5

# Download full data for analysis
wget http://localhost:8000/reports/2024/download
```

### For Policy Makers
```bash
# View market summary report
open http://localhost:8000/reports/2024/summary

# Get statistics for budget planning
curl http://localhost:8000/sri/statistics/2024
```

### For Dashboards (Power BI/Tableau)
```bash
# Connect to API endpoint
Data Source: Web
URL: http://your-server:8000/sri/latest

# Auto-refresh every hour
# Visualize high-risk states on map
```

---

## 📈 What to Expect

### First Run (Manual Test)
```
Duration: ~30 minutes
Output: Full SRI analysis for current/recent year
Reports: Market summary + state breakdowns
Email: Sent to stakeholders
API: Data available at /sri/latest
```

### Annual Production Run (Oct 1st)
```
Trigger: Automatic at 00:00 UTC
Data: Fresh harvest data from USDA
Analysis: 50 states × 3 crops = full coverage
Distribution: Reports + emails + API update
Monitoring: Email alerts if any issues
```

---

## 🔍 Verifying Success

### Check these after first run:

**1. Data Files Created**
```bash
ls airflow_production/data/results/2024/
# Should see: sri_results.csv
```

**2. API Working**
```bash
curl http://localhost:8000/sri/latest
# Should return: JSON with SRI data
```

**3. Reports Generated**
```bash
ls airflow_production/data/reports/2024/
# Should see: market_summary.html + state reports
```

**4. Email Sent**
```
Check your inbox for:
Subject: "Annual Agricultural Risk Report 2024"
```

**5. Airflow UI Shows Success**
```
All task boxes = Green
Final status = Success
```

---

## 🆘 Quick Troubleshooting

### Issue: Can't access Airflow UI
```bash
# Check if services are running
docker-compose ps

# Restart webserver
docker-compose restart airflow-webserver

# Wait 60 seconds, then try again
open http://localhost:8080
```

### Issue: DAG not visible
```bash
# Check DAG syntax
docker-compose exec airflow-scheduler \
  python /opt/airflow/dags/agricultural_sri_pipeline.py

# Restart scheduler
docker-compose restart airflow-scheduler
```

### Issue: Tasks failing
```bash
# View task logs in Airflow UI
# Click DAG → Graph → Click failed task → Logs

# Common fixes:
# 1. Check API keys in .env
# 2. Ensure internet connection
# 3. Check disk space
```

---

## 📚 Learn More

### Documentation
- [Full Deployment Guide](docs/DEPLOYMENT.md)
- [API Documentation](http://localhost:8000/docs)
- [System Architecture](PRODUCTION_SYSTEM_SUMMARY.md)

### Airflow Resources
- Airflow UI: http://localhost:8080
- Task logs: DAG → Graph → Task → Logs
- Connections: Admin → Connections
- Variables: Admin → Variables

### API Resources
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Interactive Test: http://localhost:8000/docs (click "Try it out")

---

## ✅ Next Steps

1. **Run your first pipeline** (follow steps above)
2. **Review generated reports** in `data/reports/`
3. **Test API endpoints** at http://localhost:8000
4. **Configure production schedule** (default: Oct 1st)
5. **Add stakeholder emails** in .env
6. **Set up cloud storage** (optional S3)
7. **Create dashboards** using API data

---

## 🎉 You're All Set!

Your agricultural risk assessment system is now:
- ✅ Fully automated
- ✅ Production-ready
- ✅ Delivering market intelligence
- ✅ Accessible via API
- ✅ Sending email alerts

**Questions?** Check `docs/DEPLOYMENT.md` for detailed guides.

**Issues?** Review logs: `docker-compose logs -f`

---

**Welcome to automated agricultural intelligence!** 🌾📊🚀

---

Last Updated: October 18, 2025
Version: 1.0.0
