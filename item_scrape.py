from bs4 import BeautifulSoup as soup
import requests
import json
import re


merge_items = []
merge_links = []
item_tag_url = []
item_links = []
item_tags = ["ac", "merge", "0-ac"]

url = "http://aqwwiki.wikidot.com" 

with open('item_tag.json', 'r') as f:
    item_types = json.load(f)

print("Input item:")
search_item = input().lower()
search_url = search_item.replace(" ", "-")

result = requests.get(f'{url}/{search_url}')
doc = soup(result.text, "html.parser")

def item_exists():
    for p in doc.find_all('strong'):
        if "This page doesn't exist yet!" in p.get_text():
            print("Item does not exist.")
            return False
    return True

def check_item():
    if item_exists():
        print(f'Main Page: {url}/{search_url}')
        check_merge()

def inspect_page():
    page_title = doc.find(id = "page-title").get_text().replace("\n", "").strip().lower()
    page_content = doc.find(id = "page-content")

    if search_item in page_title:
        for a in page_content.find_all('a'):
            item_tag_url.append(a.get('href'))
    

def search_item_link(item_tag_url):
    for link in item_tag_url:
        part = link.split('-')[-1]
        if check_item_tag(part) or check_item_type(part):
            item_links.append(link)


def check_item_tag(link):
    if any(tag in link for tag in item_tags):
        return True
    return False
        
# should be a single method but data is from wiki
def check_item_type(link):
    if any(t in link for t in item_types):
        return True
    return False

def split_link(item_tag_url):
    for link in item_tag_url:
        parts = link.split('-')
        for part in parts:
            print(part)

def check_merge():
    for li in doc.find_all('li'):
        if "Merge the following:" in li.get_text():
            return li
    return None

def check_ac_price():
    ac_url = None
    
    for link in item_links:
        tag = link.split("-")[-1]
        print(tag)
        if "ac" in tag:
            ac_url = f'{url}{link}'
    
    ac_page = requests.get(ac_url)
    doc = soup(ac_page.text, "html.parser")
    page_content = doc.find(id = "page-content")
    ac_price = [p for p in page_content.find_all("p") if "Price:" in p.get_text()]
   
    for p in ac_price:
        text = p.get_text()
        match = re.search(r"\d+\s*AC", text)
        if match:
            return match.group(1)


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

is_quest = False
is_ac = False

check_item() 
inspect_page()
search_item_link(item_tag_url)
for item_link in item_links:
    print(f'{url}{item_link}')



if check_merge():
    find_merge_materials()



parsed = [parse_item(item) for item in merge_items]

for item in parsed:
    print(f"Item: {item['name']}, Quantity: {item['qty']}")

for link in merge_links:
    print(f'{url}{link}')

