"""
Cloud Uploader - Production Module

Uploads generated reports and data to AWS S3 for cloud storage.
"""

import boto3
import os
import logging
from typing import Dict, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def upload_file_to_s3(
    file_path: str,
    bucket_name: str,
    s3_key: str,
    aws_access_key: str = None,
    aws_secret_key: str = None,
    make_public: bool = True
) -> bool:
    """
    Upload a single file to S3

    Args:
        file_path: Local file path to upload
        bucket_name: S3 bucket name
        s3_key: S3 object key (path in bucket)
        aws_access_key: AWS access key (defaults to env variable)
        aws_secret_key: AWS secret key (defaults to env variable)
        make_public: Whether to make file publicly accessible

    Returns:
        bool indicating success
    """
    # Get AWS credentials
    if not aws_access_key:
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    if not aws_secret_key:
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )

        # Determine content type
        content_type = 'text/html' if file_path.endswith('.html') else \
                       'text/csv' if file_path.endswith('.csv') else \
                       'image/png' if file_path.endswith('.png') else \
                       'application/octet-stream'

        # Upload file
        extra_args = {
            'ContentType': content_type
        }

        if make_public:
            extra_args['ACL'] = 'public-read'

        s3_client.upload_file(
            file_path,
            bucket_name,
            s3_key,
            ExtraArgs=extra_args
        )

        return True

    except ClientError as e:
        logger.error(f"  ❌ S3 upload error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"  ❌ Upload error: {str(e)}")
        return False


def upload_reports_to_s3(
    report_dir: str,
    year: int,
    bucket_name: str = None,
    aws_access_key: str = None,
    aws_secret_key: str = None
) -> Dict:
    """
    Upload all reports to S3

    Args:
        report_dir: Local directory containing reports
        year: Year of the reports
        bucket_name: S3 bucket name (defaults to env variable)
        aws_access_key: AWS access key (defaults to env variable)
        aws_secret_key: AWS secret key (defaults to env variable)

    Returns:
        dict with upload results
    """
    logger.info("☁️  Uploading reports to S3...")

    # Get bucket name
    if not bucket_name:
        bucket_name = os.getenv('S3_BUCKET_NAME', 'agricultural-risk-reports')

    # Check if AWS credentials are available
    if not aws_access_key:
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    if not aws_secret_key:
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    if not aws_access_key or not aws_secret_key:
        logger.warning("⚠️ AWS credentials not found, skipping S3 upload")
        return {
            'success': False,
            'uploaded_files': 0,
            'error': 'AWS credentials not configured'
        }

    uploaded_files = []
    failed_files = []

    try:
        # Collect files to upload
        files_to_upload = []

        # Market summary HTML
        market_summary = os.path.join(report_dir, f'market_summary_{year}.html')
        if os.path.exists(market_summary):
            files_to_upload.append((market_summary, f'reports/{year}/market_summary.html'))

        # State reports
        states_dir = os.path.join(report_dir, 'states')
        if os.path.exists(states_dir):
            for filename in os.listdir(states_dir):
                if filename.endswith('.csv'):
                    local_path = os.path.join(states_dir, filename)
                    s3_key = f'reports/{year}/states/{filename}'
                    files_to_upload.append((local_path, s3_key))

        # Visualizations
        viz_dir = os.path.join(report_dir, 'visualizations')
        if os.path.exists(viz_dir):
            for filename in os.listdir(viz_dir):
                if filename.endswith('.png'):
                    local_path = os.path.join(viz_dir, filename)
                    s3_key = f'reports/{year}/visualizations/{filename}'
                    files_to_upload.append((local_path, s3_key))

        # Upload each file
        logger.info(f"  Uploading {len(files_to_upload)} files to s3://{bucket_name}/")

        for local_path, s3_key in files_to_upload:
            logger.info(f"    Uploading {os.path.basename(local_path)}...")

            success = upload_file_to_s3(
                file_path=local_path,
                bucket_name=bucket_name,
                s3_key=s3_key,
                aws_access_key=aws_access_key,
                aws_secret_key=aws_secret_key,
                make_public=True
            )

            if success:
                uploaded_files.append(s3_key)
                logger.info(f"      ✓ Uploaded to s3://{bucket_name}/{s3_key}")
            else:
                failed_files.append(local_path)

        logger.info(f"✅ Uploaded {len(uploaded_files)} files to S3")

        if failed_files:
            logger.warning(f"  ⚠️ Failed to upload {len(failed_files)} files")

        return {
            'success': True,
            'bucket': bucket_name,
            'uploaded_files': len(uploaded_files),
            'failed_files': len(failed_files),
            's3_keys': uploaded_files,
            'base_url': f'https://{bucket_name}.s3.amazonaws.com/reports/{year}/'
        }

    except Exception as e:
        logger.error(f"❌ Error uploading to S3: {str(e)}")
        return {
            'success': False,
            'uploaded_files': 0,
            'error': str(e)
        }


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) != 2:
        print("Usage: python cloud_uploader.py <report_dir>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    result = upload_reports_to_s3(
        report_dir=sys.argv[1],
        year=2024
    )
    print(f"\nUpload Result: {result}")
