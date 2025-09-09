# S3 → Lambda → RDS → Lambda → Redshift Pipeline
This folder contains scripts and configurations for a serverless data pipeline that moves data from **S3** to **RDS**, processes it with **Lambda**, and finally loads it into **Redshift**.

## Project Overview
- **Source**: S3 bucket containing raw data files.
- **Processing**: AWS Lambda functions perform cleaning, transformation, and validation.
- **Intermediate Storage**: Amazon RDS stores processed data.
- **Destination**: Redshift for analytics and reporting.

## Folder Structure
s3-lambda-rds-lambda-redshift/
├── lambda1_cleaner.py # Cleans raw data from S3
├── lambda2_loader.py # Loads data to Redshift
├── requirements.txt # Python dependencies for Lambda functions
├── README.md # Project documentation
└── LICENSE # License for the project

## How to Use
1. **Set up AWS credentials** (IAM roles with S3, RDS, and Redshift access).
2. **Deploy Lambda functions** using AWS Console or AWS CLI.
3. **Configure triggers**:
   - Lambda1 triggers on S3 upload.
   - Lambda2 triggers on RDS update.
4. **Test pipeline** with sample S3 files.
5. **Monitor logs** in CloudWatch.

## Dependencies
pip install -r requirements.txt

**Notes:**
- Ensure RDS and Redshift tables exist before running Lambda2.
- Adjust Lambda memory and timeout based on data size.

---

## ⚡ Pipeline Workflow

```mermaid
flowchart LR
    A[S3 Bucket (Raw Data)] -->|Trigger| B(Lambda1: Cleaner)
    B --> C(RDS Database)
    C -->|Trigger| D(Lambda2: Loader)
    D --> E(Redshift Warehouse)
```
