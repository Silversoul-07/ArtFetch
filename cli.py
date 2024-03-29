from Extensions import scrape_images_from_google

if __name__ == "__main__":
    query  = "japanese naked women nyotaimori"
    links = scrape_images_from_google(query)

    with open('test.txt', 'w') as file:
        file.write('\n'.join(links))