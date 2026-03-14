from bs4 import BeautifulSoup as soup
from config import item_tags
import requests
import re

BASE_URL = "http://aqwwiki.wikidot.com" 
ITEM_TAGS = ["ac", "merge", "0-ac"]

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
    
    def get_main_page(self) -> str:
        return self.full_url

    def check_links(self) -> dict:

        for link in self.get_links():
            part = link.split('-')[-1]            
            tag = next((t for t in item_tags if t in part), None)
            if tag:
                self.item_links[tag] = (f'{BASE_URL}{link}')

        return self.item_links
    
    # probably be used for debugging
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
        
        if part not in ITEM_TAGS:
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
    
    def process(self):
        price = self.get_price()
        if price == 0:
            print('AC Price: N/A')
        elif price:
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
        self.materials = []         # list of { name, qty, link }
        self.gold_price = None
        self.is_parsed = False


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