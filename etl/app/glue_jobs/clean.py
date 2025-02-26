from pyspark.sql.functions import col

def clean_data(df):
    """Cleans the data by handling nulls and removing duplicates."""
    # Drop duplicates
    df = df.dropDuplicates()

    # Fill missing values (Example: Replace nulls in 'price' with 0)
    df = df.fillna({"price": 0})

    return df
