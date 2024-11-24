import psycopg2
import logging


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


def setup_db_connection(host=host_name, user=user_name, password=user_password, db=database_name, port=db_port):
    connection = psycopg2.connect(host=host, database=db, user=user, password=password, port=port)
    return connection

def create_db_tables(connection):

    create_sequences = """
        CREATE SEQUENCE transaction_id_seq START 1;
        CREATE SEQUENCE item_id_seq START 1;
        CREATE SEQUENCE item_details_id_seq START 1;
        CREATE SEQUENCE location_id_seq START 1;
        CREATE SEQUENCE payment_method_id_seq START 1;
);
    """
    create_transaction_table = """
        CREATE TABLE IF NOT EXISTS transaction_table (
    transaction_id INTEGER PRIMARY KEY DEFAULT nextval('transaction_id_seq'),
    date DATE NOT NULL,
    time TIME NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    checked_total DECIMAL(10, 2) NOT NULL,
    total_match BOOLEAN NOT NULL,
    location_id INT NOT NULL,
    payment_method_id INT NOT NULL
);
    """
    create_items_table = """
        CREATE TABLE IF NOT EXISTS items_table (
    item_id INTEGER PRIMARY KEY DEFAULT nextval('item_id_seq'),
    item_name VARCHAR(100) NOT NULL,
    CONSTRAINT unique_item_name UNIQUE (item_name)
);
    """
    create_item_details_table = """
        item_details_id INTEGER PRIMARY KEY DEFAULT nextval('item_details_id_seq'),
    item_id INT NOT NULL,
    item_size VARCHAR(50) NOT NULL,
    item_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items_table(item_id)
);
    """
    create_transaction_items_table = """
    CREATE TABLE IF NOT EXISTS transaction_items_table (
    transaction_id INT NOT NULL,
    item_details_id INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (transaction_id, item_details_id),
    FOREIGN KEY (transaction_id) REFERENCES transaction_table(transaction_id),
    FOREIGN KEY (item_details_id) REFERENCES item_details_table(item_details_id)
);
    """
    create_locations_table = """
    CREATE TABLE IF NOT EXISTS locations_table (
    location_id INTEGER PRIMARY KEY DEFAULT nextval('location_id_seq'),
    location VARCHAR(100) NOT NULL,
    CONSTRAINT unique_location UNIQUE (location)
);
    """
    create_payment_method_table = """
    CREATE TABLE IF NOT EXISTS payment_method_table (
    payment_method_id INTEGER PRIMARY KEY DEFAULT nextval('payment_method_id_seq'),
    payment_method VARCHAR(50) NOT NULL,
    CONSTRAINT unique_payment_method UNIQUE (payment_method)
);
    """
    #create all the tables 
    LOGGER.info('Creating tables')
    cursor = connection.cursor()
    cursor.execute(create_sequences)
    cursor.execute(create_transaction_table)
    cursor.execute(create_items_table)
    cursor.execute(create_item_details_table)
    cursor.execute(create_transaction_items_table)
    cursor.execute(create_locations_table)
    cursor.execute(create_payment_method_table)
    connection.commit()
    LOGGER.info('All tables created')
    connection.commit()
    cursor.close()

if __name__ == "__main__":
    connection = setup_db_connection(host_name, user_name, user_password, database_name, db_port)
    create_db_tables(connection)
