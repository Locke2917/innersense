#!/bin/bash

# If on windows, open Git Bash application and run

# Set AWS variables
AWS_REGION="us-east-2"
S3_BUCKET="innersense-ingest-default"

# Upload scripts to S3
aws s3 cp etl/app/glue_jobs/process_data.py s3://$S3_BUCKET/glue-scripts/
aws s3 cp etl/app/glue_jobs/transform.py s3://$S3_BUCKET/glue-scripts/
aws s3 cp etl/app/glue_jobs/clean.py s3://$S3_BUCKET/glue-scripts/