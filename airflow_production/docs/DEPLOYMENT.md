# 🚀 Agricultural SRI Pipeline - Deployment Guide

Complete step-by-step guide to deploy the production Airflow system.

---

## 📋 Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Disk**: 20GB free space
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+

### API Keys Needed
1. **USDA NASS QuickStats** (Free)
   - Sign up: https://quickstats.nass.usda.gov/api
   - Get API key instantly

2. **Visual Crossing Weather** (Optional - 1000 free calls/day)
   - Sign up: https://www.visualcrossing.com/sign-up
   - Upgrade for production use

3. **AWS Account** (Optional - for S3 report storage)
   - Create IAM user with S3 access
   - Get Access Key + Secret Key

---

## 🐳 Option 1: Docker Deployment (Recommended)

### Step 1: Clone & Navigate
```bash
cd Farm_Stock_Predit/airflow_production
```

### Step 2: Configure Environment
```bash
# Copy example environment file
cd docker
cp .env.example .env

# Edit with your actual values
nano .env
```

**Required Configuration:**
```bash
# Airflow Admin
AIRFLOW_ADMIN_USER=admin
AIRFLOW_ADMIN_PASSWORD=your_secure_password

# Email/SMTP (for alerts)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_MAIL_FROM=alerts@agcompany.com

# API Keys
USDA_API_KEY=YOUR_USDA_KEY_HERE
VISUAL_CROSSING_API_KEY=YOUR_WEATHER_KEY  # Optional
AWS_ACCESS_KEY_ID=YOUR_AWS_KEY  # Optional
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET  # Optional

# Stakeholders
STAKEHOLDER_EMAILS=trader1@company.com,policy@usda.gov
```

### Step 3: Start Services
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f airflow-webserver
```

**Services Started:**
- ✅ Airflow Webserver (port 8080)
- ✅ Airflow Scheduler
- ✅ PostgreSQL Database
- ✅ Redis Message Broker
- ✅ Celery Worker
- ✅ FastAPI Server (port 8000)

### Step 4: Access Airflow UI
```bash
# Open browser
http://localhost:8080

# Login with credentials from .env
Username: admin
Password: (your password)
```

### Step 5: Verify Installation
```bash
# Check DAG is loaded
# In Airflow UI, you should see:
# - DAG: agricultural_sri_annual_report
# - Status: Paused (initially)

# Test FastAPI
curl http://localhost:8000/health
```

### Step 6: Trigger Test Run
```bash
# Option A: Via UI
# 1. Go to http://localhost:8080
# 2. Find DAG: agricultural_sri_annual_report
# 3. Click "Trigger DAG" (play button)

# Option B: Via CLI
docker-compose exec airflow-webserver airflow dags trigger agricultural_sri_annual_report
```

---

## 💻 Option 2: Local Installation (Without Docker)

### Step 1: Install Python Dependencies
```bash
cd Farm_Stock_Predit/airflow_production

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Initialize Airflow
```bash
# Set Airflow home
export AIRFLOW_HOME=$(pwd)

# Initialize database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@agcompany.com
```

### Step 3: Configure Airflow
```bash
# Edit airflow.cfg
nano airflow.cfg

# Key settings:
dags_folder = /path/to/airflow_production/dags
load_examples = False
executor = LocalExecutor  # or CeleryExecutor
```

### Step 4: Set Environment Variables
```bash
# Create .env file
cp docker/.env.example .env
source .env  # Load environment variables
```

### Step 5: Start Airflow Services
```bash
# Terminal 1: Webserver
airflow webserver --port 8080

# Terminal 2: Scheduler
airflow scheduler

# Terminal 3: FastAPI (optional)
cd api
uvicorn main:app --reload --port 8000
```

### Step 6: Access UI
```bash
http://localhost:8080
```

---

## 📅 Configure Pipeline Schedule

### Default Schedule (Annual - October 1st)
```python
# Already configured in DAG
schedule_interval='0 0 1 10 *'
```

### Custom Schedules

**Quarterly Updates:**
```python
# Edit dags/agricultural_sri_pipeline.py
schedule_interval='0 0 1 */3 *'  # Every 3 months
```

**Monthly Monitoring:**
```python
schedule_interval='0 0 1 * *'  # 1st of every month
```

**Manual Only:**
```python
schedule_interval=None  # Disable automatic runs
```

---

## 🔧 Post-Deployment Configuration

### 1. Set Up Email Alerts

**Gmail Configuration:**
```bash
# In .env file
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Not your regular password!

# Get Gmail App Password:
# 1. Go to Google Account Settings
# 2. Security → 2-Step Verification
# 3. App passwords → Generate new
```

**SendGrid (Alternative):**
```bash
# Install SendGrid
pip install sendgrid

# Configure in .env
SENDGRID_API_KEY=YOUR_KEY
```

### 2. Configure AWS S3 (Optional)

**Create S3 Bucket:**
```bash
# Using AWS CLI
aws s3 mb s3://agricultural-risk-reports

# Set public access (for reports)
aws s3 website s3://agricultural-risk-reports/ \
    --index-document index.html
```

