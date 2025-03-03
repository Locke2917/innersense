

# Create S3 bucket
resource "aws_s3_bucket" "etl_bucket" {
  bucket = var.s3_bucket_name

  lifecycle {
    prevent_destroy = true
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

# Enable direct EventBridge notifications from S3
resource "aws_s3_bucket_notification" "s3_eventbridge_integration" {
  bucket      = aws_s3_bucket.etl_bucket.id
  eventbridge = true
}

# EventBridge rule listens for S3 uploads
resource "aws_cloudwatch_event_rule" "s3_trigger_glue" {
  name        = "TriggerGlueOnRawDataUpload"
  description = "Runs ETL when a file is uploaded to S3"

  event_pattern = jsonencode({
    source      = ["aws.s3"],
    detail-type = ["Object Created"],
    detail      = {
      bucket = { name = [aws_s3_bucket.etl_bucket.id] }
    }
  })
}

# EventBridge target: Call Lambda
resource "aws_cloudwatch_event_target" "glue_lambda_target" {
  rule      = aws_cloudwatch_event_rule.s3_trigger_glue.name
  arn       = aws_lambda_function.trigger_glue_lambda.arn
  role_arn  = aws_iam_role.eventbridge_role.arn  # This is the missing piece!
}

# Lambda function to trigger Glue
resource "aws_lambda_function" "trigger_glue_lambda" {
  function_name    = "TriggerGlueJob"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"
  timeout          = 30

  filename         = "lambda.zip"
  source_code_hash = filebase64sha256("lambda.zip")

  environment {
    variables = {
      GLUE_JOB_NAME = aws_glue_job.etl_job.name
      BUCKET_NAME   = aws_s3_bucket.etl_bucket.id
    }
  }
}

# Glue ETL job
resource "aws_glue_job" "etl_job" {
  name     = "MyGlueETLJob"
  role_arn = aws_iam_role.glue_role.arn

  command {
    script_location = "s3://${aws_s3_bucket.etl_bucket.id}/glue-scripts/process_data.py"
    python_version  = "3"
  }

  #default_arguments = {
    # "--extra-py-files" = "s3://${aws_s3_bucket.etl_bucket.id}/glue-scripts/glue_libs.zip"
    # "--input_path"     = "s3://${aws_s3_bucket.etl_bucket.id}/raw-data/"
  #}

  glue_version = "5.0"
  worker_type  = "G.1X"
  number_of_workers = 2
}

# IAM for Lambda to start Glue
resource "aws_iam_role" "lambda_role" {
  name = "LambdaTriggerGlueRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = { Service = "lambda.amazonaws.com" },
        Action    = "sts:AssumeRole"
      },
      {
        Effect    = "Allow",
        Principal = { Service = "events.amazonaws.com" },
        Action    = "sts:AssumeRole"
      }
    ]
  })
}


resource "aws_iam_policy_attachment" "lambda_glue_access" {
  name       = "lambda_glue_access"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# IAM for EventBridge to invoke Lambda
resource "aws_iam_role" "eventbridge_role" {
  name = "EventBridgeExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "events.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trigger_glue_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.s3_trigger_glue.arn
}


resource "aws_iam_policy" "eventbridge_lambda_policy" {
  name        = "EventBridgeLambdaPolicy"
  description = "Allows EventBridge to invoke Lambda"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect   = "Allow",
      Action   = ["lambda:InvokeFunction"],
      Resource = aws_lambda_function.trigger_glue_lambda.arn
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eventbridge_lambda_access" {
  policy_arn = aws_iam_policy.eventbridge_lambda_policy.arn
  role       = aws_iam_role.eventbridge_role.name
}


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

resource "aws_iam_policy" "lambda_s3_write_policy" {
  name        = "LambdaS3WritePolicy"
  description = "Allows Lambda to write marker files to S3"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect   = "Allow",
      Action   = ["s3:PutObject"],
      Resource = "arn:aws:s3:::${aws_s3_bucket.etl_bucket.id}/lambda-triggered/*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_write_access" {
  policy_arn = aws_iam_policy.lambda_s3_write_policy.arn
  role       = aws_iam_role.lambda_role.name
}

resource "aws_iam_role_policy_attachment" "lambda_cloudwatch_logs" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
  role       = aws_iam_role.lambda_role.name
}