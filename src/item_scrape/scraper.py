from bs4 import BeautifulSoup as soup
from collections import defaultdict
from data_loader import item_tags
from models import Material
import requests
import re

BASE_URL = "http://aqwwiki.wikidot.com" 
#ITEM_TAGS = ["ac", "merge", "0-ac"]

class ItemPage:

    def __init__(self, url: str):
        self.full_url = url
        self.doc = self._fetch()
    
    def _fetch(self):
        result = requests.get(self.full_url)
        return soup(result.text, "html.parser")
    
    # recheck for redundancy
    def fetch_item_url(self,url):
        result = requests.get(url)
        return soup(result.text, "html.parser")
    
    def exists(self) -> bool:
        for p in self.doc.find_all('strong'):
            if "This page doesn't exist yet!" in p.get_text():
                print("Item does not exist.")
                return False
        return True

    def process(self):
        raise NotImplementedError(f"{self.__class__.__name__} must implement process()")

    def summary(self) -> dict:
        raise NotImplementedError(f"{self.__class__.__name__} must implement summary()")

class ItemSearch(ItemPage):

    def __init__(self, search_item: str):
        self.search_item = search_item.lower()
        self.search_url = self.search_item.replace(" ", "-")
        super().__init__ (f"{BASE_URL}/{self.search_url}")
        self.doc = self._fetch()
        self.item_links = {}
        self.page_links = []
        self.possible_items = []
        
    def get_main_page(self) -> str:
        return self.full_url
    
    def get_links(self) -> list:
        links = []

        page_content = self.doc.find(id="page-content")

        if not page_content:
            return links

        for a in page_content.find_all('a'):
            href = a.get('href')
            if href:                         
                links.append(href)

        return links
    
    def get_possible_items(self) -> list:
        for item in self.get_links():
            part = item.split('-')[-1]            
            tag = next((t for t in item_tags if t in part), None)
            if tag:
                self.possible_items.append(item)

        return self.possible_items

    def _extract_suffix(self, link: str) -> str:
        return link.rsplit("-", 1)[-1].lower()

    def categorize_links(self) -> ItemPage:
        possible_items = self.possible_items
        #pages = [ItemPage]

        for items in possible_items:
            suffix = self._extract_suffix(items)

            if suffix == "ac":
                ac_page = ACPage(f'{BASE_URL}{items}')
                if ac_page.is_valid():
                    #print("Valid Page!")
                    ac_page.process()
                    continue

            if suffix in item_tags:
                # Try MergePage first
                merge_page = MergePage(f'{BASE_URL}{items}')
                if merge_page.is_valid():
                    merge_page.process()
                    continue

                # Try QuestPage variants
                quest_page = QuestPage(f'{BASE_URL}{items}')
                if quest_page.is_valid():
                    print("Valid Page!")
                    return quest_page
            else:
                return print("Item not found.")



    # used for debugging
    def check_links(self) -> dict:

        for link in self.get_links():
            part = link.split('-')[-1]            
            tag = next((t for t in item_tags if t in part), None)
            if tag:
                self.item_links[tag] = (f'{BASE_URL}{link}')

        return self.item_links
    
    def get_main_links(self) -> list:
        for tag,link in self.item_links.items():
            self.page_links.append(f'{tag}: {link}')
        return self.page_links

    def process(self):
            raise NotImplementedError("Use check_links() to get item pages, then call process() on each.")
    
    def summary(self) -> dict:
        return {
            'search_item': self.search_item,
            'full_url': self.full_url,
            'item_links': self.item_links,
        }

class ACPage(ItemPage):

    def __init__(self, link: str):
        super().__init__(link)
        self.link = link
        self.price = None

    def get_price(self) -> str | None:
        page_content = self.doc.find(id="page-content")
        part = self.link.split('-')[-1]
        ac_price = [p for p in page_content.find_all("p") if "Price:" in p.get_text()]
        
        if part != 'ac' :
            print('Not bought with ACs.')
            return None 

        if not page_content:
            return None
        
        for p in ac_price:
            text = p.get_text()
            match = re.search(r"(\d+)\s*AC", text)

            if "N/A" in text:
                self.price = 0
                return self.price

            if match:
                self.price = match.group(1)
                return self.price
        return None
    
    def is_valid(self) -> bool:
        price = self.get_price()
        
        if price:
            return True

        return False

    def process(self):
        price = self.get_price()
        if price == 0:
            print('AC Price: N/A')
        elif price:
            print(f'AC Link: {self.full_url}')
            print(f'AC Price: {price} AC')
        else:
            print('AC Price: 0')

    def summary(self) -> dict:
        return {
            'type': 'ac',
            'url': self.full_url,
            'price': self.price,
        }

