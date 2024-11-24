import os
import csv
import psycopg2
from dotenv import load_dotenv

#load environment variables from .env file
load_dotenv()
host_name = os.getenv('DB_HOST')
database_name = os.getenv('DB_NAME')
user_name = os.getenv('DB_USER')
user_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT')

def setup_db_connection(host=host_name, user=user_name, password=user_password, db=database_name, port=db_port):
    connection = psycopg2.connect(host=host, database=db, user=user, password=password, port=port)
    return connection

def insert_data(connection, csv_file_path):
    cursor = connection.cursor()
    #location and payments table
    #location and paymen methods are non duplicate values
    locations = set()
    payment_methods = set()
    #read cleaned csv file and append the location and payment_methods
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            locations.add(row['location'])
            payment_methods.add(row['payment_method'])
    #insert values into the correct table
    for location in locations:
        cursor.execute("INSERT INTO locations_table (location) VALUES (%s) ON CONFLICT DO NOTHING", (location,))
    for payment_method in payment_methods:
        cursor.execute("INSERT INTO payment_method_table (payment_method) VALUES (%s) ON CONFLICT DO NOTHING", (payment_method,))
    #save the changes
    connection.commit()
    #transaction table
    #get location and payment method ids
    cursor.execute("SELECT location_id, location FROM locations_table")
    location_ids = {row[1]: row[0] for row in cursor.fetchall()}  
    cursor.execute("SELECT payment_method_id, payment_method FROM payment_method_table")
    payment_method_ids = {row[1]: row[0] for row in cursor.fetchall()}
    #get date, time, total_price, checked total, total_match, location_id, payment_method
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            location_id = location_ids[row['location']]
            payment_method_id = payment_method_ids[row['payment_method']]
            #handle total_match as boolean (assuming 'True' or 'False' strings)
            total_match = row['total_match'].strip().lower() == 'true' if row.get('total_match') else False
            #insert data into transaction_table
            cursor.execute("""
                INSERT INTO transaction_table (date, time, total_price, checked_total, total_match, Location_id, payment_method_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING transaction_id
            """, (row['date'], row['time'], row['total_price'], row['checked_total'], total_match, location_id, payment_method_id))
            transaction_id = cursor.fetchone()[0]
            #make this more dynamic as it assumes there will be 4 times in the record
            for i in range(1, 5):
                item_name_key = f'item_{i}_name'
                item_size_key = f'item_{i}_size'
                item_price_key = f'item_{i}_price'
                if row.get(item_name_key):
                    item_name = row[item_name_key]
                    item_size = row[item_size_key]
                    item_price = row[item_price_key]
                    #inser the items info
                    cursor.execute("INSERT INTO items_table (item_name) VALUES (%s) ON CONFLICT (item_name) DO UPDATE SET item_name=EXCLUDED.item_name RETURNING item_id", (item_name,))
                    item_id = cursor.fetchone()[0]
                      #check if item_price exists and is not empty
                    if row.get(item_price_key):
                        item_price = row[item_price_key]
                    else:
                        item_price = 0.0
                    #insert info in the Item_details_table
                    cursor.execute("""
                        INSERT INTO item_details_table (item_id, item_size, item_price)
                        VALUES (%s, %s, %s) RETURNING item_details_id
                    """, (item_id, item_size, item_price))
                    item_details_id = cursor.fetchone()[0]
                    #insert data in the transaction_items_table
                    cursor.execute("""
                        INSERT INTO transaction_items_table (transaction_id, item_details_id, quantity)
                        VALUES (%s, %s, %s)
                    """, (transaction_id, item_details_id, 1))
    connection.commit()
    cursor.close()

if __name__ == "__main__":
    connection = setup_db_connection(host_name, user_name, user_password, database_name, db_port)
    csv_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'leeds_processed_data.csv')
    insert_data(connection, csv_file_path)
    connection.close()