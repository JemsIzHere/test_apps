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

        for items in possible_items:
            suffix = self._extract_suffix(items)

            if suffix == "ac":
                ac_page = ACPage(f'{BASE_URL}{items}')
                if ac_page.is_valid():
                    ac_page.process()
                    print("Valid Page!")
                    return ac_page

            if suffix in item_tags:
                # Try MergePage first
                merge_page = MergePage(f'{BASE_URL}{items}')
                if merge_page.is_valid():
                    print("Valid Page!")
                    merge_page.process()
                    return merge_page

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

class MergePage(ItemPage):

    def __init__(self, link: str):
        super().__init__(link)      
        self.merge_name = None
        #self.materials = []         # list of { name, qty, link }
        self.gold_price = None
        self.is_parsed = False
        self._root_children: list[Material] = []

    # Might have to change validation
    def is_valid(self) -> bool:
        for li in self.doc.find_all('li'):
            if "Merge the following:" in li.get_text():
                return True
        return False
    
    def get_merge_items(self):
        merge_items = None
        for li in self.doc.find_all('li'):
            if "Merge the following" in li.get_text():
                merge_items = li
                return merge_items
        return None

    
    # Tree implementation
    def _build_item_tree(self, page_doc, visited: set) -> list[Material]:
        nodes = []
        page_content = page_doc.find(id="page-content")
        merge_section = self.get_merge_items()
        if not page_content:
            return nodes
        
        if not merge_section:
            return nodes
        
        for item_li in merge_section.find_next_siblings('li'):
            text = item_li.get_text(strip=True)

            qty_match = re.search(r'x(\d+)', text)
            quantity = int(qty_match.group(1)) if qty_match else 1
            name = re.sub(r'x\d+', '', text).strip()
            a_tag = item_li.find('a')
            link = a_tag['href'] if a_tag and a_tag.get('href') else ""

            price, price_type = self._parse_price(text)

            if name in visited:
                print(f"  [!] Circular reference detected at '{name}' — stopping.")
                continue

            children = []
            if link:
                child_url = f"{BASE_URL}{link}"
                child_result = requests.get(child_url)
                child_doc = soup(child_result.text, "html.parser")
                child_visited = visited | {name}
                children = self._build_item_tree(child_doc, child_visited)

            nodes.append(Material(
                name=name,
                quantity=quantity,
                link=link,
                price=price,
                children=children,
            ))

        return nodes

    def parse(self):
        if self.is_parsed:
            print("parsed!")
            return
        self._root_children = self._build_item_tree(self.doc, visited=set())
        self.is_parsed = True

    def _parse_price(self, text: str) -> tuple[str, str]:
        """Returns (price_display, price_type)"""
        if "N/A" in text:
            return "N/A", "n/a"
        
        ac_match = re.search(r'(\d+)\s*AC', text)
        if ac_match:
            return f"{ac_match.group(1)} AC", "ac"
        
        gold_match = re.search(r'(\d+)\s*[Gg]old', text)
        if gold_match:
            return f"{gold_match.group(1)} Gold", "gold"
        
        return "N/A", "n/a"

    def _flatten(self, nodes: list[Material]) -> list[Material]:
        result = []
        for node in nodes:
            result.append(node)
            if node.children:
                result.extend(self._flatten(node.children))
        return result

    def _consolidated(self) -> dict[str, dict]:
        totals = defaultdict(lambda: {"quantity": 0, "price": 0.0, "link": ""})
        for m in self._flatten(self._root_children):
            totals[m.name]["quantity"] += m.quantity
            totals[m.name]["price"] = m.price
            totals[m.name]["price_type"] = m.price_type
            totals[m.name]["link"] = m.link
        return totals

    def _print_tree(self, nodes: list[Material], depth: int = 0):
        for node in nodes:
            prefix = "  " * depth
            price_str = f"{node.price} AC" if node.is_purchasable() else "Quest Reward"
            print(f"{prefix}- {node.name} x{node.quantity} | {price_str} | {node.link}")
            if node.children:
                self._print_tree(node.children, depth + 1)

    # inherited
    def process(self):
        self.parse()

        print(f"\n--- Merge Tree: {self.full_url} ---")
        self._print_tree(self._root_children)

        print(f"\n--- Consolidated Materials ---")
        for name, data in self._consolidated().items():
            price_str = f"{data['price']} AC" if data["price"] > 0 else "Quest Reward"
            print(f"- {name} x{data['quantity']} | {price_str} | {data['link']}")

        consolidated = self._consolidated()
        print(f"\nTotal Unique Materials: {len(consolidated)}")
        print(f"Total Material Count:   {sum(d['quantity'] for d in consolidated.values())}")
        print(f"Total Price:            {sum(d['price'] * d['quantity'] for d in consolidated.values())} AC")

    def summary(self) -> dict:
        self.parse()
        consolidated = self._consolidated()
        return {
            'type': 'merge',
            'url': self.full_url,
            'materials': [
                {'name': n, 'quantity': d['quantity'], 'price': d['price'], 'link': d['link']}
                for n, d in consolidated.items()
            ],
            'total_unique_materials': len(consolidated),
            'total_material_count': sum(d['quantity'] for d in consolidated.values()),
            'total_price': sum(d['price'] * d['quantity'] for d in consolidated.values()),
        }

class QuestPage(ItemPage):

    def __init__(self, link: str):
        self.link = link
        self.full_url = f"{BASE_URL}{link}"
        self.doc = self._fetch()

        self.quest_name = None
        self.requirements = []  # list of { name, qty }
        self.rewards = []       # list of { name, qty }
        self.next_quest = None  # link to next quest in chain
        self.is_parsed = False

    def is_valid(self) -> bool:
        """Merge page is valid if it contains 'merge the following'."""
        return False