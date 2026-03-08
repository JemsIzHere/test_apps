from bs4 import BeautifulSoup as soup
import requests
import re

# URL for AQW Wiki
url = "http://aqwwiki.wikidot.com" 

merge_items = []
merge_links = []
merge_li = None

print("Input item:")
search_item = input()
search_item = search_item.replace(" ", "-")

result = requests.get(f'{url}/{search_item}')
doc = soup(result.text, "html.parser")

def check_item_exists():
    for p in doc.find_all('strong'):
        if "This page doesn't exist yet!" in p.get_text():
            print("Item does not exist.")
            return False
    return True

def check_item():

    if check_item_exists():
        print(f'Main Page: {url}/{search_item}')

    check_merge()

# for abbreviations (sample)
# if search_item.lower() == "nsod":
#     # necrotic sword of doom sword
#     search_item = "necrotic-sword-of-doom-sword"


def check_merge():
    for li in doc.find_all('li'):
        if "Merge the following:" in li.get_text():
            return li
    return None

def add_to_merge_list(items):
    for item_li in items[1:]:

        a_tag = item_li.find('a')
        if a_tag:
            merge_links.append(a_tag.get('href'))
        
        merge_items.append(f'{item_li.get_text(strip=True)}')


def find_merge_materials():

    merge_li = check_merge()

    if merge_li:
        
        all_items = merge_li.find_parent('ul').find_all('li')
        add_to_merge_list(all_items)
    else:
        return print("Cannot be merged.")

#fix
def parse_item(line):
    line = line.strip()
    
    # matches pattern of itemname + x + digits at the end
    match = re.search(r'\s*x\s*(\d{1,3}(?:,\d{3})*)\s*$', line, re.IGNORECASE)
    if match:
        qty = int(match.group(1).replace(',', ''))  # Remove commas before converting to int
        # removes 'x' and separates the qty
        item_name = re.sub(r'\s*x\s*\d+\s*$', '', line, flags=re.IGNORECASE)
        return {'name': item_name.strip(), 'qty': qty}
    
    match = re.match(r'^(\d+)\s*×\s*(.+)$', line)
    if match:
        qty = int(match.group(1))
        item_name = match.group(2).strip()
        return {'name': item_name, 'qty': qty}
    
    # No quantity found
    return {'name': line, 'qty': None}


check_item() 
find_merge_materials()

parsed = [parse_item(item) for item in merge_items]

for item in parsed:
    print(f"Item: {item['name']}, Quantity: {item['qty']}")

for link in merge_links:
    print(f'{url}{link}')

