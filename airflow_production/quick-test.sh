#!/bin/bash

# ==============================================================================
# Agricultural SRI System - Quick Test Script
# ==============================================================================
# This script helps you quickly test the entire system
# ==============================================================================

set -e  # Exit on error

echo "🌾 Agricultural SRI System - Quick Test"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Change to docker directory
cd "$(dirname "$0")/docker" || exit 1

# Step 1: Check Docker
echo "Step 1: Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running!"
    echo ""
    echo "Please start Docker Desktop and try again."
    echo "1. Open Docker Desktop"
    echo "2. Wait for it to start (icon should be solid)"
    echo "3. Run this script again"
    exit 1
fi
print_status "Docker is running"
echo ""

# Step 2: Check .env file
echo "Step 2: Checking configuration..."
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    print_warning "Please edit .env file and add your API keys"
    exit 1
fi
print_status "Configuration file exists"
echo ""

# Step 3: Start services
echo "Step 3: Starting Docker services..."
echo "This may take 2-3 minutes on first run..."
docker compose up -d
echo ""
print_status "Services started"
echo ""

# Step 4: Wait for services to be ready
echo "Step 4: Waiting for services to initialize..."
echo "Waiting 60 seconds for Airflow to be ready..."
sleep 60

# Check if webserver is up
for i in {1..10}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        print_status "Airflow webserver is ready"
        break
    fi
    if [ $i -eq 10 ]; then
        print_warning "Airflow webserver not responding yet"
        echo "Check status with: docker compose logs airflow-webserver"
    fi
    sleep 5
done
echo ""

# Step 5: Check service status
echo "Step 5: Checking service status..."
docker compose ps
echo ""

# Step 6: Instructions
echo "======================================"
echo "🎉 System Started Successfully!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Access Airflow UI:"
echo "   ${GREEN}http://localhost:8080${NC}"
echo "   Username: admin"
echo "   Password: test_password_123"
echo ""
echo "2. Find the DAG named:"
echo "   ${GREEN}agricultural_sri_annual_report${NC}"
echo ""
echo "3. Unpause and trigger the DAG:"
echo "   - Toggle switch to ON (blue)"
echo "   - Click Play button → Trigger DAG"
echo ""
echo "4. Access API documentation:"
echo "   ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "5. Monitor logs:"
echo "   docker compose logs -f"
echo ""
echo "6. View results after pipeline completes:"
echo "   cd ../data/reports/2024/"
echo "   open market_summary_2024.html"
echo ""
echo "======================================"
echo "For detailed testing guide, see:"
echo "${YELLOW}TEST_GUIDE.md${NC}"
echo "======================================"
echo ""
echo "To stop the system:"
echo "  docker compose down"
echo ""
