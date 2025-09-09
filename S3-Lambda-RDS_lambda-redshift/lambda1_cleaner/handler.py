import json
import boto3
import psycopg2
import csv
import io
import os

# RDS connection details (pseudo names, replace later if needed)
RDS_HOST = os.getenv("RDS_HOST", "demo-rds-instance.cluster-123456789012.ap-south-1.rds.amazonaws.com")
RDS_PORT = int(os.getenv("RDS_PORT", "5432"))
RDS_DB   = os.getenv("RDS_DB", "demo_db")
RDS_USER = os.getenv("RDS_USER", "demo_user")
RDS_PASS = os.getenv("RDS_PASS", "demo_password")

def lambda_handler(event, context):
    try:
        # --- 1. Get bucket + key from S3 event ---
        s3 = boto3.client('s3')
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        print(f"Processing file: s3://{bucket}/{key}")

        # --- 2. Read CSV from S3 ---
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))

        cleaned_rows = []

        for row in csv_reader:
            customer_id = row['customer id'].strip() if row['customer id'] else None
            customer_name = row['Customer Name'].strip() if row['Customer Name'] else None
            amount = row['amount'].strip() if row['amount'] else None
            notes = row['notes'].strip() if row['notes'] else None

            # Skip rows with missing critical fields
            if not customer_id or not customer_name or not amount:
                continue

            cleaned_rows.append((customer_id, customer_name, amount, notes))

        # --- 3. Remove duplicates ---
        unique_rows = list(set(cleaned_rows))

        # --- 4. Insert into RDS staging_table ---
        conn = psycopg2.connect(
            host=RDS_HOST,
            port=RDS_PORT,
            dbname=RDS_DB,
            user=RDS_USER,
            password=RDS_PASS
        )
        cur = conn.cursor()

        insert_query = """
            INSERT INTO staging_table (customer_id, customer_name, amount, notes)
            VALUES (%s, %s, %s, %s);
        """

        for row in unique_rows:
            cur.execute(insert_query, row)

        conn.commit()
        cur.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps(f"Inserted {len(unique_rows)} unique rows into staging_table")
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing file: {str(e)}")
        }
