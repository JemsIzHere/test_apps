from scraper import ItemPage, ACPage, MergePage, BASE_URL
from config import item_tags

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





    # needs to be scalable or most likely to be a part of later
    if 'ac' in item_links:
        ac = ACPage(item_links['ac'])
        print(f'{ac.get_price()} AC')
    
    if 'merge' in item_links:
        merge = MergePage(item_links['merge'])



if __name__ == "__main__":
    print("Input item:")
    search_item = input().lower()
    main(search_item)