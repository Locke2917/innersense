import boto3
import os
import json
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

glue_client = boto3.client("glue")

def lambda_handler(event, context):
    logger.info("🚀 Lambda triggered! Event received: %s", json.dumps(event, indent=2))

    # Extract the uploaded file path from the EventBridge event
    try:
        bucket_name = event["detail"]["bucket"]["name"]
        object_key = event["detail"]["object"]["key"]
    except KeyError:
        logger.error("❌ EventBridge event structure is incorrect!")
        return {"statusCode": 400, "body": "Invalid event format"}

    if not object_key.startswith("raw-data/"):
        logger.info(f"🔕 Skipping file {object_key}, not in raw-data/")
        return {"statusCode": 200, "body": f"Skipped {object_key}, not in raw-data/"}
    
    # Construct input & output paths
    input_path = f"s3://{bucket_name}/{object_key}"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = f"s3://{bucket_name}/processed-data/{timestamp}/"

    logger.info(f"📌 Extracted input_path: {input_path}")
    logger.info(f"📌 Generated output_path: {output_path}")

    job_name = os.getenv("GLUE_JOB_NAME")

    try:
        response = glue_client.start_job_run(
            JobName=job_name,
            Arguments={
                "--input_path": input_path,
                "--output_path": output_path
            }
        )
        logger.info(f"🔥 Glue job started successfully: {response['JobRunId']}")
    except Exception as e:
        logger.error(f"❌ Glue job failed to start: {str(e)}")

    return {
        "statusCode": 200,
        "body": json.dumps(f"Glue job started: {response.get('JobRunId', 'N/A')} with input_path: {input_path} and output_path: {output_path}")
    }
