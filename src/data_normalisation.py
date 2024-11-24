import sys
import os

# Add the project root to the PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data_ingestion import loading_data

def normalize_data(data):
    normalized_data = []
    for item in data:
        # Example normalization process:
        # Convert total_price to float
        item['total_price'] = float(item['total_price'])
        
        # Normalize date_time (example: parse to datetime object)
        # item['date_time'] = datetime.strptime(item['date_time'], "%d/%m/%Y %H:%M")
        
        # Normalize order (example: split order items)
        item['order'] = item['order'].split(", ")
        
        # Normalize card_info (example: convert scientific notation to string)
        if item['card_info']:
            item['card_info'] = str(int(float(item['card_info'])))
        
        normalized_data.append(item)
    return normalized_data

data = loading_data()
normalized_data = normalize_data(data)
print(normalized_data)