import csv
import os

def loading_data():
    #Get the directory of the of the raw data. Everyone will have different local directory structure
    script_dir = os.path.dirname(__file__)
    #As long as the repository structure remains the same, the raw data can be accessed
    csv_file_path = os.path.join(script_dir, '..', 'data', 'raw', 'leeds_data.csv')
    #Empty list to later print our list of dictionaries
    sale_data = [] 
    try:
        with open(csv_file_path, 'r', newline="") as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=["date_time", "location", "name", "order", "total_price", "payment_method", "card_info"]) #Add headers to csv file
            for row in reader:
                sale_data.append(row)
    #Error checking
    except FileNotFoundError: 
        print("csv file not found")

    return(sale_data)