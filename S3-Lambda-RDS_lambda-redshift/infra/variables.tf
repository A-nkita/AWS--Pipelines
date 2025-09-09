variable "region" {
  type    = string
  default = "us-east-1"
}

variable "project" {
  type    = string
  default = "ankita-pipeline"
}

variable "s3_bucket" {
  description = "Name of S3 bucket for raw & processed data"
  type = string
  default = "ankita-pipeline-raw-data-2025"
}

# Redshift
variable "redshift_user" {
  type = string
  default = "redshift_user"
}

# RDS
variable "rds_username" { type = string; default = "pipeline_admin" }
