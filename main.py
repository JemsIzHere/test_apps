from scraper import ItemPage, ACItem, MergeItem, BASE_URL
from config import item_types

def main(search_item: str):
    page = ItemPage(search_item)
    item_links = page.check_links()
    main_links = page.get_main_links()

    if not page.exists():
        print('Item page does not exist.')
        return

    print(f'\nMain Page: {page.full_url}')

    for i in main_links:
        print(i)

    # needs to be scalable
    if 'ac' in item_links:
        ac = ACItem(item_links['ac'])
        print(f'{ac.get_price()} AC')
    
    if 'merge' in item_links:
        merge = MergeItem(item_links['merge'])


# moved to ItemPage
# def check_links(links):

if __name__ == "__main__":
    print("Input item:")
    search_item = input().lower()
    main(search_item)