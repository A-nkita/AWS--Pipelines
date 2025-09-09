resource "random_password" "rds_password" {
  length           = 16
  override_characters = "_@-"
  special          = true
}

resource "aws_db_instance" "rds_instance" {
  identifier              = "${var.project}-rds"
  engine                  = "postgres"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  name                    = "pipeline_db"
  username                = var.rds_username
  password                = random_password.rds_password.result
  skip_final_snapshot     = true
  publicly_accessible     = true
  port                    = 5432
  backup_retention_period = 0

  tags = {
    Name = "${var.project}-rds"
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "${var.project}-rds-sg"
  description = "Allow postgres inbound (demo only)"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "Postgres from anywhere (DEMO)"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# attach SG to DB (if DB supports)
resource "aws_db_instance" "rds_instance_sg" {
  # NOTE: for certain engines you must supply vpc_security_group_ids; some AWS providers
  # require different args. If your terraform complains, attach the sg via the instance's
  # parameter or modify accordingly.
  depends_on = [aws_db_instance.rds_instance]
}
