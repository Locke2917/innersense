import boto3
import os
import json
from datetime import datetime

# AWS Clients
s3_client = boto3.client("s3")
glue_client = boto3.client("glue")

# Get environment variables
bucket_name = os.getenv("BUCKET_NAME")  # Set this in Terraform
glue_job_name = os.getenv("GLUE_JOB_NAME")

def lambda_handler(event, context):
    # Log event received
    print("🚀 Lambda triggered!! Event received:", json.dumps(event, indent=2))

    # Write a marker file to S3
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    marker_file_key = f"lambda-triggered/lambda_triggered_{timestamp}.txt"
    

    s3_client.put_object(
        Bucket=bucket_name,
        Key=marker_file_key,
        Body=f"Lambda was triggered at {timestamp} UTC\nEvent: {json.dumps(event, indent=2)}"
    )

    print(f"📌 Marker file written to s3://{bucket_name}/{marker_file_key}")

    # Start Glue job
    response = glue_client.start_job_run(JobName=glue_job_name)
    print(f"🔥 Glue job started: {response['JobRunId']}")

    return {
        "statusCode": 200,
        "body": json.dumps(f"Glue job started: {response['JobRunId']}, Marker file: {marker_file_key}")
    }
