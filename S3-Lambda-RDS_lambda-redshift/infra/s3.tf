resource "aws_s3_bucket" "raw_data_bucket" {
  bucket = var.s3_bucket
  acl    = "private"

  tags = {
    Name = "${var.project}-raw-bucket"
    Env  = "dev"
  }

  # Versioning is helpful for debugging
  versioning {
    enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "block" {
  bucket = aws_s3_bucket.raw_data_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
