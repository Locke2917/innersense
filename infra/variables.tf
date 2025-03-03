variable "aws_region" {
  default = "us-east-2"
}

variable "glue_job_name" {
  default = "MyGlueETLJob"
}

variable "s3_bucket_name" {
  description = "The name of the S3 bucket used for AWS Glue"
  default     = "innersense-ingest-default"  # Change as needed
}
