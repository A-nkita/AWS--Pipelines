Lambda file using environment variables added to lambda configuration/ os and pandas-
go to configiration and keey and values in enviornment variables as-

DB_NAME- AWS_Study
DB_PASSWORD- 9623769118
DB_USER- admin
RDS_HOST- database-2.cf0qse4o8mlh.ap-south-1.rds.amazonaws.com
S3_BUCKET- pedya-input
S3_KEY- data-test/customers.csv
-----------------------------------------------
import boto3
import os
import sys, subprocess
import io

# Install pymysql in Lambda /tmp/ at runtime (only pymysql, since pandas is in layer)
subprocess.call(
    'pip install pymysql -t /tmp/ --no-cache-dir'.split(),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
sys.path.insert(1, '/tmp/')

import pymysql
import pandas as pd

# Read configuration from Lambda environment variables
rds_host = os.environ["RDS_HOST"]
db_username = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_NAME"]

s3_bucket = os.environ["S3_BUCKET"]
s3_key = os.environ["S3_KEY"]

def lambda_handler(event, context):
    try:
        # Connect to RDS MySQL
        conn = pymysql.connect(
            host=rds_host,
            user=db_username,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()

        # Execute SQL query to retrieve all data
        cursor.execute("SELECT * FROM Customers")
        result = cursor.fetchall()

        # Auto-detect column names from DB
        columns = [desc[0] for desc in cursor.description]

        # Load into pandas DataFrame
        df = pd.DataFrame(result, columns=columns)

        # Convert to CSV (in-memory)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        # Upload data to S3
        s3 = boto3.client('s3')
        s3.put_object(Body=csv_buffer.getvalue(), Bucket=s3_bucket, Key=s3_key)

        # Close RDS connection
        cursor.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': f'Data uploaded to S3 as CSV successfully: {s3_key}'
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }


--------------------------------------------------------------------------------------------------------------------------
Lambda file raw-

import boto3
import sys, subprocess

# Install pymysql in Lambda /tmp/ at runtime
subprocess.call(
    'pip install pymysql -t /tmp/ --no-cache-dir'.split(),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
sys.path.insert(1, '/tmp/')

import pymysql

# RDS configuration
rds_host = "database-2.cf0qse4o8mlh.ap-south-1.rds.amazonaws.com"
db_username = "admin"
db_password = "9623769118"
db_name = "AWS_Study"

# S3 configuration
s3_bucket = "pedya-input"
s3_key = "data/categories.csv"

def lambda_handler(event, context):
    try:
        # Connect to RDS MySQL
        conn = pymysql.connect(
            host=rds_host,
            user=db_username,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()

        # Execute SQL query to retrieve all data
        cursor.execute("SELECT * FROM Categories")
        result = cursor.fetchall()

        # Close RDS connection
        cursor.close()
        conn.close()

        # Debug log
        for row in result:
            print(row)

        # Upload data to S3
        s3 = boto3.client('s3')
        s3.put_object(Body=str(result), Bucket=s3_bucket, Key=s3_key)

        return {
            'statusCode': 200,
            'body': 'Data uploaded to S3 successfully.'
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }

--------------------------------------------------------------------------------------------------------------------------
Lambda file using config.json-
config.json file-
{
  "rds_config": {
    "rds_host": "database-2.cf0qse4o8mlh.ap-south-1.rds.amazonaws.com",
    "db_username": "admin",
    "db_password": "9623769118",
    "db_name": "AWS_Study"
  },
  "s3_config": {
    "bucket": "pedya-input",
    "key": "data/categories.csv"
  }
}
------------------------------------------------------------------

import boto3
import sys, subprocess, json

# Install pymysql in /tmp
subprocess.call(
    'pip install pymysql -t /tmp/ --no-cache-dir'.split(),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
sys.path.insert(1, '/tmp/')

import pymysql

# Load configuration from JSON file (config.json should be in Lambda layer or S3)
def load_config():
    # If config.json is packaged with the Lambda
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()

# Extract RDS and S3 config
rds_host = config["rds_config"]["rds_host"]
db_username = config["rds_config"]["db_username"]
db_password = config["rds_config"]["db_password"]
db_name = config["rds_config"]["db_name"]

s3_bucket = config["s3_config"]["bucket"]
s3_key = config["s3_config"]["key"]

def lambda_handler(event, context):
    try:
        # Connect to RDS MySQL
        conn = pymysql.connect(
            host=rds_host,
            user=db_username,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()

        # Execute SQL query to retrieve all data
        cursor.execute("SELECT * FROM Categories")
        result = cursor.fetchall()

        # Close RDS connection
        cursor.close()
        conn.close()

        # Upload data to S3
        s3 = boto3.client('s3')
        s3.put_object(Body=str(result), Bucket=s3_bucket, Key=s3_key)

        return {
            'statusCode': 200,
            'body': f'Data uploaded to S3 bucket {s3_bucket} at {s3_key}.'
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }


--------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------


Steps Required

Create RDS MySQL Instance

Launch an RDS MySQL database in AWS (done by you ✅).

Ensure security group allows inbound traffic from Lambda’s VPC (port 3306).

Create a database and tables (e.g., Customers).

Prepare IAM Role for Lambda

Attach policies to Lambda’s execution role:

AmazonRDSFullAccess (or custom with RDS connect perms).

AmazonS3FullAccess (to upload result to S3).

Deploy Lambda Function

Use Python runtime (≥ 3.9).

Install PyMySQL inside Lambda (since Lambda doesn’t have it by default).

That’s why you used subprocess.call('pip install pymysql -t /tmp/').

Write Lambda handler to:

Connect to RDS.

Run SQL query.

Fetch results.

Upload results to S3.

Test Lambda

Manually invoke Lambda from AWS Console.

Ensure logs in CloudWatch show fetched data.

Check S3 bucket for uploaded file.
