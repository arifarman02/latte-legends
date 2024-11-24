import logging
import boto3
import json
import csv
from io import StringIO
import io

def get_prefix(object_key):
    #split object key
    parts = object_key.split('/')

    #check length
    if len(parts) != 4:
        raise ValueError(f"Unexpected object key format: {object_key}")
    
    #store parts of file path individually
    year, month, day, filename = parts
    
    #get prefix
    prefix = f"{year}/{month}/"


    return prefix


def check_processed(object_key,LOGGER):
    #get client
    s3_client = boto3.client('s3')
    #table name
    bucket = "latte-legends-processed-files"

    #check object key in bucket
    try:
        s3_client.head_object(Bucket = bucket, Key = object_key)
        LOGGER.info(f"{object_key} was previously processed")
        return True
    except Exception as e:
        LOGGER.info(f"Error checking processed files for {object_key}: {e}")
        return False

def add_to_processed(object_key,LOGGER):
    #get client
    s3_client = boto3.client('s3')
    #table name
    bucket = "latte-legends-processed-files"

    #remove path from object key
    object_key_no_path = object_key.split('/')[-1]

    #put object key in bucket
    try:
        s3_client.put_object(Bucket = bucket, Key = object_key_no_path)
        LOGGER.info(f"{object_key} was saved in bucket")
        return True
    except Exception as e:
        LOGGER.info(f"Error saving name to processed files for {object_key}: {e}")
        return False




