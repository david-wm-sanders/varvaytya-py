import csv
import pathlib

import click

from app import app, db
from app.models import World, ItemGroup, ItemDef, Realm


@app.cli.command("create-world")
@click.argument("name", default="valhalla")
@click.argument("summation_mode", default="xp+rp")
def create_world(name: str, summation_mode: str):
    print(f"Creating world '{name}' [summation_mode='{summation_mode}']...")
    world = World(name=name, summation_mode=summation_mode)
    db.session.add(world)
    db.session.commit()
    print(f"Created world '{name}' [{world.id}]!")


@app.cli.command("create-items")
@click.argument("name", required=True)
@click.argument("items_csv_path", required=True)
@click.argument("storage_width", type=int, default=10)
def create_items(name, items_csv_path, storage_width):
    print(f"Creating item group '{name}' [sw:{storage_width}] from '{items_csv_path}'...")
    items_csv_p = pathlib.Path(items_csv_path)
    if not items_csv_p.exists():
        print(f"Error: '{items_csv_path}' doesn't exist!")
        return

    items = []
    print(f"Reading '{items_csv_p}'...")
    with items_csv_p.open("r", encoding="utf-8") as csv_f:
        reader = csv.DictReader(csv_f)
        for row in reader:
            items.append((row["class"], row["index"], row["key"]))
    print(f"Read {len(items)} items!")

    print(f"Creating item group '{name}'...")
    ig = ItemGroup(name=name, storage_width=storage_width)
    db.session.add(ig)
    db.session.commit()
    print(f"Created item group '{name}' [{ig.id}]!")

    print("Constructing item definitions...")
    itemdefs = [{"item_group_id": ig.id, "id": x,
                 "cls": item[0], "dex": item[1], "key": item[2]} for x, item
                in enumerate(items)]
    print("Bulk inserting item definitions...")
    db.session.bulk_insert_mappings(ItemDef, itemdefs)
    print("Committing...")
    db.session.commit()
    print("Success!")


@app.cli.command("_delete_ig")
@click.argument("item_group_id", type=int, required=True)
def _delete_ig(item_group_id: int):
    db.session.query(ItemGroup).filter_by(id=item_group_id).delete()
    db.session.query(ItemDef).filter_by(itemgroup_id=item_group_id).delete()
    db.session.commit()


@app.cli.command("create-realm")
@click.argument("name", required=True)
@click.argument("digest", required=True)
@click.argument("itemgroup_id", type=int, required=True)
def create_realm(name, digest, item_group_id):
    r = Realm(name=name, digest=digest, itemgroup_id=item_group_id)
    db.session.add(r)
    db.session.commit()
