import logging
import json
from io import StringIO
import boto3
import csv



def download_from_s3(event):
    #set up logger
    LOGGER = logging.getLogger()
    #set logger level to info
    LOGGER.setLevel(logging.INFO)   
    # download event object (data from the trigger in s3 bucket object)
    s3_client = boto3.client('s3')
    # Get bucket name and object key from event
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']
        LOGGER.info(f'Extracted bucket name: {bucket_name}, object key: {object_key}')
    except KeyError as e:
        LOGGER.error(f"KeyError accessing 'Records': {e}")
        return {
            'statusCode': 400,
            'body': json.dumps(f"KeyError accessing 'Records': {e}")
        }
    
    # Download data 
    try:
        LOGGER.info(f'Attempting to download object: {object_key} from bucket: {bucket_name}')
        #get resonse
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        # Convert binary to string
        data_csv = response['Body'].read().decode('utf-8')
        #log progress
        LOGGER.info(f'Successfully downloaded object: {object_key} from bucket: {bucket_name}')
    except Exception as e:
        LOGGER.error(f"Error downloading file from S3: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error downloading file from S3: {e}")
        }
        
    # Read data using csv module
    try:
        LOGGER.info('Attempting to read CSV data')
        # StringIO makes CSV string a "file-like" format that csv.reader() can understand
        csv_file = StringIO(data_csv)
        #dynamically get field names
        # field_names = ["date","time", "location", "name", "order", "total_price", "payment_method", "card_info"]
        #read in the csv as dict
        csv_reader = csv.DictReader(csv_file)
        #field_names = csv_reader.fieldnames
        
        data = []
        # Print CSV data and store
        for row in csv_reader:
            data.append(row)
            LOGGER.info(f'CSV Row: {row}')
    except Exception as e:
        LOGGER.error(f"Error reading CSV: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error reading CSV: {e}")
        }
    return data