import os
import csv
from data_ingestion import loading_data

def main():
    data = loading_data()
    data_no_card = remove_card_info(data)
    data_no_name = remove_name_info(data_no_card)
    data_time_split = date_time_split(data_no_name)
    data_two_decimals = total_to_decimal(data_time_split)
    data_split_orders = split_order(data_two_decimals)
    data_clean = check_total(data_split_orders)
    data_reordered_keys = reorder_headers(data_clean)
    print_data_clean(data_reordered_keys)
    save_to_csv(data_clean, "leeds_processed_data.csv")
    
def remove_card_info(data):
    #for every dict in list
    for transaction in data:
        #delete dict['card_info']
        del transaction['card_info']
    return data

def remove_name_info(data):
    #for dict in list
    for transaction in data:
        #delete dict['name']
        del transaction['name']
        #return the new version
    return data

def date_time_split(data):
    #for dict in list
    for transaction in data:
        #add separate date and time columns
        transaction['date'] = ''
        transaction['time'] = ''
    #for dict in list
    for transaction in data:
        #split date and time into two variables
        date, time = transaction['date_time'].split()
        #add the variable to correct columns
        transaction['date'] = date
        transaction['time'] = time
    #delete date and time
    for transaction in data:
        del transaction['date_time']
    return data

def total_to_decimal(data):
    #for every transaction
    for transaction in data:
        #convert str into float
        transaction['total_price'] = f"{float(transaction['total_price']):.2f}"
    return data

def split_order(data):
    #for every transaction
    for transaction in data:
    #split order at comma
        order_items = transaction['order'].split(', ')
        #initiate counter
        counter = 1
        #for each item in the order
        for item in order_items:
        #make 3 new columns names (item_x, item_x_size and item_x_price)
            name_col = f"item_{counter}_name"
            size_col = f"item_{counter}_size"
            price_col = f"item_{counter}_price"
            #split items into list
            split_list = item.split(' ')
            #store first word as size
            size = split_list[0]
            #store name
            name = split_list[1:-2]  
            #rejoin name
            joined_name = ' '.join(name)    
            #store price'
            price = split_list[-1]          
            #add each split value to its correct column
            transaction[name_col] = joined_name
            transaction[size_col] = size
            transaction[price_col] = price
            #increment counter
            counter += 1
        #delete the order column
        del transaction['order']
    #return data
    return data

def check_total(data):
    #for every transaction
    for transaction in data:
        #empty total list
        checked_total = 0.00
        #look through every key
        for key, value in transaction.items():
            #if keyname includes 'price'
            if 'price' in key and 'total' not in key:
                #add value to total list
                checked_total += float(value)
                #maybe convert to 2 decimal places here
                checked_total_formatted = f"{float(checked_total):.2f}"
        transaction['checked_total'] = checked_total_formatted
        #if total == total price
        if transaction['checked_total'] == transaction['total_price']:
        #add new column called total_match and asign it Yes/true/1
            transaction['total_match'] = True
        #elif total != total price
        elif transaction['checked_total'] != transaction['total_price']:
            #add new column called total_match and asign it no/false/0
            transaction['total_match'] = False
    return data

def reorder_headers(data):
    #reorder the keys to avoid issues when uploading to the database
    key_order = ['location', 'total_price', 'payment_method', 'date', 'time', 'checked_total', 'total_match', ]
    #reorder for every transaction in the the csv file
    for i, transaction in enumerate(data):
        ordered_transaction = {key: transaction[key] for key in key_order if key in transaction}
        for key, value in transaction.items():
            if key not in ordered_transaction:
                ordered_transaction[key] = value
        data[i] = ordered_transaction
    #return data
    return data

def save_to_csv(data, filename):
  #get the script directory (same directory as the script)
  script_dir = os.path.dirname(__file__)
  #define the base directory for processed data (assuming a 'data' folder within project)
  base_processed_dir = os.path.join(script_dir, '..', 'data', 'processed')
  #combine base directory and filename to get the full path
  full_file_path = os.path.join(base_processed_dir, filename)
  with open(full_file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    #get all the keys from the first transaction
    fieldnames = list(data[0].keys())
    writer.writerow(fieldnames)
    for transaction in data:
      writer.writerow(transaction.values())

def print_data_clean(data):
    #This function prints out the dictionary of transactions neatly
    for transaction in data:
        for key,value in transaction.items():
            print(f"{key}: {value}")
        print()

if __name__ == "__main__":
    main()

