# Lambda 1 - Cleaner
resource "aws_lambda_function" "cleaner" {
  filename         = "${path.root}/lambda_packages/lambda1.zip" # created by packaging script
  function_name    = "${var.project}-lambda-cleaner"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "app.lambda_handler"
  runtime          = "python3.10"
  timeout          = 60

  environment {
    variables = {
      RDS_HOST = aws_db_instance.rds_instance.address
      RDS_PORT = aws_db_instance.rds_instance.port
      RDS_DB   = aws_db_instance.rds_instance.name
      RDS_USER = var.rds_username
      RDS_PASS = random_password.rds_password.result
      S3_BUCKET = aws_s3_bucket.raw_data_bucket.bucket
      CLEAN_TABLE = "cleaned_data"
    }
  }
}

# Lambda 2 - Loader
resource "aws_lambda_function" "loader" {
  filename         = "${path.root}/lambda_packages/lambda2.zip"
  function_name    = "${var.project}-lambda-loader"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "app.lambda_handler"
  runtime          = "python3.10"
  timeout          = 300

  environment {
    variables = {
      RDS_HOST = aws_db_instance.rds_instance.address
      RDS_PORT = aws_db_instance.rds_instance.port
      RDS_DB   = aws_db_instance.rds_instance.name
      RDS_USER = var.rds_username
      RDS_PASS = random_password.rds_password.result

      S3_BUCKET = aws_s3_bucket.raw_data_bucket.bucket

      REDSHIFT_HOST = aws_redshift_cluster.redshift_cluster.endpoint
      REDSHIFT_PORT = aws_redshift_cluster.redshift_cluster.port
      REDSHIFT_DB   = aws_redshift_cluster.redshift_cluster.database_name
      REDSHIFT_USER = var.redshift_user
      REDSHIFT_PASS = random_password.redshift_password.result
      REDSHIFT_IAM_ROLE = aws_iam_role.redshift_s3_role.arn
      FINAL_TABLE = "final_data"
      CLEAN_TABLE = "cleaned_data"
    }
  }
}
