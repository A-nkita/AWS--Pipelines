output "s3_bucket" {
  value = aws_s3_bucket.raw_data_bucket.bucket
}
output "rds_endpoint" {
  value = aws_db_instance.rds_instance.address
}
output "redshift_endpoint" {
  value = aws_redshift_cluster.redshift_cluster.endpoint
}
output "redshift_role_arn" {
  value = aws_iam_role.redshift_s3_role.arn
}
output "lambda_cleaner" {
  value = aws_lambda_function.cleaner.function_name
}
output "lambda_loader" {
  value = aws_lambda_function.loader.function_name
}
