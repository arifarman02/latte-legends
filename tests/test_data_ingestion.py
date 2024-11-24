import pytest
import csv
import os
from src.data_ingestion import loading_data

def test_loading_data_file_not_found(monkeypatch):
    #monkeypatch os.path.join to return a non-existent path
    def mock_join(*args):
        return 'non_existing_path/leeds_data.csv'
    monkeypatch.setattr(os.path, 'join', mock_join)
    #execute the function
    result = loading_data()
    #assert the result is an empty list since the file does not exist
    assert result == []
