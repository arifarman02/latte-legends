#from data_ingestion import loading_data
import os
import csv

def main():
    #data = loading_data()
    data_no_card = remove_card_info(data)
    data_no_name = remove_name_info(data_no_card)
    data_time_split = date_time_split(data_no_name)
    data_two_decimals = total_to_decimal(data_time_split)
    data_split_orders = split_order(data_two_decimals)
    data_clean = check_total(data_split_orders)
    #print_data_clean(data_clean)
    
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

        #split date and reformat
        month,day,year = date.split('/')
        date = f'{year}-{month}-{day}'

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
    #return data
    return data

def save_dict_to_csv(data):
    #open new file called
    field_names = ["date_time", "location", "name", "order", "total_price", "payment_method", "card_info"]
    with open("clean_data.csv", "w"):
        #create writer
        writer = csv.DictWriter(data,fieldnames=field_names)
        #write headings
        writer.writeheader()
        #write rows
        writer.writerows(data)
        

def print_data_clean(data):
    #This function prints out the dictionary of transactions neatly
    for transaction in data:
        for key,value in transaction.items():
            print(f"{key}: {value}")
        print()

if __name__ == "__main__":
    main()

