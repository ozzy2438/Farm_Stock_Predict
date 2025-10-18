# 🚀 Agricultural SRI Production Pipeline

**Automated Agricultural Risk Assessment & Market Intelligence System**

This is the **production-grade Airflow pipeline** that automatically:
- Collects agricultural data from USDA APIs
- Calculates Stock Risk Index (SRI) scores
- Generates market reports
- Distributes insights to stakeholders

---

## 📁 Folder Structure

```
airflow_production/
├── dags/                          # Airflow DAG definitions
│   └── agricultural_sri_pipeline.py
│
├── scripts/                       # Production ETL scripts
│   ├── data_collectors/           # Fetch data from APIs
│   ├── processors/                # Clean & merge data
│   ├── models/                    # SRI calculation
│   └── reporters/                 # Generate reports
│
├── config/                        # Configuration files
│   ├── airflow.cfg                # Airflow settings
│   ├── connections.yaml           # API credentials
│   └── variables.yaml             # Pipeline parameters
│
├── docker/                        # Docker deployment
│   ├── docker-compose.yml         # Complete stack
│   ├── Dockerfile                 # Custom Airflow image
│   └── .env.example               # Environment variables
│
├── api/                          # FastAPI market data endpoint
│   ├── main.py                    # API server
│   └── endpoints/                 # API routes
│
├── templates/                    # HTML report templates
│   ├── market_summary.html        # Executive summary
│   └── state_report.html          # State-specific reports
│
├── tests/                        # Unit & integration tests
│
├── data/                         # Data storage (gitignored)
│   ├── raw/                      # Raw API responses
│   ├── processed/                # Cleaned data
│   ├── results/                  # SRI scores
│   └── reports/                  # Generated reports
│
└── docs/                         # Documentation
    ├── DEPLOYMENT.md              # Deployment guide
    └── API_DOCS.md                # API documentation
```

---

## 🎯 What This System Does

### Annual Pipeline (Runs October 1st)

**Stage 1: Data Collection**
- Fetches crop yield data (USDA NASS)
- Fetches weather data (Visual Crossing)
- Fetches drought data (US Drought Monitor)
- Fetches economic indicators (WASDE/FAS PSD)

**Stage 2: Data Processing**
- Validates data quality
- Merges all datasets
- Engineers features for SRI model

**Stage 3: Risk Calculation**
- Calculates SRI scores for all 50 states
- Validates model output
- Compares with previous years

**Stage 4: Report Generation**
- Creates executive market summary
- Generates state-specific reports
- Produces visualizations & charts

**Stage 5: Distribution**
- Uploads reports to S3/cloud storage
- Sends email alerts to stakeholders
- Updates live API endpoints
- Refreshes Power BI/Tableau dashboards

---

## 🚀 Quick Start

### Option A: Docker (Recommended)
```bash
cd airflow_production/docker
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d
```

Access Airflow UI: http://localhost:8080

### Option B: Local Installation
```bash
cd airflow_production
pip install -r requirements.txt
airflow db init
airflow users create --username admin --password admin --role Admin
airflow webserver --port 8080
# In another terminal:
airflow scheduler
```

---

## 📅 Pipeline Schedule

**Default**: Annual run on October 1st at 00:00 UTC
```python
schedule_interval='0 0 1 10 *'
```

**Optional schedules**:
- Quarterly: `'0 0 1 */3 *'`
- Monthly: `'0 0 1 * *'`
- Manual trigger: via Airflow UI

---

## 📊 Outputs

### 1. Market Summary Report
- **Format**: HTML/PDF
- **Audience**: Traders, policymakers, executives
- **Content**:
  - National production totals
  - High-risk states requiring stockpiling
  - Recommended actions

### 2. Data Exports
- `sri_results_{year}.csv` - Full SRI scores
- `high_risk_states.json` - API-ready format
- `state_reports/*.csv` - Individual state data

### 3. API Endpoint
```bash
GET https://api.yourcompany.com/sri/latest
GET https://api.yourcompany.com/sri/{year}
GET https://api.yourcompany.com/sri/state/{state_name}
```

### 4. Dashboards
- Power BI: Auto-refreshed from S3
- Tableau: Connected to API endpoint

---

## 🔧 Configuration

### API Keys (Required)
```yaml
# config/connections.yaml
usda_nass_api_key: "YOUR_KEY_HERE"
visual_crossing_api_key: "YOUR_KEY_HERE"
aws_access_key: "YOUR_KEY_HERE"
aws_secret_key: "YOUR_KEY_HERE"
```

### Email Alerts
```yaml
# config/variables.yaml
stakeholder_emails:
  - traders@market.com
  - policy@usda.gov
  - executives@agcompany.com
```

---

## 📈 Monitoring

**Airflow UI**: http://localhost:8080
- DAG runs history
- Task success/failure rates
- Execution logs

**Alerts**:
- Email on pipeline failure
- Slack notifications (optional)
- PagerDuty integration (optional)

---

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Test DAG
airflow dags test agricultural_sri_annual_report 2025-10-01

# Validate data quality
python scripts/validators/test_data_quality.py
```

---

## 📚 Documentation

- [Deployment Guide](docs/DEPLOYMENT.md)
- [API Documentation](docs/API_DOCS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

---

## 🔐 Security

- API keys stored in Airflow Connections (encrypted)
- S3 buckets with IAM policies
- Email via encrypted SMTP
- No credentials in code or git

---

## 🌟 Features

✅ Fully automated annual pipeline
✅ Data validation & quality checks
✅ Retry logic for API failures
✅ Email notifications to stakeholders
✅ Cloud storage integration (S3/Azure/GCP)
✅ RESTful API for market access
✅ Docker-based deployment
✅ Production-ready logging
✅ Comprehensive testing

---

## 🎯 Business Value

**For Commodity Traders:**
- Early warning of supply shortages → Better pricing decisions
- Historical trend analysis → Market predictions

**For Policymakers:**
- Evidence-based stockpiling → Budget optimization
- State-level risk assessment → Targeted interventions

**For Agricultural Companies:**
- Automated reporting → Cost savings
- Real-time API access → System integration

---

## 🆘 Support

For issues or questions:
1. Check [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
2. Review Airflow logs: `docker-compose logs -f airflow-webserver`
3. Contact: engineering@yourcompany.com

---

**Last Updated**: October 18, 2025
**Version**: 1.0.0
**Status**: Production Ready 🚀
