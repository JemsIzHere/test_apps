from item_scrape.scraper import ItemSearch,MergePage,QuestPage
from data_loader import item_tags

def main(search_item: str):
    page = ItemSearch(search_item)
    merge = MergePage('http://aqwwiki.wikidot.com/necrotic-sword-of-doom-sword')
    quest = QuestPage('http://aqwwiki.wikidot.com/legion-revenant-class')

    #search_link = page.get_main_page()

    # if not page.exists():
    #     print('Item page does not exist.')
    #     return

    #page.get_possible_items()

    #print(f'\nMain Page: {search_link}')

    print(quest.is_valid())

    # page.categorize_links()



if __name__ == "__main__":
    print("Input item:")
    # search_item = input()
    search_item = "Test"
    main(search_item)