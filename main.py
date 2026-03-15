from scraper import ItemSearch, ACPage, MergePage, BASE_URL
from config import item_tags

def main(search_item: str):
    page = ItemSearch(search_item)
    # item_links = page.check_links()
    # main_links = page.get_main_links()

    search_link = page.get_main_page()

    if not page.exists():
        print('Item page does not exist.')
        return

    page.get_possible_items()

    print(f'\nMain Page: {search_link}')

    page.categorize_links()

    # for i in main_links:
    #     print(i)

    # needs to be scalable or most likely to be a part of later
    # if 'ac' in item_links:
    #     ac = ACPage(item_links['ac'])
    #     ac.process()
    # if 'merge' in item_links:
    #     merge = MergePage(item_links['merge'])



if __name__ == "__main__":
    print("Input item:")
    search_item = input()
    main(search_item)