import sys
import boto3
from awsglue.context import GlueContext
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
# hi guys s!

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
logger = glueContext.get_logger()

# Get job arguments
args = getResolvedOptions(sys.argv, ['input_path', 'output_path'])

INPUT_PATH = args['input_path']
OUTPUT_PATH = args['output_path']

print(f"Processing file: {INPUT_PATH}")
print(f"Saving output to: {OUTPUT_PATH}")

def main():
    logger.info("Starting ETL Job")

    # Read data from S3
    df = spark.read.csv(INPUT_PATH, header=True, inferSchema=True)

    # Write output to S3
    df.write.mode("overwrite").parquet(OUTPUT_PATH)

    logger.info(f"ETL Job Completed. Processed data saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
