import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

#load environment variables from .env file
load_dotenv()
host_name = os.getenv('DB_HOST')
database_name = os.getenv('DB_NAME')
user_name = os.getenv('DB_USER')
user_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT')

def create_database(host, user, password, db_name, port):
    connection = psycopg2.connect(host=host, database="postgres", user=user, password=password, port=port)
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
    cursor.close()
    connection.close()

def setup_db_connection(host=host_name, user=user_name, password=user_password, db=database_name, port=db_port):
    connection = psycopg2.connect(host=host, database=db, user=user, password=password, port=port)
    return connection

def create_db_tables(connection):
    create_transaction_table = """
        CREATE TABLE IF NOT EXISTS transaction_table(
            transaction_id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            time TIME NOT NULL,
            total_price DECIMAL NOT NULL,
            checked_total DECIMAL NOT NULL,
            total_match BOOLEAN NOT NULL,
            location_id INT NOT NULL,
            payment_method_id INT NOT NULL
        );
    """
    create_items_table = """
        CREATE TABLE IF NOT EXISTS items_table(
            item_id SERIAL PRIMARY KEY,
            item_name VARCHAR(100) NOT NULL
        );
    """
    create_item_details_table = """
        CREATE TABLE IF NOT EXISTS item_details_table(
            item_details_id SERIAL PRIMARY KEY,
            item_id INT NOT NULL,
            item_size VARCHAR(50) NOT NULL,
            item_price DECIMAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items_table(item_id)
        );
    """
    create_transaction_items_table = """
        CREATE TABLE IF NOT EXISTS transaction_items_table(
            transaction_id INT NOT NULL,
            item_details_id INT NOT NULL,
            quantity INT NOT NULL,
            PRIMARY KEY (transaction_id, item_details_id),
            FOREIGN KEY (transaction_id) REFERENCES transaction_table(transaction_id),
            FOREIGN KEY (item_details_id) REFERENCES item_details_table(item_details_id)
        );
    """
    create_locations_table = """
        CREATE TABLE IF NOT EXISTS locations_table(
            location_id SERIAL PRIMARY KEY,
            location VARCHAR(100) NOT NULL
        );
    """
    create_payment_method_table = """
        CREATE TABLE IF NOT EXISTS payment_method_table(
            payment_method_id SERIAL PRIMARY KEY,
            payment_method VARCHAR(50) NOT NULL
        );
    """
    #add unique contraints to handle duplicate data in the locations_table
    alter_locations_table = """
        ALTER TABLE locations_table ADD CONSTRAINT unique_location UNIQUE (location);
    """
    #add unique contraints to handle duplicate data in the payment_method_table
    alter_payment_method_table = """
        ALTER TABLE payment_method_table ADD CONSTRAINT unique_payment_method UNIQUE (payment_method);
    """
    #add unique contraints to handle duplicate data in the items_table
    alter_items_table = """
        ALTER TABLE items_table ADD CONSTRAINT unique_item_name UNIQUE (item_name);
    """
    
    cursor = connection.cursor()
    cursor.execute(create_transaction_table)
    cursor.execute(create_items_table)
    cursor.execute(create_item_details_table)
    cursor.execute(create_transaction_items_table)
    cursor.execute(create_locations_table)
    cursor.execute(create_payment_method_table)
    connection.commit()

    cursor.execute(alter_locations_table)
    cursor.execute(alter_payment_method_table)
    cursor.execute(alter_items_table)
    connection.commit()

    cursor.close()

if __name__ == "__main__":
    create_database(host_name, user_name, user_password, database_name, db_port)
    connection = setup_db_connection(host_name, user_name, user_password, database_name, db_port)
    create_db_tables(connection)
    connection.close()
