# 🧪 Agricultural SRI System - Testing Guide

## ⚠️ Current Status

I've prepared your system for testing:
- ✅ Created `.env` file with test configuration
- ✅ Fixed docker-compose.yml (removed deprecated version)
- ✅ Created Dockerfile for FastAPI server
- ✅ All code files are ready

**Docker is currently unresponsive** - you'll need to restart Docker Desktop first.

---

## 🔧 Step 1: Restart Docker Desktop

Docker commands are timing out. Please restart Docker Desktop:

1. **Quit Docker Desktop completely**
   - Click Docker icon in menu bar
   - Select "Quit Docker Desktop"
   - Wait 10 seconds

2. **Start Docker Desktop again**
   - Open Docker Desktop application
   - Wait for it to fully start (icon turns solid)
   - You should see "Docker Desktop is running" in the menu

3. **Verify Docker is working**
   ```bash
   docker ps
   ```
   This should return quickly with a list of containers (may be empty).

---

## 🚀 Step 2: Start the Services

Once Docker is responsive, start the Airflow system:

```bash
# Navigate to docker directory
cd /Users/osmanorka/Farm_Stock_Predit/airflow_production/docker

# Start all services
docker compose up -d
```

**Expected output:**
```
[+] Running 7/7
 ✔ Network docker_default          Created
 ✔ Container docker-postgres-1      Started
 ✔ Container docker-redis-1         Started
 ✔ Container docker-airflow-init-1  Started
 ✔ Container docker-api-server-1    Started
 ✔ Container docker-airflow-webserver-1  Started
 ✔ Container docker-airflow-scheduler-1  Started
 ✔ Container docker-airflow-worker-1     Started
```

**This will take 2-3 minutes on first run** (pulling images and initializing).

---

## 📊 Step 3: Verify Services Are Running

Check that all services started successfully:

```bash
docker compose ps
```

**Expected output - all services should show "Up" or "healthy":**
```
NAME                             STATUS
docker-airflow-scheduler-1       Up (healthy)
docker-airflow-webserver-1       Up (healthy)
docker-airflow-worker-1          Up (healthy)
docker-api-server-1              Up
docker-postgres-1                Up (healthy)
docker-redis-1                   Up (healthy)
```

If any service shows "Exited" or "unhealthy", check logs:
```bash
docker compose logs <service-name>
```

---

## 🌐 Step 4: Access Airflow UI

1. **Open your web browser** and go to:
   ```
   http://localhost:8080
   ```

2. **Login with credentials:**
   - Username: `admin`
   - Password: `test_password_123`

3. **You should see the Airflow UI** with the DAG list.

---

## 🎯 Step 5: Find and Unpause the DAG

1. In the Airflow UI, look for the DAG named:
   ```
   agricultural_sri_annual_report
   ```

2. **Unpause the DAG:**
   - Toggle the switch on the left side to ON (blue)
   - This enables the DAG for execution

3. **View DAG details:**
   - Click on the DAG name
   - You'll see the DAG graph showing all 5 stages

---

## 🚦 Step 6: Trigger a Test Run

### Option A: Via Web UI (Recommended)

1. Click on the DAG name: `agricultural_sri_annual_report`
2. Click the **"Play" button** (▶️) in the top right
3. Select **"Trigger DAG"**
4. Click **"Trigger"** to confirm

### Option B: Via Command Line

```bash
docker compose exec airflow-webserver \
  airflow dags trigger agricultural_sri_annual_report
```

---

## 📈 Step 7: Monitor Execution

### Watch in Real-Time:

