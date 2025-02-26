# Create an S3 bucket for ETL scripts & data
resource "aws_s3_bucket" "etl_bucket" {
  bucket = "innersense-ingest-default"

  lifecycle {
    prevent_destroy = true  # Prevents accidental deletion
  }
}

# Create "folders" in S3 by adding empty objects
resource "aws_s3_object" "glue_scripts_folder" {
  bucket = aws_s3_bucket.etl_bucket.id
  key    = "glue-scripts/"  # Folder in S3
}

resource "aws_s3_object" "raw_data_folder" {
  bucket = aws_s3_bucket.etl_bucket.id
  key    = "raw-data/"  # Folder in S3
}

resource "aws_s3_object" "processed_data_folder" {
  bucket = aws_s3_bucket.etl_bucket.id
  key    = "processed-data/"
}

# Create AWS Glue IAM Role
resource "aws_iam_role" "glue_role" {
  name = "AWSGlueETLRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Service = "glue.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

# Attach necessary policies to Glue IAM Role
resource "aws_iam_policy_attachment" "glue_s3_access" {
  name       = "glue_s3_access"
  roles      = [aws_iam_role.glue_role.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# Create AWS Glue Job
resource "aws_glue_job" "etl_job" {
  name     = "MyGlueETLJob"
  role_arn = aws_iam_role.glue_role.arn

  command {
    script_location = "s3://${aws_s3_bucket.etl_bucket.bucket}/glue-scripts/process_data.py"
    python_version  = "3"
  }

  default_arguments = {
    "--TempDir"  = "s3://${aws_s3_bucket.etl_bucket.bucket}/temp/"
    "--job-language" = "python"
  }

  glue_version = "3.0"
  worker_type  = "G.1X"
  number_of_workers = 2
}
