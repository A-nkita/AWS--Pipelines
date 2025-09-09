import os
import boto3
import psycopg2
import psycopg2.extras
import csv
import io
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def connect_rds():
    return psycopg2.connect(
        host=os.environ['RDS_HOST'],
        dbname=os.environ['RDS_DB'],
        user=os.environ['RDS_USER'],
        password=os.environ['RDS_PASS'],
        port=os.environ.get('RDS_PORT', '5432')
    )

def connect_redshift():
    return psycopg2.connect(
        host=os.environ['REDSHIFT_HOST'],
        dbname=os.environ['REDSHIFT_DB'],
        user=os.environ['REDSHIFT_USER'],
        password=os.environ['REDSHIFT_PASS'],
        port=os.environ.get('REDSHIFT_PORT', '5439')
    )

def lambda_handler(event, context):
    logger.info("Starting loader")
    bucket = os.environ['S3_BUCKET']
    clean_table = os.environ.get('CLEAN_TABLE', 'cleaned_data')
    final_table = os.environ.get('FINAL_TABLE', 'final_data')
    s3_key = f"processed/cleaned-{int(time.time())}.csv"

    # 1) extract from RDS
    conn = connect_rds()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM "{clean_table}";')
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]  # includes columns
    cur.close()
    conn.close()

    if not rows:
        logger.info("No rows in %s, nothing to load", clean_table)
        return {"status": "no_rows"}

    # 2) write CSV to memory and upload to S3
    # remove 'id' column if present (we will let redshift create its own)
    if 'id' in cols:
        id_index = cols.index('id')
        cols = [c for c in cols if c != 'id']
        rows = [tuple(v for i,v in enumerate(r) if i != id_index) for r in rows]

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(cols)
    writer.writerows(rows)
    csv_content = csv_buffer.getvalue()
    s3.put_object(Bucket=bucket, Key=s3_key, Body=csv_content.encode('utf-8'))
    logger.info("Uploaded cleaned CSV to s3://%s/%s", bucket, s3_key)

    # 3) Create table in Redshift (all columns as VARCHAR(65535) / or VARCHAR(256) for demo)
    red_conn = connect_redshift()
    red_cur = red_conn.cursor()
    # create if not exists
    col_defs = ", ".join([f'"{c}" VARCHAR(256)' for c in cols])
    create_stmt = f'CREATE TABLE IF NOT EXISTS "{final_table}" ({col_defs});'
    red_cur.execute(create_stmt)
    red_conn.commit()

    # 4) COPY from S3 into Redshift
    s3_path = f"s3://{bucket}/{s3_key}"
    iam_role = os.environ['REDSHIFT_IAM_ROLE']
    copy_sql = f"""
        COPY "{final_table}"
        FROM '{s3_path}'
        IAM_ROLE '{iam_role}'
        CSV
        IGNOREHEADER 1;
    """
    # Important: ensure Redshift cluster role has S3 read permission and the CSV is in same account or accessible
    try:
        red_cur.execute(copy_sql)
        red_conn.commit()
        logger.info("COPY executed into %s", final_table)
    except Exception as e:
        logger.error("COPY failed: %s", e)
        red_conn.rollback()
        raise

    red_cur.close()
    red_conn.close()

    return {"status": "loaded", "s3_path": s3_path, "rows": len(rows)}
