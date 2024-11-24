import logging
import boto3
import json
import csv
from io import StringIO
import io
from data_cleaning import remove_card_info,remove_name_info, date_time_split, split_order, check_total, total_to_decimal, print_data_clean
from download_tools import get_prefix,check_processed,add_to_processed

#set up logger
LOGGER = logging.getLogger()
#set logger level to info
LOGGER.setLevel(logging.INFO)

#lambda function that will execute on trigger
def lambda_handler(event, context):
    #show event structure
    LOGGER.info(f'Event structure: {json.dumps(event, indent=2)}')

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
    
    #get prefix
    prefix = get_prefix(object_key)

    #list all objects in with prefix
    try:
        LOGGER.info("Listing all objects with matching prefix")
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' not in response:
            LOGGER.error(f"No objects found with prefix {prefix}")
            return {
                'statusCode': 400,
                'body': json.dumps(f"No objects found in prefix: {prefix}")
            }
    except Exception as e:
        # Log and return an error if listing objects fails
        LOGGER.error(f"Error listing objects in S3: \n{e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error listing objects in S3: {e}")
        }

    print(f"contents:\n{response['Contents']}")
    #get list of processed object keys
    
    #iterate over each object in prefix
    for object in response['Contents']:
        #check if already processed
        if check_processed(object_key,LOGGER) == False:
            # Download data 
            try:
                object_key = object['Key']
                LOGGER.info(f'Attempting to download object: {object_key} from bucket: {bucket_name}')
                #get resonse
                response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
                # Convert binary to string
                data_csv = response['Body'].read().decode('utf-8')
                #log progress
                LOGGER.info(f'Successfully downloaded object: {object_key} from bucket: {bucket_name}')
        
                # Read data using csv module
                try:
                    LOGGER.info('Attempting to read CSV data')
                    # StringIO makes CSV string a "file-like" format that csv.reader() can understand
                    csv_file = StringIO(data_csv)
                    #set field names for csv
                    field_names = ["date_time", "location", "name", "order", "total_price", "payment_method", "card_info"]
                    #read in the csv as dict
                    csv_reader = csv.DictReader(csv_file, fieldnames = field_names)
                    
                    data = []
                    # Print CSV data and store
                    for row in csv_reader:
                        data.append(row)
                    LOGGER.info(f'{object_key} read in complete')
                except Exception as e:
                    LOGGER.error(f"Error reading CSV: {e}")
                    return {
                        'statusCode': 500,
                        'body': json.dumps(f"Error reading CSV: {e}")
                    }
                
                #clean data
                
                #remove card info from data
                data_no_card = remove_card_info(data)
                LOGGER.info(f'remove_card_data for {object_key} was successful')
                
                #remove name from data
                data_no_name = remove_name_info(data_no_card)
                LOGGER.info(f'remove_name_info for {object_key} was successful')
                
                #split datetime into date and time
                data_time_split = date_time_split(data_no_name)
                LOGGER.info(f'date_time_split for {object_key}  was successful')
                
                #set prices to 2 decimals
                data_two_decimals = total_to_decimal(data_time_split)
                LOGGER.info(f'data_two_decimals for {object_key}  was successful')
                
                #split orders into items
                data_split_orders = split_order(data_two_decimals)
                LOGGER.info(f'split_orders for {object_key}  was successful')
                
                #check sum of item prices equals the total
                data_clean = check_total(data_split_orders)
                LOGGER.info(f'data_clean for {object_key}  was successful')
                
                #print out the data
                #print_data_clean(data_clean)
                LOGGER.info(f"{object_key} first row: {data_clean[0]}")

                #save clean_data to bucket
                LOGGER.info(f'saving cleaned data to s3 as CSV')
                #name of bucket to save to
                clean_bucket = "latte-legends-clean-data"

                #desired file name
                file_name = f"clean_{object_key.split('/')[-1]}"

                #create buffer. This makes the text appear like a file to csv reader
                csv_buffer = io.StringIO()

                #get updated field names
                #get the longest field names in clean data
                longest = 0
                field_names = []
                for data in data_clean:
                    #look for longest list of field names
                    #print(data.keys())
                    if len(data.keys()) > longest:
                        longest = len(data.keys())
                        field_names = [name for name in data.keys()]

                #print(f"field names for {object_key}: {field_names}")
                LOGGER.info(f'{object_key} field names calculated')

                #create dict writer
                writer = csv.DictWriter(csv_buffer,fieldnames=field_names)

                #write header
                writer.writeheader()
                
                #write rows
                writer.writerows(data_clean)

                #get csv string from buffer
                csv_string = csv_buffer.getvalue()
                LOGGER.info('Uploading to bucket')
                #upload to bucket
                s3_client.put_object(Bucket = clean_bucket, Key = file_name, Body = csv_string)
                #add to processed list
                add_to_processed(object_key,LOGGER)
            
                
                LOGGER.info(f'{file_name} saved to bucket')

            except Exception as e:
                    LOGGER.error(f"Error: {e}")
                    return {
                        'statusCode': 500,
                        'body': json.dumps(f"Error: {e}")
                    }
        else:
            LOGGER.info(f"{object_key} already processed")
            pass