**IAM Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::agricultural-risk-reports/*",
        "arn:aws:s3:::agricultural-risk-reports"
      ]
    }
  ]
}
```

### 3. Set Up Connections in Airflow

```bash
# Via Airflow UI:
# Admin → Connections → Add

# Or via CLI:
docker-compose exec airflow-webserver \
  airflow connections add usda_api \
  --conn-type http \
  --conn-host https://quickstats.nass.usda.gov \
  --conn-password YOUR_API_KEY
```

---

## 📊 Monitoring & Maintenance

### View Logs
```bash
# Docker logs
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-worker

# Airflow UI logs
# Go to DAG → Graph → Click task → Logs
```

### Monitor Resources
```bash
# Docker stats
docker stats

# Celery Flower (if enabled)
http://localhost:5555
```

### Database Backup
```bash
# Backup Postgres
docker-compose exec postgres pg_dump -U airflow airflow > backup.sql

# Restore
cat backup.sql | docker-compose exec -T postgres psql -U airflow airflow
```

---

## 🧪 Testing the Pipeline

### Test Individual Stages

**Stage 1: Data Collection**
```bash
docker-compose exec airflow-worker \
  python /opt/airflow/dags/scripts/data_collectors/crop_data_collector.py 2024 /tmp
```

**Stage 2: Data Processing**
```bash
# Test data validation
python scripts/processors/data_validator.py
```

**Stage 3: SRI Calculation**
```bash
# Test SRI model
python scripts/models/sri_calculator.py
```

### Test Full Pipeline
```bash
# Trigger DAG with specific date
airflow dags test agricultural_sri_annual_report 2024-10-01
```

---

## 🔒 Security Best Practices

### 1. Secure API Keys
```bash
# NEVER commit .env to git
echo ".env" >> .gitignore

# Use Airflow Connections for secrets
# Store in encrypted database, not files
```

### 2. Change Default Passwords
```bash
# Airflow admin password
AIRFLOW_ADMIN_PASSWORD=StrongPassword123!

# Database password
POSTGRES_PASSWORD=SecureDBPassword456!
```

### 3. Restrict Network Access
```bash
# In docker-compose.yml
# Expose only necessary ports
# Use firewall rules for production
```

### 4. Enable HTTPS
```bash
# Use nginx reverse proxy
# Configure SSL certificates
# Force HTTPS redirect
```

---

## 🚨 Troubleshooting

### Issue: DAG not showing in UI
```bash
# Check DAG syntax
docker-compose exec airflow-scheduler \
  python /opt/airflow/dags/agricultural_sri_pipeline.py

# Restart scheduler
docker-compose restart airflow-scheduler
```

### Issue: Task failing with import errors
```bash
# Install missing packages
docker-compose exec airflow-worker pip install package-name

# Or rebuild image with dependencies
docker-compose build --no-cache
```

### Issue: Email not sending
```bash
# Test SMTP connection
docker-compose exec airflow-worker \
  python -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587)"

# Check email configuration in .env
```

### Issue: Out of memory
```bash
# Increase Docker memory
# Docker Desktop → Settings → Resources → Memory: 8GB+

# Or reduce worker count
# In docker-compose.yml: scale workers down
```

---

## 📈 Production Deployment Checklist

- [ ] Environment variables configured (.env)
- [ ] API keys added and tested
- [ ] Email/SMTP working
- [ ] S3 bucket created (if using)
- [ ] DAG schedule configured
- [ ] Stakeholder emails list updated
- [ ] Test run completed successfully
- [ ] Monitoring alerts configured
- [ ] Database backup strategy in place
- [ ] Documentation reviewed
- [ ] Security audit completed

---

## 🔄 Updating the System

### Update Docker Images
```bash
docker-compose pull
docker-compose up -d
```

### Update DAG Code
```bash
# Edit dags/agricultural_sri_pipeline.py
# No restart needed - Airflow auto-detects changes

# Or force refresh
docker-compose restart airflow-scheduler
```

### Update Scripts
```bash
# Edit scripts in scripts/ folder
# Restart worker to reload
docker-compose restart airflow-worker
```

---

## 📞 Support

### Common Commands
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# View service status
docker-compose ps

# Restart single service
docker-compose restart airflow-webserver

# Execute command in container
docker-compose exec airflow-worker bash
```

### Useful Links
- Airflow Documentation: https://airflow.apache.org/docs/
- Docker Compose Docs: https://docs.docker.com/compose/
- FastAPI Docs: https://fastapi.tiangolo.com/

---

## ✅ Next Steps After Deployment

1. **Verify System Health**
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8000/health
   ```

2. **Run Test Pipeline**
   - Trigger DAG manually
   - Monitor execution in UI
   - Check output data files

3. **Review Generated Reports**
   - Check `/data/reports/{year}/`
   - Verify email delivery
   - Test API endpoints

4. **Schedule Production Run**
   - Unpause DAG in UI
   - Wait for October 1st
   - Or set custom schedule

5. **Share API with Stakeholders**
   ```
   API Endpoint: http://your-server:8000
   Documentation: http://your-server:8000/docs
   ```

---

**Deployment Complete!** 🎉

Your agricultural SRI pipeline is now ready to automatically deliver market intelligence every year.

---

Last Updated: October 18, 2025
Version: 1.0.0