class MaterialTree:
    def __init__(self, root: Material):
            self.root = root

    def add_prerequisite(self, parent_name: str, prereq: Material):
        parent = self.find(self.root, parent_name)
        if parent is None:
            raise ValueError(f"'{parent_name}' not found")
        parent.prerequisites.append(prereq)

    def find(self, node: Material, name: str) -> Material | None:
        if node is None:
            return None
        if node.name == name:
            return node
        for prereq in node.prerequisites:
            result = self.find(prereq, name)
            if result:
                return result
        return None

    def print_tree(self, node: Material = None, prefix="", is_last=True):
        if node is None:
            node = self.root
        connector = "" if prefix == "" else ("└── " if is_last else "├── ")
        print(f'{prefix}{connector} {node.name} x{str(node.quantity)}')
        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, prereq in enumerate(node.prerequisites):
            self.print_tree(prereq, child_prefix, i == len(node.prerequisites) - 1)

    def save_tree(self, filename="output.txt"):
        import sys
        original = sys.stdout
        with open(filename, "w", encoding="utf-8") as f:
            sys.stdout = f        # redirect print to file
            self.print_tree()
            sys.stdout = original # restore print

class MergePage(ItemPage):

    def __init__(self, link: str):
        super().__init__(link)      
        self.merge_item_name = []
        self.merge_links = []        
        self.is_parsed = False
        self.is_base_item = True

    # Might have to change validation
    def is_valid(self) -> bool:
        for li in self.doc.find_all('li'):
            if "Merge the following:" in li.get_text():
                return True
        return False
    
    # change for self.doc
    # def fetch_item_url(self,url):
    #     result = requests.get(url)
    #     return soup(result.text, "html.parser")
    
    # initial check
    def set_base_item(self, value: bool):
        self.is_base_item = value

    def format_name(self, item) -> dict:
        match = re.search(r"x(\d+)", item)
        if match:
            qty = int(match.group(1))
            name = re.sub(r"\s*x\d+", "", item).strip() 

        return {"name": name, "qty": qty}
    
    def check_merge(self, link):
        merge_link = self.fetch_item_url(link)

        for li in merge_link.find_all('li'):
            if "Merge the following:" in li.get_text():
                return li
        
        return None
    
    def add_to_merge_list(self, items):
        for item_li in items[1:]:

            a_tag = item_li.find('a')
            if a_tag:
                self.merge_links.append(f'{BASE_URL}{a_tag.get('href')}')
            
                self.merge_item_name.append(f'{item_li.get_text(strip=True)}')

    def find_merge_materials(self,link):

        merge_li = self.check_merge(link)

        if merge_li:
            
            all_items = merge_li.find_parent('ul').find_all('li')
            self.add_to_merge_list(all_items)

        else:
            return None
        
    # Tree implementation
    def set_root(self) -> Material:
        item_name = self.doc.find(id="page-title").get_text(strip=True)
        root_material = Material(name=item_name, quantity=1, link=self.full_url)

        return root_material
    
    def get_current_list(self) -> dict:
        current_list = {}

        for name, link in zip(self.merge_item_name, self.merge_links):
            current_list[name] = link
        return current_list



    def build_tree(self) -> MaterialTree:
        root_material = self.set_root()
        tree = MaterialTree(root=root_material)
        self._build_recursive(root_material)
        return tree

    def _build_recursive(self, parent: Material):

        link = self.full_url if self.is_base_item else parent.link
        self.find_merge_materials(link)
        self.set_base_item(False)

        current_list = self.get_current_list()
        self.merge_item_name.clear()
        self.merge_links.clear()

        for name,link in current_list.items():
            formatted_name = self.format_name(name)
            child = Material(name=formatted_name["name"],quantity=formatted_name["qty"], link=link) # change
            parent.prerequisites.append(child)

            if not self.is_base_item:
                child_page = MergePage(link)
                child_page._build_recursive(child)

    # inherited
    def process(self):
        print(f'Merge Link: {self.full_url}')

        print("Building Item Tree....")
        tree = self.build_tree()
        tree.print_tree()
        tree.save_tree()

    def summary(self) -> dict:
        return {
            'type': 'merge',
            'url': self.full_url
        }

class QuestPage(ItemPage):

    def __init__(self, link: str):
        super().__init__(link)  
        self.questline = []

    def is_quest_reward(self) -> bool:
        """Merge page is valid if it contains 'merge the following'."""
        return False
    
    
    # search also needs to check for apostrophes ' 
    def is_shop_item(self) -> bool:
        strong_tag = self.doc.find('strong', string='Location:')
        a_tag = strong_tag.find_next('a').get('href')

        shop_link = self.fetch_item_url(f'{BASE_URL}{a_tag}')
        breadcrumbs = shop_link.find(id='breadcrumbs')
        shops_a = breadcrumbs.find('a', string=lambda t: t and 'Shops' in t)

        page_content = shop_link.find(id='page-content')
        strong_note = page_content.find('strong', string ='Note:')
        quest_req = strong_note.next_sibling

        return bool(shops_a) and 'Must have completed the' in quest_req
    
    def is_valid(self) -> bool:
        """Merge page is valid if it contains 'merge the following'."""
        return False
    

    # inherited
    def process(self):
        print(f'Quest Link: {self.full_url}')
        print("Quest valid!")
        #validate

    def summary(self) -> dict:
        return {
            'type': 'quest',
            'url': self.full_url
        }