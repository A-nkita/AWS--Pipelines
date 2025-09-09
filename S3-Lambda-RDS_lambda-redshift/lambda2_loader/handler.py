import psycopg2
import os

def lambda_handler(event, context):
    try:
        # --- Connect to RDS ---
        rds_conn = psycopg2.connect(
            host=os.environ['RDS_HOST'],
            dbname=os.environ['RDS_DB'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASS'],
            port=5432
        )
        rds_cur = rds_conn.cursor()

        # Fetch data from RDS staging_table
        rds_cur.execute("SELECT customer_id, customer_name, amount, notes FROM staging_table;")
        rows = rds_cur.fetchall()

        # --- Connect to Redshift ---
        redshift_conn = psycopg2.connect(
            host=os.environ['REDSHIFT_HOST'],
            dbname=os.environ['REDSHIFT_DB'],
            user=os.environ['REDSHIFT_USER'],
            password=os.environ['REDSHIFT_PASS'],
            port=5439
        )
        redshift_cur = redshift_conn.cursor()

        # Insert into Redshift final_table
        insert_query = """
            INSERT INTO final_table (customer_id, customer_name, amount, notes)
            VALUES (%s, %s, %s, %s);
        """
        for row in rows:
            redshift_cur.execute(insert_query, row)

        # Commit and close
        redshift_conn.commit()
        rds_cur.close()
        rds_conn.close()
        redshift_cur.close()
        redshift_conn.close()

        return {
            'statusCode': 200,
            'body': f"Successfully transferred {len(rows)} rows from RDS to Redshift"
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }
