import csv

from app import app, db
from app.models import ItemGroup, ItemDef, Realm


# todo: write flask command to create ItemGroup - loading item defs from csv created by index_items.py
# todo: write flask command to create Realm - requiring name, digest, and itemgroup id
