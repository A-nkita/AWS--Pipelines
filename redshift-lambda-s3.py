## 🔹 Steps for `Lambda → S3 → Redshift`

1. **Lambda does two things**:

   * Extract/prepare data (could be from RDS, API, etc.).
   * Save it to S3 as a CSV file.

2. **Lambda connects to Redshift** (using `redshift_connector`) and runs:

   COPY schema.table
   FROM 's3://bucket/key.csv'
   IAM_ROLE 'arn:aws:iam::<account-id>:role/<RedshiftCopyRole>'
   FORMAT AS CSV
   IGNOREHEADER 1;

3. **IAM role requirement**:

   * Redshift cluster must have an attached **IAM role** with `AmazonS3ReadOnlyAccess`.
   * The same role ARN is used in the `COPY` command.

---

## 🔹 Lambda Code: Save to S3 + Load to Redshift

import boto3
import pandas as pd
import redshift_connector
import os
import io

def lambda_handler(event, context):
    try:
        # Connect to Redshift using environment variables
        conn = redshift_connector.connect(
            host=os.environ["REDSHIFT_HOST"],
            database=os.environ["REDSHIFT_DB"],
            user=os.environ["REDSHIFT_USER"],
            password=os.environ["REDSHIFT_PASSWORD"],
            port=int(os.environ.get("REDSHIFT_PORT", 5439))
        )

        cursor = conn.cursor()

        # Query data from existing Redshift table
        cursor.execute("SELECT * FROM customers;")  # <-- your table

        # Fetch all rows
        rows = cursor.fetchall()

        # Get column names
        colnames = [desc[0] for desc in cursor.description]

        # Convert to Pandas DataFrame
        df = pd.DataFrame(rows, columns=colnames)

        # Save to CSV in-memory
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        # Upload to S3
        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=os.environ["S3_BUCKET"],
            Key=os.environ["S3_KEY"],
            Body=csv_buffer.getvalue()
        )

        return {
            "statusCode": 200,
            "body": "Data exported from Redshift to S3 successfully"
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }

---

## 🔹 Lambda Environment Variables

* `S3_BUCKET` → your S3 bucket name
* `REDSHIFT_HOST` → `cluster-name.region.redshift.amazonaws.com`
* `REDSHIFT_PORT` → `5439`
* `REDSHIFT_DB` → your Redshift database
* `REDSHIFT_USER` → your Redshift username
* `REDSHIFT_PASSWORD` → your Redshift password
* `REDSHIFT_ROLE_ARN` → IAM Role ARN attached to Redshift cluster

---

⚡ With this setup:

* Data → S3 as CSV
* Redshift `COPY` → fast load into table
