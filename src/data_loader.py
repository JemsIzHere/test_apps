import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_json(filename):
    with open(os.path.join(DATA_DIR, filename), 'r') as f:
        return json.load(f)

item_tags = load_json('item_tag.json')