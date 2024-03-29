from Extensions import scrape_images_from_google

if __name__ == "__main__":
    query = input("Enter your query: ")
    limit = int(input("Enter the number of images you want to scrape: "))
    img_srcs = scrape_images_from_google(query, limit)
    print(img_srcs)