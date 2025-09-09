import redshift_connector
import os

def lambda_handler(event, context):
    try:
        # Read Redshift connection details from environment variables
        conn = redshift_connector.connect(
            host=os.environ["REDSHIFT_HOST"],     # e.g. cluster-name.region.redshift.amazonaws.com
            port=int(os.environ.get("REDSHIFT_PORT", 5439)),
            database=os.environ["REDSHIFT_DB"],   # e.g. dev
            user=os.environ["REDSHIFT_USER"],     # e.g. awsuser
            password=os.environ["REDSHIFT_PASSWORD"]
        )

        cursor = conn.cursor()

        # Example query
        cursor.execute("SELECT current_date;")
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": f"Connected! Query result: {result}"
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