1. **In Airflow UI**, click on the DAG run (you'll see a new row appear)
2. Click **"Graph"** view to see task progress
3. Tasks will change colors:
   - **Gray** = Not started
   - **Yellow** = Running
   - **Green** = Success
   - **Red** = Failed

### Expected Execution Flow:

```
Stage 1: Data Collection (5-10 min)
├─ wait_for_data_availability ✓
├─ fetch_crop_yield ✓
├─ fetch_weather ⚠️ (may fail if no API key)
├─ fetch_drought ✓
└─ fetch_economic ✓

Stage 2: Data Processing (2 min)
├─ validate_data ✓
└─ merge_datasets ✓

Stage 3: SRI Calculation (3 min)
├─ calculate_sri ✓
├─ validate_sri ✓
└─ compare_with_previous_year ✓

Stage 4: Report Generation (5 min)
├─ generate_market_summary ✓
├─ generate_state_reports ✓
└─ generate_visualizations ✓

Stage 5: Distribution (2 min)
├─ upload_to_s3 ⚠️ (skipped - no AWS key)
├─ update_api_database ✓
└─ send_email_notifications ⚠️ (skipped - no SMTP)

✅ COMPLETE!
```

**Total time: ~20-30 minutes**

---

## 🔍 Step 8: View Results

### Check Generated Files:

```bash
# Navigate to data directory
cd /Users/osmanorka/Farm_Stock_Predit/airflow_production/data

# View directory structure
tree -L 3 .
```

**Expected output:**
```
data/
├── raw/2024/
│   ├── crop_yield_2024.csv
│   ├── weather_2024.csv (if API key provided)
│   ├── drought_2024.csv
│   └── economic_2024.csv
│
├── processed/2024/
│   └── merged_data_2024.csv
│
├── results/2024/
│   └── sri_results_2024.csv
│
└── reports/2024/
    ├── market_summary_2024.html
    ├── states/
    │   └── [50 state CSV files]
    └── visualizations/
        └── [5 PNG charts]
```

### View the Market Summary Report:

```bash
# Open the HTML report in your browser
open data/reports/2024/market_summary_2024.html
```

You should see a professional report with:
- Executive summary
- Critical alerts
- Top risk states
- Commodity analysis

---

## 🔌 Step 9: Test the API

### Check API Health:

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T...",
  "data_available": true,
  "available_years": [2024],
  "latest_year": 2024
}
```

### Get Latest SRI Data:

```bash
curl http://localhost:8000/sri/latest | jq
```

### View API Documentation:

Open in your browser:
```
http://localhost:8000/docs
```

You'll see interactive API documentation with all 10+ endpoints.

---

## 🐛 Troubleshooting

### Issue: Services won't start

```bash
# Check logs
docker compose logs -f

# Restart everything
docker compose down
docker compose up -d
```

### Issue: Airflow UI shows error

```bash
# Check webserver logs
docker compose logs airflow-webserver

# Restart webserver
docker compose restart airflow-webserver
```

### Issue: DAG not visible

```bash
# Check DAG for syntax errors
docker compose exec airflow-webserver \
  python /opt/airflow/dags/agricultural_sri_pipeline.py

# Restart scheduler
docker compose restart airflow-scheduler
```

### Issue: Tasks fail with "Module not found"

```bash
# Install missing dependencies
docker compose exec airflow-worker \
  pip install <package-name>

# Or rebuild containers
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Issue: Weather data collection fails

This is expected if you don't have a Visual Crossing API key. The pipeline will continue with other data sources.

---

## 📝 View Task Logs

To see detailed logs of any task:

1. In Airflow UI, click on the task (colored box)
2. Click **"Log"** button
3. View execution logs in detail

Or via command line:
```bash
docker compose exec airflow-worker \
  airflow tasks test agricultural_sri_annual_report fetch_crop_yield 2024-10-01
```

---

## 🛑 Stop the System

When you're done testing:

```bash
# Stop all services
docker compose down

# Stop and remove data volumes (clean slate)
docker compose down -v
```

---

## ✅ Success Indicators

Your test is successful if:

- ✅ All services start and show "healthy" status
- ✅ Airflow UI is accessible at http://localhost:8080
- ✅ DAG appears in the list
- ✅ DAG run completes (all tasks green)
- ✅ Market summary HTML is generated
- ✅ SRI results CSV is created
- ✅ API returns data at http://localhost:8000/sri/latest

---

## 📞 Next Steps After Testing

Once testing is successful:

1. **Add real API keys** to `.env`:
   - Visual Crossing for weather data
   - AWS credentials for S3 storage (optional)
   - Gmail SMTP for email alerts

2. **Configure stakeholder emails** in `.env`

3. **Set production schedule** (default is October 1st annually)

4. **Deploy to production server** (optional)

---

## 💡 Quick Commands Reference

```bash
# Start system
docker compose up -d

# Check status
docker compose ps

# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f airflow-scheduler

# Stop system
docker compose down

# Restart single service
docker compose restart airflow-webserver

# Access Airflow CLI
docker compose exec airflow-webserver airflow <command>

# Access worker shell
docker compose exec airflow-worker bash
```

---

**Ready to test!** Follow the steps above and let me know if you encounter any issues. 🚀
