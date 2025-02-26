import sys
import boto3
from awsglue.context import GlueContext
from awsglue.transforms import *
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from transform import transform_data
from clean import clean_data
# hi guys s

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
logger = glueContext.get_logger()

# S3 Paths (Replace with actual S3 bucket)
INPUT_PATH = "s3://your-bucket/raw-data/input.csv"
OUTPUT_PATH = "s3://your-bucket/processed-data/"

def main():
    logger.info("Starting ETL Job")

    # Read data from S3
    df = spark.read.csv(INPUT_PATH, header=True, inferSchema=True)

    # Clean the data
    df_cleaned = clean_data(df)

    # Transform the data
    df_transformed = transform_data(df_cleaned)

    # Write output to S3
    df_transformed.write.mode("overwrite").parquet(OUTPUT_PATH)

    logger.info(f"ETL Job Completed. Processed data saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
