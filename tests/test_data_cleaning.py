import pytest
import sys
import os

from src.data_ingestion import loading_data
from src.data_cleaning import (
    remove_card_info,
    remove_name_info,
    date_time_split,
    total_to_decimal,
    split_order,
    check_total,
    reorder_headers,
)

def sample_data():
    return [
        {
            'location': 'Leeds',
            'card_info': '1234-5678-9876-5432',
            'name': 'John Doe',
            'date_time': '2023-07-24 14:55:30',
            'total_price': '10.50',
            'payment_method': 'Credit Card',
            'order': 'Small Coffee 2.50, Medium Latte 4.00, Large Espresso 4.00'
        }
    ]

def test_remove_card_info(sample_data):
    data_no_card = remove_card_info(sample_data)
    for transaction in data_no_card:
        assert 'card_info' not in transaction