from scraper import ItemPage, ACItem, BASE_URL

def main(search_item: str):
    page = ItemPage(search_item)

    if not page.exists():
        return

    print(f'\nMain Page: {page.full_url}')
    print(page.get_links())



if __name__ == "__main__":
    print("Input item:")
    search_item = input().lower()
    main(search_item)