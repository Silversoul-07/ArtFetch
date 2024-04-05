from Extensions.Download.Database import fetch_data, batch_insert, batch_update, fetch_all_data
from Extensions.Downloader import Downloader, decoder
from Extensions.search.Google import scrape_images_from_google
from Extensions.Download.link_classifier import classify_links, extract_specific_links, extract_all_links, delete_links, delete_all_links
from Extensions.Download.webdriver import get_webdriver, scroll_to_bottom


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