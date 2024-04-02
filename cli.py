# Description: Command line interface for the application
from Extensions import classify_links, extract_specific_links, decoder
import os
from uuid import uuid4
if __name__ == "__main__":
    save = {}
    
    for i in extract_specific_links('base64'):
        filetype, content = decoder(i)
        filename = os.path.join('Downloads', f'{uuid4().hex}.{filetype}')
        with open(filename, 'wb') as f:
            f.write(content)
    