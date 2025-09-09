# S3 → Lambda → RDS → Lambda → Redshift Pipeline
A serverless data pipeline that moves data from **S3** to **RDS**, processes it via **Lambda**, and finally loads it into **Redshift** for analytics. This pipeline is designed for efficiency, automation, and scalability.

## 📂 Folder Structure
s3-lambda-rds-lambda-redshift/
├── lambda1_cleaner.py # Cleans and validates raw data from S3
├── lambda2_loader.py # Loads processed data from RDS to Redshift
├── requirements.txt # Python dependencies for Lambda functions
├── README.md # This documentation
└── LICENSE # MIT License

## ⚡ Pipeline Workflow
flowchart TD
    A[S3 Bucket (Raw Data)] --> B[Lambda1: Cleaner]
    B --> C[RDS Database]
    C --> D[Lambda2: Loader]
    D --> E[Redshift Warehouse]

## Workflow Steps:
1. S3 Upload → Lambda1 triggers when a new file is uploaded.
2. Lambda1: Cleaner → Cleans, validates, and transforms raw data.
3. RDS Database → Stores intermediate cleaned data.
4. Lambda2: Loader → Loads data from RDS into Redshift.
5. Redshift Warehouse → Data ready for analytics & reporting.

## Installation & Setup
1. Clone the repository:
   - git clone https://github.com/A-nkita/AWS--Pipelines.git
   - cd AWS--Pipelines/s3-lambda-rds-lambda-redshift
3. Install dependencies:
   - pip install -r requirements.txt
4. Configure AWS credentials:
   - Create an IAM role with S3, RDS, and Redshift access.
   - Set up credentials locally:
   - aws configure

## 🚀 Usage
1. Deploy Lambda functions using AWS CLI or AWS Console.
2. Configure triggers:
   - Lambda1 → S3 Upload
   - Lambda2 → RDS data update
   - Test pipeline with sample S3 files.
   - Monitor logs in CloudWatch for debugging.

## 📝 Example: Lambda1 Cleaner (Python)
      import boto3
      import pandas as pd
      
      s3 = boto3.client('s3')
      
      def lambda_handler(event, context):
          bucket = event['Records'][0]['s3']['bucket']['name']
          key = event['Records'][0]['s3']['object']['key']
          
          obj = s3.get_object(Bucket=bucket, Key=key)
          df = pd.read_csv(obj['Body'])
          
          # Example cleaning
          df.dropna(inplace=True)
          
          # Upload cleaned file to RDS or another S3 bucket
          # ...
          return {"status": "success"}

## 📌 Notes
1. Ensure RDS and Redshift tables exist before Lambda2 runs.
2. Adjust Lambda memory and timeout depending on data size.
3. CloudWatch logging is enabled for troubleshooting.

## 📜 License
This project is licensed under the MIT License
