import json
from collections import defaultdict
from scraper import ItemPage, ACItem, MergeItem, QuestItem, parse_item, BASE_URL

with open('item_tag.json', 'r') as f:
    item_types = json.load(f)

ITEM_TAGS = ["ac", "merge", "0-ac"]


class ItemFilter:

    def __init__(self):
        self.item_tags = ITEM_TAGS
        self.item_types = item_types

    def filter(self, links: list) -> list:
        return [
            link for link in links
            if self._matches(link.split('-')[-1])
        ]

    def _matches(self, part: str) -> bool:
        return (
            any(tag in part for tag in self.item_tags) or
            any(t in part for t in self.item_types)
        )
