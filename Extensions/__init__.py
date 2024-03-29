from Extensions.Database import fetch_data, batch_insert, batch_update
from Extensions.Downloader import Downloader
from Extensions.Google import scrape_images_from_google


args = [
    'fetch_data',
    'batch_insert',
    'batch_update',
    'Downloader',
    'scrape_images_from_google'
]

def get_agrs():
    return ', '.join(args)