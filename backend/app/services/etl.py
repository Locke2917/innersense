import boto3

glue_client = boto3.client("glue", region_name="us-east-1")

def start_etl_job(job_name: str):
    response = glue_client.start_job_run(JobName=job_name)
    return response["JobRunId"]
