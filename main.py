from scraper import ItemPage, ACItem, BASE_URL
from config import item_types

def main(search_item: str):
    page = ItemPage(search_item)
    page_links = page.get_links()
    #item_links = split_link(page_links)
    item_links = check_links(page_links)

    if not page.exists():
        print('Item page does not exist.')
        return

    print(f'\nMain Page: {page.full_url}')
    
    print(f'{item_links}')
    # print(type_item)


#def categorize_links(links):



def check_links(links):
    item_links = []

    for link in links:
        part = link.split('-')[-1]            
        if any(tag in part for tag in item_types):
            item_links.append(f'{BASE_URL}{link}')

    return item_links
    

# # might have to remove
# def split_link(links):
#     item_links = []

#     for link in links:
#         part = link.split('-')[-1]
#         print(part)
#         if check_item_tag(part) or check_item_type(part):
#             item_links.append(f'{BASE_URL}{link}')

#     return item_links

# def check_item_tag(links):

#     for link in links:
#         part = link.split('-')[-1]
#         if any(tag in part for tag in ITEM_TAGS):
#             tagged_item = f'{BASE_URL}{link}'
#         return tagged_item
#     return
        
# # should be a single method but data is from wiki
# def check_item_type(links):
#     for link in links:
#         part = link.split('-')[-1]
#         if any(tag in part for tag in item_types):
#             tagged_item = f'{BASE_URL}{link}'
#         return tagged_item
#     return

if __name__ == "__main__":
    print("Input item:")
    search_item = input().lower()
    main(search_item)