from pyspark.sql.functions import col

def transform_data(df):
    """Applies transformations to the DataFrame."""
    # Example: Rename columns
    df = df.withColumnRenamed("old_column_name", "new_column_name")

    # Example: Convert data types
    df = df.withColumn("amount", col("amount").cast("double"))

    return df
