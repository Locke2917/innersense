import boto3
import os
import json

glue_client = boto3.client("glue")

def lambda_handler(event, context):
    job_name = os.getenv("GLUE_JOB_NAME")
    response = glue_client.start_job_run(JobName=job_name)
    return {
        "statusCode": 200,
        "body": json.dumps(f"Started Glue job: {response['JobRunId']}")
    }