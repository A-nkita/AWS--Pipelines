import os
import boto3
import pandas as pd
import io
import psycopg2
import psycopg2.extras
import re
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

def sanitize_col(col):
    col = col.strip()
    col = col.lower()
    col = re.sub(r"[^a-z0-9_]+", "_", col)
    col = re.sub(r"_+", "_", col)
    col = col.strip("_")
    if not col:
        col = "col"
    return col

def connect_rds():
    return psycopg2.connect(
        host=os.environ['RDS_HOST'],
        dbname=os.environ['RDS_DB'],
        user=os.environ['RDS_USER'],
        password=os.environ['RDS_PASS'],
        port=os.environ.get('RDS_PORT', '5432')
    )

def lambda_handler(event, context):
    logger.info("Event: %s", event)
    try:
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
    except Exception as e:
        logger.error("No S3 record in event: %s", e)
        raise

    # download file
    tmp_key = key.split("/")[-1]
    tmp_path = f"/tmp/{tmp_key}"
    s3.download_file(bucket, key, tmp_path)
    logger.info("Downloaded %s to %s", key, tmp_path)

    # read CSV (robust)
    try:
        df = pd.read_csv(tmp_path)
    except Exception as e:
        logger.error("Error reading CSV: %s", e)
        raise

    # sanitize columns
    original_cols = df.columns.tolist()
    sanitized = [sanitize_col(c) for c in original_cols]
    df.columns = sanitized
    logger.info("Sanitized columns: %s", sanitized)

    # strip whitespace in string columns
    for c in df.select_dtypes(include=['object']).columns:
        df[c] = df[c].astype(str).str.strip()
        # convert 'nan' strings back to actual NaN
        df[c] = df[c].replace({'nan': pd.NA, 'None': pd.NA, '': pd.NA})

    # drop rows with any nulls (strict)
    before = len(df)
    df = df.dropna(how='any')
    after_dropna = len(df)
    logger.info("Dropped rows with nulls: %s -> %s", before, after_dropna)

    # drop full duplicates
    df = df.drop_duplicates()
    after_dedup = len(df)
    logger.info("Dropped duplicates: %s -> %s", after_dropna, after_dedup)

    if df.empty:
        logger.info("No data after cleaning. Exiting.")
        return {"status": "empty_after_clean"}

    # Write to RDS (dynamic schema with TEXT columns)
    table = os.environ.get("CLEAN_TABLE", "cleaned_data")

    conn = connect_rds()
    cur = conn.cursor()

    # Build CREATE TABLE with id serial and dynamic columns
    col_defs = ", ".join([f'"{c}" TEXT' for c in df.columns])
    create_stmt = f'''
        CREATE TABLE IF NOT EXISTS "{table}" (
            id SERIAL PRIMARY KEY,
            {col_defs}
        );
    '''
    cur.execute(create_stmt)
    conn.commit()
    logger.info("Ensured table %s exists", table)

    # Insert data using psycopg2.extras.execute_values for speed
    cols_sql = ", ".join([f'"{c}"' for c in df.columns])
    values = [tuple(row) for row in df.itertuples(index=False, name=None)]
    insert_sql = f'INSERT INTO "{table}" ({cols_sql}) VALUES %s'

    psycopg2.extras.execute_values(cur, insert_sql, values, template=None, page_size=1000)
    conn.commit()

    cur.close()
    conn.close()

    logger.info("Inserted %s rows into %s", len(values), table)

    return {"status": "ok", "rows_inserted": len(values)}
