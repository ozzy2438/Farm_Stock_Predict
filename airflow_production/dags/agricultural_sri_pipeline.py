"""
Agricultural Stock Risk Index (SRI) Annual Pipeline

This DAG automatically runs every January 1st to:
1. Collect agricultural data from USDA APIs
2. Process and merge datasets
3. Calculate SRI risk scores
4. Generate market reports
5. Distribute insights to stakeholders

Schedule: Annual (January 1st, 00:00 UTC)
Owner: Agricultural Risk Team
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.python import PythonSensor
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# DAG CONFIGURATION
# =============================================================================

default_args = {
    'owner': 'agricultural_risk_team',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),  # Start from January 1, 2026
    'email': ['osmanorka@gmail.com'],  # Your email for reports
    'email_on_failure': True,
    'email_on_retry': False,
    'email_on_success': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=30),
    'execution_timeout': timedelta(hours=4),
}

dag = DAG(
    'agricultural_sri_annual_report',
    default_args=default_args,
    description='Annual agricultural risk assessment and market reporting pipeline',
    schedule_interval='0 0 1 1 *',  # January 1st, 00:00 UTC (every year)
    catchup=False,
    max_active_runs=1,
    tags=['production', 'agriculture', 'risk-assessment', 'annual'],
)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_current_year(**context):
    """Get the year for this pipeline run"""
    execution_date = context['execution_date']
    return execution_date.year

def check_data_availability(**context):
    """Sensor to check if USDA data is available for current year"""
    import requests
    import os

    year = get_current_year(**context)
    api_key = os.getenv('USDA_API_KEY', '2EEF90B1-825E-322B-8B27-098A9C92D575')

    # Test API availability
    url = "https://quickstats.nass.usda.gov/api/api_GET/"
    params = {
        'key': api_key,
        'year': year,
        'commodity_desc': 'CORN',
        'statisticcat_desc': 'YIELD',
        'format': 'JSON'
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json().get('data', [])
            if len(data) > 0:
                logger.info(f"✅ USDA data available for {year}: {len(data)} records found")
                return True
        logger.warning(f"⚠️ USDA data not yet available for {year}")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking data availability: {str(e)}")
        return False

# =============================================================================
# STAGE 1: DATA COLLECTION
# =============================================================================

with TaskGroup('data_collection', tooltip='Fetch data from external APIs', dag=dag) as data_collection_group:

    def fetch_crop_yield_data(**context):
        """Fetch crop yield data from USDA NASS QuickStats API"""
        import sys
        import os
        sys.path.append('/opt/airflow/dags/scripts/data_collectors')
        from crop_data_collector import fetch_all_crop_data

        year = get_current_year(**context)
        logger.info(f"📊 Fetching crop yield data for {year}")

        data_dir = f'/opt/airflow/data/raw/{year}'
        os.makedirs(data_dir, exist_ok=True)

        result = fetch_all_crop_data(year, output_dir=data_dir)

        context['ti'].xcom_push(key='crop_data_path', value=result['file_path'])
        context['ti'].xcom_push(key='crop_records', value=result['records'])

        logger.info(f"✅ Fetched {result['records']} crop yield records")
        return result

    def fetch_weather_data(**context):
        """Fetch weather data from Visual Crossing API"""
        import sys
        import os
        sys.path.append('/opt/airflow/dags/scripts/data_collectors')
        from weather_data_collector import fetch_all_weather_data

        year = get_current_year(**context)
        logger.info(f"🌦️ Fetching weather data for {year}")

        data_dir = f'/opt/airflow/data/raw/{year}'
        os.makedirs(data_dir, exist_ok=True)

        result = fetch_all_weather_data(year, output_dir=data_dir)

        context['ti'].xcom_push(key='weather_data_path', value=result['file_path'])
        context['ti'].xcom_push(key='weather_states', value=result['states'])

        logger.info(f"✅ Fetched weather data for {result['states']} states")
        return result

    def fetch_drought_data(**context):
        """Fetch drought severity data from US Drought Monitor"""
        import sys
        import os
        sys.path.append('/opt/airflow/dags/scripts/data_collectors')
        from drought_data_collector import fetch_all_drought_data

        year = get_current_year(**context)
        logger.info(f"🌵 Fetching drought data for {year}")

        data_dir = f'/opt/airflow/data/raw/{year}'
        os.makedirs(data_dir, exist_ok=True)

        result = fetch_all_drought_data(year, output_dir=data_dir)

        context['ti'].xcom_push(key='drought_data_path', value=result['file_path'])
        context['ti'].xcom_push(key='drought_states', value=result['states'])

        logger.info(f"✅ Fetched drought data for {result['states']} states")
        return result

    def fetch_economic_data(**context):
        """Fetch WASDE and FAS PSD economic indicators"""
        import sys
        import os
        sys.path.append('/opt/airflow/dags/scripts/data_collectors')
        from economic_data_collector import fetch_all_economic_data

        year = get_current_year(**context)
        logger.info(f"💰 Fetching economic data for {year}")

        data_dir = f'/opt/airflow/data/raw/{year}'
        os.makedirs(data_dir, exist_ok=True)

        result = fetch_all_economic_data(year, output_dir=data_dir)

        context['ti'].xcom_push(key='economic_data_path', value=result['file_path'])

        logger.info(f"✅ Fetched economic indicators")
        return result

    # Create tasks
    task_fetch_crops = PythonOperator(
        task_id='fetch_crop_yield',
        python_callable=fetch_crop_yield_data,
        dag=dag,
    )

    task_fetch_weather = PythonOperator(
        task_id='fetch_weather',
        python_callable=fetch_weather_data,
        dag=dag,
    )

    task_fetch_drought = PythonOperator(
        task_id='fetch_drought',
        python_callable=fetch_drought_data,
        dag=dag,
    )

    task_fetch_economic = PythonOperator(
        task_id='fetch_economic_indicators',
        python_callable=fetch_economic_data,
        dag=dag,
    )

# =============================================================================
# STAGE 2: DATA VALIDATION & PROCESSING
# =============================================================================

with TaskGroup('data_processing', tooltip='Validate and process collected data', dag=dag) as data_processing_group:

    def validate_data_quality(**context):
        """Validate collected data for completeness and quality"""
        import sys
        sys.path.append('/opt/airflow/dags/scripts/processors')
        from data_validator import validate_all_data

        year = get_current_year(**context)
        logger.info(f"🔍 Validating data quality for {year}")

        # Get data paths from XCom
        crop_path = context['ti'].xcom_pull(key='crop_data_path', task_ids='data_collection.fetch_crop_yield')
        weather_path = context['ti'].xcom_pull(key='weather_data_path', task_ids='data_collection.fetch_weather')
        drought_path = context['ti'].xcom_pull(key='drought_data_path', task_ids='data_collection.fetch_drought')
        economic_path = context['ti'].xcom_pull(key='economic_data_path', task_ids='data_collection.fetch_economic_indicators')

        validation_results = validate_all_data(
            crop_file=crop_path,
            weather_file=weather_path,
            drought_file=drought_path,
            economic_file=economic_path
        )

        # Check validation results
        if not validation_results.get('overall_passed', False):
            total_errors = validation_results.get('total_errors', 0)
            error_msg = f"❌ Data validation failed: {total_errors} errors found"
            logger.error(error_msg)
            raise ValueError(error_msg)

        total_warnings = validation_results.get('total_warnings', 0)
        logger.info(f"✅ Data validation passed ({total_warnings} warnings)")
        context['ti'].xcom_push(key='validation_results', value=validation_results)

        return validation_results

    def clean_and_merge_data(**context):
        """Clean and merge all datasets"""
        import sys
        sys.path.append('/opt/airflow/dags/scripts/processors')
        from data_merger import merge_all_data

        year = get_current_year(**context)
        logger.info(f"🔧 Merging datasets for {year}")

        # Get data paths
        crop_path = context['ti'].xcom_pull(key='crop_data_path', task_ids='data_collection.fetch_crop_yield')
        weather_path = context['ti'].xcom_pull(key='weather_data_path', task_ids='data_collection.fetch_weather')
        drought_path = context['ti'].xcom_pull(key='drought_data_path', task_ids='data_collection.fetch_drought')
        economic_path = context['ti'].xcom_pull(key='economic_data_path', task_ids='data_collection.fetch_economic_indicators')

        output_dir = f'/opt/airflow/data/processed/{year}'

        result = merge_all_data(
            crop_file=crop_path,
            weather_file=weather_path,
            drought_file=drought_path,
            economic_file=economic_path,
            output_dir=output_dir,
            year=year
        )

        context['ti'].xcom_push(key='merged_data_path', value=result['file_path'])
        context['ti'].xcom_push(key='merged_records', value=result['records'])

        logger.info(f"✅ Merged {result['records']} records")
        return result

    task_validate = PythonOperator(
        task_id='validate_data_quality',
        python_callable=validate_data_quality,
        dag=dag,
    )

    task_merge = PythonOperator(
        task_id='clean_and_merge',
        python_callable=clean_and_merge_data,
        dag=dag,
    )

    task_validate >> task_merge

# =============================================================================
# STAGE 3: SRI MODEL CALCULATION
# =============================================================================

with TaskGroup('sri_calculation', tooltip='Calculate Stock Risk Index scores', dag=dag) as sri_calculation_group:

    def calculate_sri_scores(**context):
        """Calculate SRI scores for all states and crops"""
        import sys
        sys.path.append('/opt/airflow/dags/scripts/models')
        from sri_calculator import calculate_sri

        year = get_current_year(**context)
        logger.info(f"📊 Calculating SRI scores for {year}")

        merged_data_path = context['ti'].xcom_pull(
            key='merged_data_path',
            task_ids='data_processing.clean_and_merge'
        )

        output_dir = f'/opt/airflow/data/results/{year}'

        result = calculate_sri(
            merged_file=merged_data_path,
            output_dir=output_dir,
            year=year
        )

        # Extract key metrics from stats
        stats = result.get('stats', {})
        high_risk_state_count = stats.get('high_risk_states', 0)
        avg_sri = stats.get('avg_sri', 0)
        risk_distribution = stats.get('risk_distribution', {})

        context['ti'].xcom_push(key='sri_results_path', value=result['file_path'])
        context['ti'].xcom_push(key='high_risk_state_count', value=high_risk_state_count)
        context['ti'].xcom_push(key='avg_sri', value=avg_sri)
        context['ti'].xcom_push(key='risk_distribution', value=risk_distribution)
        context['ti'].xcom_push(key='sri_stats', value=stats)

        logger.info(f"✅ Calculated SRI scores - Avg: {avg_sri:.1f}, High-risk states: {high_risk_state_count}")
        return result

    def validate_sri_model(**context):
        """Run validation tests on SRI output"""
        import sys
        sys.path.append('/opt/airflow/dags/scripts/models')
        from sri_validator import validate_sri_results

        year = get_current_year(**context)
        logger.info(f"🔍 Validating SRI model output for {year}")

        sri_results_path = context['ti'].xcom_pull(
            key='sri_results_path',
            task_ids='sri_calculation.calculate_sri_scores'
        )

        passed, validation_results = validate_sri_results(sri_file=sri_results_path)

        if not passed:
            logger.warning(f"⚠️ SRI validation warnings: {validation_results.get('errors', [])}")
        else:
            logger.info(f"✅ SRI validation passed")

        context['ti'].xcom_push(key='sri_validation', value=validation_results)
        context['ti'].xcom_push(key='sri_validation_passed', value=passed)
        return validation_results

    def compare_with_previous_year(**context):
        """Compare SRI scores with previous year for trend analysis"""
        import sys
        import os
        sys.path.append('/opt/airflow/dags/scripts/models')
        from sri_comparator import compare_sri_years

        year = get_current_year(**context)
        previous_year = year - 1

        logger.info(f"📈 Comparing {year} with {previous_year}")

        current_sri_path = context['ti'].xcom_pull(
            key='sri_results_path',
            task_ids='sri_calculation.calculate_sri_scores'
        )

        previous_sri_path = f'/opt/airflow/data/results/{previous_year}/sri_results_{previous_year}.csv'

        # Check if previous year data exists
        if not os.path.exists(previous_sri_path):
            logger.warning(f"⚠️ No previous year data found at {previous_sri_path}. Skipping comparison.")
            comparison = {
                'comparison_available': False,
                'message': f'No data available for {previous_year}',
                'current_year': year
            }
        else:
            output_dir = f'/opt/airflow/data/results/{year}/comparisons'

            comparison = compare_sri_years(
                current_file=current_sri_path,
                previous_file=previous_sri_path,
                output_dir=output_dir,
                current_year=year
            )
            comparison['comparison_available'] = True

        context['ti'].xcom_push(key='year_comparison', value=comparison)

        logger.info(f"✅ Year-over-year comparison complete")
        return comparison

    task_calculate_sri = PythonOperator(
        task_id='calculate_sri_scores',
        python_callable=calculate_sri_scores,
        dag=dag,
    )

    task_validate_sri = PythonOperator(
        task_id='validate_sri_model',
        python_callable=validate_sri_model,
        dag=dag,
    )

    task_compare_years = PythonOperator(
        task_id='compare_with_previous_year',
        python_callable=compare_with_previous_year,
        dag=dag,
    )

    task_calculate_sri >> [task_validate_sri, task_compare_years]

# =============================================================================
# STAGE 4: REPORT GENERATION
# =============================================================================

with TaskGroup('report_generation', tooltip='Generate market reports and visualizations', dag=dag) as report_generation_group:

    def generate_market_summary(**context):
        """Generate executive market summary report with embedded visualizations"""
        import sys
        import os
        sys.path.append('/opt/airflow/dags/scripts/reporters')
        from market_report_generator import generate_market_report

        year = get_current_year(**context)
        logger.info(f"📄 Generating market summary for {year}")

        # Get all required data from XCom
        sri_path = context['ti'].xcom_pull(key='sri_results_path', task_ids='sri_calculation.calculate_sri_scores')

        output_dir = f'/opt/airflow/data/reports/{year}'

        # Get visualization directory from XCom (generated by visualization task)
        viz_base_dir = context['ti'].xcom_pull(key='visualizations_dir', task_ids='report_generation.generate_visualizations')

        # The actual PNG files are in a subdirectory called 'visualizations'
        viz_dir = os.path.join(viz_base_dir, 'visualizations') if viz_base_dir else None

        logger.info(f"📊 Using visualizations from: {viz_dir}")

        report = generate_market_report(
            sri_file=sri_path,
            output_dir=output_dir,
            year=year,
            viz_dir=viz_dir
        )

        context['ti'].xcom_push(key='market_summary_path', value=report.get('file_path'))

        logger.info(f"✅ Market summary report generated with embedded visualizations")
        return report

    def generate_state_reports(**context):
        """Generate detailed reports for each state"""
        import sys
        sys.path.append('/opt/airflow/dags/scripts/reporters')
        from state_report_generator import generate_state_reports as gen_state_reports

        year = get_current_year(**context)
        logger.info(f"📊 Generating state-specific reports for {year}")

        sri_path = context['ti'].xcom_pull(key='sri_results_path', task_ids='sri_calculation.calculate_sri_scores')
        output_dir = f'/opt/airflow/data/reports/{year}/states'

        result = gen_state_reports(
            sri_file=sri_path,
            output_dir=output_dir,
            year=year
        )

        context['ti'].xcom_push(key='state_reports_dir', value=output_dir)
        context['ti'].xcom_push(key='states_generated', value=result.get('states_count', 0))

        logger.info(f"✅ Generated reports for {result.get('states_count', 0)} states")
        return result

    def generate_visualizations(**context):
        """Create charts and visualizations"""
        import sys
        sys.path.append('/opt/airflow/dags/scripts/reporters')
        from visualization_generator import generate_all_visualizations

        year = get_current_year(**context)
        logger.info(f"📈 Generating visualizations for {year}")

        sri_path = context['ti'].xcom_pull(key='sri_results_path', task_ids='sri_calculation.calculate_sri_scores')
        output_dir = f'/opt/airflow/data/reports/{year}/visualizations'

        result = generate_all_visualizations(
            sri_file=sri_path,
            output_dir=output_dir,
            year=year
        )

        context['ti'].xcom_push(key='visualizations_dir', value=output_dir)

        logger.info(f"✅ Generated {result.get('charts_count', 0)} visualizations")
        return result

    task_market_summary = PythonOperator(
        task_id='generate_market_summary',
        python_callable=generate_market_summary,
        dag=dag,
    )

    task_state_reports = PythonOperator(
        task_id='generate_state_reports',
        python_callable=generate_state_reports,
        dag=dag,
    )

    task_visualizations = PythonOperator(
        task_id='generate_visualizations',
        python_callable=generate_visualizations,
        dag=dag,
    )

    # Define dependencies within report generation group
    # Visualizations must complete before market summary (which embeds them)
    task_visualizations >> task_market_summary

# =============================================================================
# STAGE 5: DISTRIBUTION
# =============================================================================

with TaskGroup('distribution', tooltip='Distribute reports to stakeholders', dag=dag) as distribution_group:

    def upload_to_cloud_storage(**context):
        """Upload reports to S3/cloud storage"""
        import sys
        import os
        sys.path.append('/opt/airflow/dags/scripts/reporters')
        from cloud_uploader import upload_reports_to_s3

        year = get_current_year(**context)
        logger.info(f"☁️ Uploading reports to cloud storage for {year}")

        reports_dir = f'/opt/airflow/data/reports/{year}'

        # Check if AWS credentials are configured
        aws_key = os.getenv('AWS_ACCESS_KEY_ID')
        if not aws_key:
            logger.warning("⚠️ AWS credentials not configured. Skipping cloud upload.")
            result = {
                'success': False,
                'message': 'AWS credentials not configured',
                'public_url': 'N/A',
                's3_paths': []
            }
        else:
            result = upload_reports_to_s3(
                local_dir=reports_dir,
                s3_bucket='agricultural-risk-reports',
                s3_prefix=f'reports/{year}',
                year=year
            )

        context['ti'].xcom_push(key='public_url', value=result.get('public_url', 'N/A'))
        context['ti'].xcom_push(key='s3_paths', value=result.get('s3_paths', []))

        logger.info(f"✅ Cloud upload completed: {result.get('message', 'Success')}")
        return result

    def update_api_database(**context):
        """Update database for API endpoint"""
        import sys
        sys.path.append('/opt/airflow/dags/scripts/reporters')
        from api_updater import update_api_data

        year = get_current_year(**context)
        logger.info(f"🗄️ Updating API database for {year}")

        sri_path = context['ti'].xcom_pull(key='sri_results_path', task_ids='sri_calculation.calculate_sri_scores')
        api_data_dir = f'/opt/airflow/data/api/{year}'

        result = update_api_data(
            sri_file=sri_path,
            api_data_dir=api_data_dir,
            year=year
        )

        logger.info(f"✅ API database updated with {result.get('records', 0)} records")
        return result

    def send_stakeholder_notifications(**context):
        """Send email notifications to stakeholders"""
        year = get_current_year(**context)
        high_risk_state_count = context['ti'].xcom_pull(key='high_risk_state_count', task_ids='sri_calculation.calculate_sri_scores')
        avg_sri = context['ti'].xcom_pull(key='avg_sri', task_ids='sri_calculation.calculate_sri_scores')
        risk_distribution = context['ti'].xcom_pull(key='risk_distribution', task_ids='sri_calculation.calculate_sri_scores')
        public_url = context['ti'].xcom_pull(key='public_url', task_ids='distribution.upload_to_cloud_storage')

        # Calculate total high risk
        high_count = risk_distribution.get('high', 0) if risk_distribution else 0
        very_high_count = risk_distribution.get('very_high', 0) if risk_distribution else 0
        total_high_risk = high_count + very_high_count

        # Build email HTML
        email_html = f"""
        <html>
        <head><style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background-color: #2E7D32; color: white; padding: 20px; }}
            .summary {{ background-color: #f5f5f5; padding: 15px; margin: 20px 0; }}
            .high-risk {{ color: #d32f2f; font-weight: bold; }}
            .button {{ background-color: #2E7D32; color: white; padding: 10px 20px; text-decoration: none; display: inline-block; }}
        </style></head>
        <body>
            <div class="header">
                <h1>🌾 Annual Agricultural Risk Report {year}</h1>
            </div>

            <div class="summary">
                <h2>📊 Executive Summary</h2>
                <ul>
                    <li><b>Reporting Year:</b> {year}</li>
                    <li><b>National Average SRI:</b> {avg_sri:.1f}</li>
                    <li><b>High-Risk States:</b> <span class="high-risk">{high_risk_state_count} states require attention</span></li>
                    <li><b>High-Risk Records:</b> <span class="high-risk">{total_high_risk} records flagged</span></li>
                </ul>
            </div>

            <h3>⚠️ Risk Distribution:</h3>
            <p>High: {high_count} | Very High: {very_high_count}</p>

            <h3>📄 Access Full Report:</h3>
            <p><a href="{public_url}" class="button">View Market Summary Report</a></p>

            <hr>
            <p><small>This report was automatically generated by the Agricultural SRI Pipeline on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</small></p>
        </body>
        </html>
        """

        context['ti'].xcom_push(key='email_content', value=email_html)
        return email_html

    task_upload_cloud = PythonOperator(
        task_id='upload_to_cloud_storage',
        python_callable=upload_to_cloud_storage,
        dag=dag,
    )

    task_update_api = PythonOperator(
        task_id='update_api_database',
        python_callable=update_api_database,
        dag=dag,
    )

    task_prepare_email = PythonOperator(
        task_id='prepare_notifications',
        python_callable=send_stakeholder_notifications,
        dag=dag,
    )

    task_send_email = EmailOperator(
        task_id='send_email_alerts',
        to='osmanorka@gmail.com',  # Your email for testing
        subject='🌾 Annual Agricultural Risk Report {{ execution_date.year }}',
        html_content="{{ ti.xcom_pull(key='email_content', task_ids='distribution.prepare_notifications') }}",
        conn_id='gmail_smtp',  # Using your custom connection
        dag=dag,
    )

    [task_upload_cloud, task_update_api] >> task_prepare_email >> task_send_email

# =============================================================================
# FINAL TASK: CLEANUP & ARCHIVAL
# =============================================================================

def archive_and_cleanup(**context):
    """Archive results and cleanup temporary files"""
    import shutil
    import os

    year = get_current_year(**context)
    logger.info(f"🗄️ Archiving data for {year}")

    # Archive to long-term storage
    source_dir = f'/opt/airflow/data/results/{year}'
    archive_dir = f'/opt/airflow/data/historical/{year}'

    if os.path.exists(source_dir):
        os.makedirs(os.path.dirname(archive_dir), exist_ok=True)
        shutil.copytree(source_dir, archive_dir, dirs_exist_ok=True)
        logger.info(f"✅ Archived {year} data to {archive_dir}")

    # Cleanup old temporary files (keep last 3 years)
    # (Implementation details)

    return {'archived': True, 'year': year}

task_archive = PythonOperator(
    task_id='archive_and_cleanup',
    python_callable=archive_and_cleanup,
    dag=dag,
)

# =============================================================================
# INITIAL SENSOR
# =============================================================================

task_wait_for_data = PythonSensor(
    task_id='wait_for_data_availability',
    python_callable=check_data_availability,
    poke_interval=3600,  # Check every hour
    timeout=86400,  # Wait up to 24 hours
    mode='poke',
    dag=dag,
)

# =============================================================================
# DAG FLOW DEFINITION
# =============================================================================

# Wait for data availability
task_wait_for_data >> data_collection_group

# Stage 1 → Stage 2
data_collection_group >> data_processing_group

# Stage 2 → Stage 3
data_processing_group >> sri_calculation_group

# Stage 3 → Stage 4 (parallel report generation)
sri_calculation_group >> report_generation_group

# Stage 4 → Stage 5 (distribution)
report_generation_group >> distribution_group

# Final archival
distribution_group >> task_archive
