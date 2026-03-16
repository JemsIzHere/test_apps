from item_scrape.scraper import ItemSearch,MergePage
from data_loader import item_tags

def main(search_item: str):
    page = ItemSearch(search_item)
    merge = MergePage('http://aqwwiki.wikidot.com/legion-doomblade-ac')


    search_link = page.get_main_page()

    if not page.exists():
        print('Item page does not exist.')
        return

    page.get_possible_items()

    print(f'\nMain Page: {search_link}')

    page.categorize_links()

    merge.process()


if __name__ == "__main__":
    print("Input item:")
    search_item = input()
    main(search_item)