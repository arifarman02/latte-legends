from connection_db import setup_db_connection
import logging
from download_from_s3 import download_from_s3
import json

#set up logger
LOGGER = logging.getLogger()
#set logger level to info
LOGGER.setLevel(logging.INFO)

#credentials
host_name = "redshiftcluster-2mdz2z5k6u5l.cevjfhhfzr6y.eu-west-1.redshift.amazonaws.com"
database_name = "latte_lagends_cafe_db"
user_name = "latte_lagends_user"
user_password = "lmyTZFeSDQc7p"
db_port = 5439

def lambda_handler(event,context):
    LOGGER.info("beginning second lambda")
    #connect to database
    LOGGER.info("Setting up connection")
    connection = setup_db_connection(host=host_name, user=user_name, password=user_password, db=database_name, port=db_port)
    LOGGER.info("Connection sucessful")
    #set up cursor
    cursor = connection.cursor()

    #get the clean data 
    LOGGER.info("downloading from S3")
    clean_data = download_from_s3(event)
    LOGGER.info("S3 download complete")
    #dict reader
    print("Here is the downloaded data:")
    print(clean_data)


    #insert data into correct tables
    #transaction_table - date,time,total_price,checked_total,total_match
    #items_table - item_name
    #item_details - item_size, item_price
    #transaction_items_table - quantity??
    #locations_table - location
   # payment_methods_table - payment_method
    for record in clean_data:
        try:
            # Insert into locations_table and get location_id
            cursor.execute("""
                SELECT location_id FROM locations_table WHERE location = %s
                """, 
                (record['location'],)
            )
            result = cursor.fetchone()
            if result:
                location_id = result[0]
            else:
                cursor.execute("""
                    INSERT INTO locations_table (location)
                    VALUES (%s)
                    """, 
                    (record['location'],)
                )
                cursor.execute("SELECT MAX(location_id) FROM locations_table WHERE location = %s", (record['location'],))
                location_id = cursor.fetchone()[0]

            # Insert into payment_methods_table and get payment_method_id
            cursor.execute("""
                SELECT payment_method_id FROM payment_method_table WHERE payment_method = %s
                """, 
                (record['payment_method'],)
            )
            result = cursor.fetchone()
            if result:
                payment_method_id = result[0]
            else:
                cursor.execute("""
                    INSERT INTO payment_method_table (payment_method)
                    VALUES (%s)
                    """, 
                    (record['payment_method'],)
                )
                cursor.execute("SELECT MAX(payment_method_id) FROM payment_method_table WHERE payment_method = %s", (record['payment_method'],))
                payment_method_id = cursor.fetchone()[0]

            # Insert into transaction_table
            cursor.execute("""
                INSERT INTO transaction_table (date, time, total_price, checked_total, total_match, location_id, payment_method_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (record['date'], record['time'], record['total_price'], record['checked_total'], record['total_match'], location_id, payment_method_id)
            )

            # Get the transaction ID (assuming it's auto-generated and returned)
            cursor.execute("SELECT MAX(transaction_id) FROM transaction_table")
            transaction_id = cursor.fetchone()[0]

            # Insert each item
            for i in range(1, 6):
                item_name = record.get(f'item_{i}_name')
                item_size = record.get(f'item_{i}_size')
                item_price = record.get(f'item_{i}_price')

                if item_name and item_name.strip():  # Only insert non-empty item names
                    # Insert into items_table (if not already present)
                    cursor.execute("""
                        SELECT item_id FROM items_table WHERE item_name = %s
                        """, 
                        (item_name,)
                    )
                    result = cursor.fetchone()
                    if not result:
                        cursor.execute("""
                            INSERT INTO items_table (item_name)
                            VALUES (%s)
                            """, 
                            (item_name,)
                        )
                        cursor.execute("SELECT MAX(item_id) FROM items_table WHERE item_name = %s", (item_name,))
                        item_id = cursor.fetchone()[0]
                    else:
                        item_id = result[0]

                    # Insert into item_details_table
                    cursor.execute("""
                        SELECT item_details_id FROM item_details_table WHERE item_id = %s AND item_size = %s AND item_price = %s
                        """,
                        (item_id, item_size, item_price)
                    )
                    result = cursor.fetchone()
                    if not result:
                        cursor.execute("""
                            INSERT INTO item_details_table (item_id, item_size, item_price)
                            VALUES (%s, %s, %s)
                            """,
                            (item_id, item_size, item_price)
                        )
                        cursor.execute("SELECT MAX(item_details_id) FROM item_details_table WHERE item_id = %s AND item_size = %s AND item_price = %s", (item_id, item_size, item_price))
                        item_details_id = cursor.fetchone()[0]
                    else:
                        item_details_id = result[0]

                    # Insert into transaction_items_table
                    cursor.execute("""
                        INSERT INTO transaction_items_table (transaction_id, item_details_id, quantity)
                        VALUES (%s, %s, %s)
                        """,
                        (transaction_id, item_details_id, 1)  # Assuming quantity is 1 for simplicity
                    )

            # Commit the transaction after each record
            connection.commit()
            LOGGER.info("Data inserted successfully for record: %s", record)

        except Exception as e:
            LOGGER.error("Error inserting data for record: %s, error: %s", record, e)
            connection.rollback()

    # Close the database connection
    cursor.close()
    connection.close()