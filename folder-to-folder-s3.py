import json
import boto3
import logging
from botocore.exceptions import ClientError

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# S3 client
s3_client = boto3.client('s3')

# Buckets
source_bucket = 'folder-1-input'
destination_bucket = 'folder-1-output'

def delete_object(bucket, filename):
    """Delete a file from the source bucket."""
    try:
        response = s3_client.delete_object(Bucket=bucket, Key=filename)
        return response['ResponseMetadata']['HTTPStatusCode'] == 204
    except ClientError as e:
        logger.error(f"Failed to delete {filename} from {bucket}: {e}")
        return False

def lambda_handler(event, context):
    logger.info("Lambda execution started.")
    logger.info(f"Event: {json.dumps(event)}")

    try:
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        filename = event['Records'][0]['s3']['object']['key']
        logger.info(f"Processing file: {filename} from {source_bucket}")
    except Exception as e:
        logger.error(f"Failed to parse S3 event: {e}")
        return {"statusCode": 400, "body": "Bad event structure"}

    try:
        s3_client.copy_object(
            Bucket=destination_bucket,
            CopySource={'Bucket': source_bucket, 'Key': filename},
            Key=filename
        )
        logger.info(f"Copied {filename} to {destination_bucket}")
    except ClientError as e:
        logger.error(f"Failed to copy {filename} from {source_bucket} to {destination_bucket}: {e}")
        return {"statusCode": 500, "body": f"Copy failed for {filename}"}

    if delete_object(source_bucket, filename):
        logger.info(f"Moved {filename} successfully.")
    else:
        logger.warning(f"Copied {filename}, but failed to delete from {source_bucket}")

    return {
        'statusCode': 200,
        'body': json.dumps(f"Moved {filename} from {source_bucket} to {destination_bucket}")
    }
