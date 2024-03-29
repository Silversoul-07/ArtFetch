from Extensions.Database import fetch_data, batch_insert, batch_update
from Extensions.Downloader import Downloader

def get_func():
    args = [
        'fetch_data',
        'batch_insert',
        'batch_update',
        'Downloader'
    ]
    return ', '.join(args)