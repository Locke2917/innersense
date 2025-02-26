# Use an official PySpark image
FROM jupyter/pyspark-notebook:latest

WORKDIR /app

# Copy ETL scripts into the container
COPY app/ ./app/
COPY requirements.txt ./

# Install Python dependencies
RUN pip install -r requirements.txt

# Default command: Run the ETL job
CMD ["spark-submit", "app/jobs/process_data.py"]