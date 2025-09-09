resource "random_password" "redshift_password" {
  length = 16
  special = true
}

resource "aws_redshift_cluster" "redshift_cluster" {
  cluster_identifier = "${var.project}-redshift"
  node_type          = "dc2.large"
  cluster_type       = "single-node"
  database_name      = "pipeline_rs"
  master_username    = var.redshift_user
  master_password    = random_password.redshift_password.result
  publicly_accessible = true

  # NOTE: In production, configure VPC and subnets for redshift
  depends_on = [aws_iam_role.redshift_s3_role]
}

# allow redshift to assume role created above - we will use role ARN in COPY
