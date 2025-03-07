import os
import datetime
import requests
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Process JSON Index") \
    .config("spark.jars", "postgresql-42.2.24.jar") \
    .getOrCreate()

# Database connection details
DATABASE_URL = "jdbc:postgresql://localhost/innersense"
DB_PROPERTIES = {
    "user": "postgres",
    "password": "Smartchoice1!",
    "driver": "org.postgresql.Driver"
}

FILES_DIR = "files"
BCBS_IL_ID = 100

os.makedirs(FILES_DIR, exist_ok=True)

def get_payer():
    """Retrieve payer details."""
    query = f"""
        SELECT id, mrf_index_file_url FROM payer WHERE id = {BCBS_IL_ID}
    """
    payer_df = spark.read.jdbc(DATABASE_URL, f"({query}) as payer_data", properties=DB_PROPERTIES)
    return payer_df.collect()[0] if payer_df.count() > 0 else None

def process_fee_schedules(payer_id, index_data):
    fee_schedule_df = index_data.select("id", explode(col("reporting_structure.in_network_files")).alias("file")) \
        .select(col("id").alias("payer_id"), col("file.location").alias("source_file_url"), col("file.description"))
    
    #fee_schedule_df.write.jdbc(DATABASE_URL, "fee_schedule", mode="append", properties=DB_PROPERTIES)
    print(f"✅ Inserted {fee_schedule_df.count()} new fee schedule records.")

def process_plans(payer_id, index_data):
    plans_df = index_data.select("id", explode(col("reporting_structure.reporting_plans")).alias("plan")) \
        .select(col("id").alias("payer_id"), col("plan.plan_name").alias("name"), col("plan.plan_id").alias("category_id"), col("plan.plan_id_type").alias("category_id_type"), col("plan.plan_market_type"))
    
    #plans_df.write.jdbc(DATABASE_URL, "plan", mode="append", properties=DB_PROPERTIES)
    print(f"✅ Inserted {plans_df.count()} new plan records.")

def process_plan_fee_schedule_mappings(payer_id, index_data):
    mappings_df = index_data.select("id", explode(col("reporting_structure")).alias("structure")) \
        .select(col("id").alias("payer_id"), explode(col("structure.reporting_plans")).alias("plan"), explode(col("structure.in_network_files")).alias("file")) \
        .select(col("plan.plan_id").alias("plan_id"), col("file.location").alias("fee_schedule_id"))
    
    #mappings_df.write.jdbc(DATABASE_URL, "plan_fee_schedule", mode="append", properties=DB_PROPERTIES)
    print(f"✅ Inserted {mappings_df.count()} new plan <> fee schedule mapping records.")

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
    index_data = spark.read.json(index_filepath)
    
    index_data.show()
    index_data.printSchema()

    sys.exit()
    # Process data
    print("🔄 Creating fee schedules...")
    process_fee_schedules(payer_id, index_data)

    print("🔄 Creating plan records...")
    process_plans(payer_id, index_data)
    
    print("🔄 Creating plan <> fee schedule mappings...")
    process_plan_fee_schedule_mappings(payer_id, index_data)

    print("✅ Metadata stored successfully.")

if __name__ == "__main__":
    process_json_index()
