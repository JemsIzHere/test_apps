import json
import os

with open(os.path.join(os.path.dirname(__file__), 'item_tag.json'), 'r') as f:
    item_types = json.load(f)