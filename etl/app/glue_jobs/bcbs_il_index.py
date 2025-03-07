import os
import datetime
import requests
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, lit, sha2, concat_ws, posexplode, explode_outer

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Process JSON Index") \
    .config("spark.jars", "postgresql-42.2.24.jar") \
    .getOrCreate()

# Database connection details
DATABASE_URL = "jdbc:postgresql://localhost/innersense_3"
DATABASE_URL = "jdbc:postgresql://host.docker.internal/innersense_3"
DB_PROPERTIES = {
    "user": "postgres",
    "password": "Smartchoice1!",
    "driver": "org.postgresql.Driver"
}

FILES_DIR = "files"
BCBS_IL_ID = 100
MODE = "append"
"""
Mode	Behavior	SQL Equivalent
"append"	✅ Adds new rows without deleting existing ones.	INSERT INTO ...
"overwrite"	❌ Replaces the table completely before writing new data.	DROP TABLE fee_schedules; CREATE TABLE fee_schedules ...
"ignore"	✅ Skips insert if the table already exists.	(Does nothing if table exists)
"error" (default)	❌ Throws an error if the table exists.	(No changes made)
"""
os.makedirs(FILES_DIR, exist_ok=True)

def get_payer():
    """Retrieve payer details."""
    query = f"""
        SELECT id, mrf_index_file_url FROM payers WHERE id = {BCBS_IL_ID}
    """
    payer_df = spark.read.jdbc(DATABASE_URL, f"({query}) as payer_data", properties=DB_PROPERTIES)
    return payer_df.collect()[0] if payer_df.count() > 0 else None

def process_fee_schedules(payer_id, index_data): 
    print("🔄 Creating fee schedules...")

    fee_schedule_df = index_data \
        .withColumn("reporting_structure", explode(col("reporting_structure"))) \
        .withColumn("file", explode(col("reporting_structure.in_network_files"))) \
        .select(
            sha2(concat_ws("_", lit(payer_id), col("file.description"),  col("file.location")), 256).alias("id"),
            lit(payer_id).alias("payer_id"),
            col("file.location").alias("source_file_url"),
            col("file.description")
        ) \
        .distinct()
    
    fee_schedule_df.write.jdbc(DATABASE_URL, "fee_schedules", mode=MODE, properties=DB_PROPERTIES)
    print(f"✅ Inserted {fee_schedule_df.count()} new fee schedule records.")

def process_plans(payer_id, index_data): 
    print("🔄 Creating plans...")
    
    plans_df = index_data \
        .withColumn("reporting_structure", explode(col("reporting_structure"))) \
        .withColumn("plan", explode(col("reporting_structure.reporting_plans"))) \
        .select(
            sha2(concat_ws("_", lit(payer_id), col("plan.plan_name")), 256).alias("id"),
            lit(payer_id).alias("payer_id"),
            col("plan.plan_name").alias("name"),
            col("plan.plan_id").alias("category_id"),
            col("plan.plan_id_type").alias("category_id_type"),
            col("plan.plan_market_type")
        ).distinct()
    
    plans_df.write.jdbc(DATABASE_URL, "plans", mode=MODE, properties=DB_PROPERTIES)
    print(f"✅ Inserted {plans_df.count()} new plan records.")

def process_plan_fee_schedule_mappings(payer_id, index_data):
    print("🔄 Creating plan <> fee schedule mappings...")

    mappings_df = index_data \
        .withColumn("reporting_structure", explode(col("reporting_structure"))) \
        .withColumn("plan", explode(col("reporting_structure.reporting_plans"))) \
        .withColumn("file", explode(col("reporting_structure.in_network_files"))) \
        .select(
            sha2(concat_ws("_", lit(payer_id), col("plan.plan_name")), 256).alias("plan_id"),
            sha2(concat_ws("_", lit(payer_id), col("file.description"),  col("file.location")), 256).alias("fee_schedule_id")
    ).distinct()

    print(mappings_df.count())

    mappings_df.write.jdbc(DATABASE_URL, "plan_fee_schedules", mode=MODE, properties=DB_PROPERTIES)
    print(f"✅ Inserted {mappings_df.count()} new plan <> fee  records.")


def process_json_index():

    payer = get_payer()
    if not payer:
        print("❌ Payer not found.")
        return

    payer_id = payer.id
    payer_index_file_url = payer.mrf_index_file_url
    index_filepath = os.path.join(FILES_DIR, f"BCBS_IL_Index_{datetime.datetime.now().strftime('%m-%d-%Y')}.json")

    # Download JSON file
    response = requests.get(payer_index_file_url, stream=True)
    with open(index_filepath, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    # Load JSON directly into a DataFrame
    index_data = spark.read.json(os.path.join(FILES_DIR, "test_index.json"))
    index_data = spark.read.json(index_filepath)
    """
    root
    |-- reporting_entity_name: string (nullable = true)
    |-- reporting_entity_type: string (nullable = true)
    |-- reporting_structure: array (nullable = true)
    |    |-- element: struct (containsNull = true)
    |    |    |-- allowed_amount_file: array (nullable = true)
    |    |    |    |-- element: struct (containsNull = true)
    |    |    |    |    |-- description: string (nullable = true)
    |    |    |    |    |-- location: string (nullable = true)
    |    |    |-- in_network_files: array (nullable = true)
    |    |    |    |-- element: struct (containsNull = true)
    |    |    |    |    |-- description: string (nullable = true)
    |    |    |    |    |-- location: string (nullable = true)
    |    |    |-- reporting_plans: array (nullable = true)
    |    |    |    |-- element: struct (containsNull = true)
    |    |    |    |    |-- plan_id: string (nullable = true)
    |    |    |    |    |-- plan_id_type: string (nullable = true)
    |    |    |    |    |-- plan_market_type: string (nullable = true)
    |    |    |    |    |-- plan_name: string (nullable = true)
    """
    process_fee_schedules(payer_id, index_data)

    process_plans(payer_id, index_data)
    
    process_plan_fee_schedule_mappings(payer_id, index_data)

    print("✅ Index parsed successfully")

if __name__ == "__main__":

    process_json_index()
