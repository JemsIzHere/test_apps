from scraper import ItemPage, ACItem, BASE_URL
from config import item_types

def main(search_item: str):
    page = ItemPage(search_item)
    page_links = page.get_links()
    item_links = check_links(page_links)
    ac_link = ACItem(item_links.get("ac"))

    if not page.exists():
        print('Item page does not exist.')
        return

    print(f'\nMain Page: {page.full_url}')
    
    print(f'{ac_link.get_price()} AC')
    # print(type_item)

def check_links(links):
    item_links = {}

    for link in links:
        part = link.split('-')[-1]            
        tag = next((t for t in item_types if t in part), None)
        if tag:
            item_links[tag] = (f'{BASE_URL}{link}')

    return item_links
    
if __name__ == "__main__":
    print("Input item:")
    search_item = input().lower()
    main(search_item)