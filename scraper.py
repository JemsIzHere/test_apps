from bs4 import BeautifulSoup as soup
import requests
import re

BASE_URL = "http://aqwwiki.wikidot.com" 
ITEM_TAGS = ["ac", "merge", "0-ac"]

class ItemPage:

    def __init__(self, search_item: str):
        self.search_item = search_item.lower()
        self.search_url = self.search_item.replace(" ", "-")
        self.full_url = f"{BASE_URL}/{self.search_url}"
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

    # needs to categorize ac, merge, item links and prints them.
    def get_links(self) -> list:
        links = []
        #page_title = self.doc.find(id="page-title").get_text().strip().lower()
        page_content = self.doc.find(id="page-content")

        if not page_content:
            return links

        for a in page_content.find_all('a'):
            href = a.get('href')
            if href:                         
                links.append(href)

        return links


class ACItem:

    def __init__(self, link: str):
        self.link = link
        self.full_url = f"{link}"
        self.doc = self._fetch()
        self.price = None

    def _fetch(self):
        result = requests.get(self.full_url)
        return soup(result.text, "html.parser")
    
    def exists(self) -> bool:
        for p in self.doc.find_all('strong'):
            if "This page doesn't exist yet!" in p.get_text():
                return False
        return True

    def get_price(self) -> str | None:
        page_content = self.doc.find(id="page-content")
        if not page_content:
            return None

        ac_price = [p for p in page_content.find_all("p") if "Price:" in p.get_text()]
        for p in ac_price:
            match = re.search(r"(\d+)\s*AC", p.get_text())
            if match:
                self.price = match.group(1)
                return self.price
        return None

class MergeItem:

    def __init__(self, link: str):
        self.link = link
        self.full_url = f"{BASE_URL}{link}"
        self.doc = self._fetch()

        self.merge_name = None
        self.materials = []     # list of { name, qty, link }
        self.is_parsed = False

    def _fetch(self):
        result = requests.get(self.full_url)
        return soup(result.text, "html.parser")

    def exists(self) -> bool:
        for p in self.doc.find_all('strong'):
            if "This page doesn't exist yet!" in p.get_text():
                return False
        return True

class QuestItem:

    def __init__(self, link: str):
        self.link = link
        self.full_url = f"{BASE_URL}{link}"
        self.doc = self._fetch()

        self.quest_name = None
        self.requirements = []  # list of { name, qty }
        self.rewards = []       # list of { name, qty }
        self.next_quest = None  # link to next quest in chain
        self.is_parsed = False

    def _fetch(self):
        result = requests.get(self.full_url)
        return soup(result.text, "html.parser")
    
    def exists(self) -> bool:
        for p in self.doc.find_all('strong'):
            if "This page doesn't exist yet!" in p.get_text():
                return False
        return True