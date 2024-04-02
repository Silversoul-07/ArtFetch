import json
from urllib.parse import urlparse

def classify_links(links):
    with open(r'Support files\sorted_links.json', 'r') as f:
        categories = json.load(f)
    errors = 0

    for link in links:
        try:
            if link.startswith('data:image'):
                domain = 'base64'
            else:
                # extract domain name, ignoring subdomains
                domain = urlparse(link).netloc.split('.')[-2:]
                domain = '.'.join(domain)
        except Exception:
            errors += 1
            continue

        if domain in categories:
            categories[domain].append(link)
        else:
            categories[domain] = [link]

    with open(r'Support files\sorted_links.json', 'w') as f:
        json.dump(categories, f)
    
    print(f'Errors: {errors}')

def extract_specific_links(domain):
    with open(r'Support files\sorted_links.json', 'r') as f:
        categories = json.load(f)
    
    if domain in categories:
        return categories[domain]
    else:
        return []
    
def extract_all_links():
    with open(r'Support files\sorted_links.json', 'r') as f:
        categories = json.load(f)
    
    return categories

def delete_links(domain):
    with open(r'Support files\sorted_links.json', 'r') as f:
        categories = json.load(f)
    
    if domain in categories:
        del categories[domain]
    
    with open(r'Support files\sorted_links.json', 'w') as f:
        json.dump(categories, f)
    
    print(f'Deleted {domain}')  

def delete_all_links():
    with open(r'Support files\sorted_links.json', 'w') as f:
        f.write('{}')
    
    print('Deleted all links')