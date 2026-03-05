from bs4 import BeautifulSoup as soup
import requests
import re

# URL for AQW Wiki
url = "http://aqwwiki.wikidot.com/" 

print("Input item:")
search_item = input()
search_item = search_item.replace(" ", "-")

# for abbreviations (sample)
if search_item.lower() == "nsod":
    # necrotic sword of doom sword
    search_item = "necrotic-sword-of-doom-sword"

print(f'Main Page: {url}{search_item}')

# html parse
result = requests.get(f'{url}/{search_item}')
doc = soup(result.text, "html.parser")

# finder
merge_items = []
merge_links = []
merge_li = None

# check merge

# material finder
def find_materials(li):


    if merge_li:
        
        parent_ul = merge_li.find_parent('ul')
        
        if parent_ul:
            
            all_items = parent_ul.find_all('li')
            
            for i, item_li in enumerate(all_items[1:], 1):

                # adds link to merge_links
                a_tag = item_li.find('a')
                if a_tag:
                    merge_links.append(a_tag.get('href'))
                
                # adds item name and qty to merge_items
                merge_items.append(f'/{item_li.get_text(strip=True)}')
                
        # else:
        #     return print("cannot be merged.")
    else:
        return print("Cannot be merged.")

def parse_item(line):
    line = line.strip()
    
    # matches pattern of itemname + x + digits at the end
    match = re.search(r'\s*x\s*(\d+)\s*$', line, re.IGNORECASE)
    if match:
        qty = int(match.group(1))
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

find_materials(merge_li)

parsed = [parse_item(item) for item in merge_items]

for item in parsed:
    print(f"Item: {item['name']}, Quantity: {item['qty']}")

for link in merge_links:
    print(f'{url}{link}')

