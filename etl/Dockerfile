FROM apache/spark:latest

# Set environment variables
ENV PYSPARK_PYTHON=python3
ENV SPARK_HOME=/opt/spark

# Set the working directory inside the container
WORKDIR /opt/workdir

# Install dependencies
COPY requirements.txt .
USER root
RUN pip3 install --no-cache-dir -r requirements.txt

# Ensure /opt/workdir/glue_jobs exists and download the PostgreSQL JDBC driver
RUN mkdir -p /opt/workdir/glue_jobs && \
curl -o /opt/workdir/glue_jobs/postgresql-42.2.24.jar \
https://jdbc.postgresql.org/download/postgresql-42.7.5.jar

# Copy app files
COPY . .

# Set the container to run PySpark by default
CMD ["/opt/spark/bin/pyspark"]

#docker run -it --rm -v //c/users/clock/development/innersense/etl/app:/opt/workdir innersense-spark /bin/bash

#docker run -it --rm --mount src="$(pwd)",target=/opt/workdir,type=bind innersense-spark /bin/bash