import json
import boto3
import logging

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# S3 client
s3_client = boto3.client('s3')

# Destination bucket
destination_bucket = 'pedya-output'

def delete_object(bucket, filename):
    """Delete a file from the source bucket."""
    response = s3_client.delete_object(
        Bucket=bucket,
        Key=filename
    )
    return response['ResponseMetadata']['HTTPStatusCode'] == 204

def lambda_handler(event, context):
    logger.info("Lambda execution started.")
    logger.info(f"Event: {json.dumps(event)}")

    # Extract bucket and file info from event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    filename = event['Records'][0]['s3']['object']['key']

    logger.info(f"File detected: {filename} from {source_bucket}")

    # Copy to destination
    s3_client.copy_object(
        Bucket=destination_bucket,
        CopySource={'Bucket': source_bucket, 'Key': filename},
        Key=filename
    )
    logger.info(f"Copied {filename} to {destination_bucket}")

    # Delete from source
    if delete_object(source_bucket, filename):
        logger.info(f"Moved {filename} successfully.")
    else:
        logger.warning(f"Failed to delete {filename} after copy.")

    return {
        'statusCode': 200,
        'body': json.dumps(f"Moved {filename} from {source_bucket} to {destination_bucket}")
    }
