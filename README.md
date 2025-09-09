# AWS Pipelines 🚀

A collection of end-to-end AWS data engineering pipelines and demo projects.  
This repository contains multiple projects showing how to integrate **S3, Lambda, RDS, and Redshift** with data cleaning and transformation.

---

## 📂 Projects

### 1. [s3-rds-redshift-pipeline](./s3-rds-redshift-pipeline)
> Full pipeline: **S3 → Lambda (Cleaner) → RDS → Lambda (Loader) → Redshift**

- Handles raw CSV uploads into S3  
- Cleans nulls & duplicates via Lambda  
- Loads cleaned data into RDS staging table  
- Moves data from RDS to Redshift using another Lambda  
- Orchestrated with AWS Step Functions  

### 2. Other Scripts
- `read_RDS_dump_s3.py` → dumps RDS tables into S3  
- `redshift-lambda-s3.py` → Lambda script for Redshift access  
- `S3-S3-migration.py` → migrate data between buckets  

---

## 🛠️ Tech Stack
- **AWS S3** – raw data storage  
- **AWS Lambda** – serverless cleaning + loading  
- **Amazon RDS (Postgres)** – staging database  
- **Amazon Redshift** – data warehouse  
- **Terraform** – infra as code  
- **Step Functions** – orchestration  

---

## 📌 How to Use
1. Clone repo  
   ```bash
   git clone https://github.com/A-nkita/AWS--Pipelines.git
   cd AWS--Pipelines
