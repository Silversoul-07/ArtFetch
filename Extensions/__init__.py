from Extensions.Download.Database import fetch_data, batch_insert, batch_update
from Extensions.Download.Downloader import Downloader, decoder
from Extensions.search.Google import scrape_images_from_google
from Extensions.Download.link_classifier import classify_links, extract_specific_links, extract_all_links, delete_links, delete_all_links


args = [
    'fetch_data',
    'batch_insert',
    'batch_update',
    'Downloader',
    'scrape_images_from_google',
    'classify_links',
    'extract_specific_links',
    'extract_all_links',
    'delete_links',
    'delete_all_links'
]

def get_agrs():
    return ', '.join(args)