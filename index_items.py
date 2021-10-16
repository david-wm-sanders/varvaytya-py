import sys
import dataclasses
import pathlib
from xml.etree import ElementTree as XmlET

VERSION = 0.002
DEFAULT_WIN_INSTALL_PATH = pathlib.Path(r"C:\Program Files (x86)\Steam\steamapps\common\RunningWithRifles")
PACKAGE_PATH = DEFAULT_WIN_INSTALL_PATH / "media/packages"
VANILLA_PATH = PACKAGE_PATH / "vanilla"


def _get_pkgs_path() -> pathlib.Path:
    # todo: make crossplatform, check other locations?
    if PACKAGE_PATH.exists():
        return PACKAGE_PATH
    else:
        # couldn't find media/packages at default location, ask user
        i = input("> media/packages path: ")
        return pathlib.Path(i)


@dataclasses.dataclass
class Package:
    name: str
    path: pathlib.Path


def _find_pkgs(pkg_path: pathlib.Path) -> dict[str, Package]:
    packages = {}
    for p in [f for f in pkg_path.iterdir() if f.is_dir()]:
        # look for package config
        pkg_cfg = p / "package_config.xml"
        if pkg_cfg.exists():
            packages[p.name] = Package(p.name, p)
    return packages


def _discover_items(pkg_path: pathlib.Path) -> tuple[dict[str, pathlib.Path],
                                                     dict[str, pathlib.Path],
                                                     dict[str, pathlib.Path]]:
    _w, _t, _c = {}, {}, {}
    weapons_path = pkg_path / "weapons"
    # discover weapons
    for weapon_path in weapons_path.rglob("*.weapon"):
        if (name := weapon_path.name) not in _w:
            _w[name] = weapon_path
        else:
            print(f"Warning: weapon '{name}' already discovered, duplicates?! ('{weapon_path}')")
    # discover projectiles
    for projectile_path in weapons_path.rglob("*.projectile"):
        if (name := projectile_path.name) not in _t:
            _t[name] = projectile_path
        else:
            print(f"Warning: projectile '{name}' already discovered, duplicates?! ('{projectile_path}')")
    # discover carry items
    items_path = pkg_path / "items"
    for carryitem_path in items_path.rglob("*.carry_item"):
        if (name := carryitem_path.name) not in _c:
            _c[name] = carryitem_path
        else:
            print(f"Warning: carryitem '{name}' already discovered, duplicates?! ('{carryitem_path}')")
    return _w, _t, _c


if __name__ == '__main__':
    print(f"enlistd/värväytyä item indexer ({VERSION})!")
    # get the packages path, will ask user if none of the default paths exist
    pkgs_path = _get_pkgs_path()
    if not pkgs_path.exists() and pkgs_path.is_dir():
        print(f"Error: directory '{pkgs_path}' not found :/")
        sys.exit(1)

    print(f"Finding packages in '{pkgs_path}'...")
    pkgs = _find_pkgs(pkgs_path)
    if len(pkgs) == 0:
        print(f"Error: no packages found in '{pkgs_path}' :/")
        sys.exit(2)
    print(f"Located {len(pkgs)} packages: {', '.join(name for name in pkgs.keys())}")

    # discover items in vanilla
    # most packages overlay vanilla so we discover items from it early
    print(f"Discovering vanilla items...")
    vw_paths, vt_paths, vc_paths = _discover_items(VANILLA_PATH)
    print(f"Found {len(vw_paths)} weapon, {len(vt_paths)} projectile, and {len(vc_paths)} carry item paths.")

    # ask user which package they want to index
    ow_paths, ot_paths, oc_paths = {}, {}, {}
    i = input("> Which package should be indexed? ")
    if i not in pkgs:
        print(f"Error: '{i}' is not a located package :/")
        sys.exit(3)
    pkg = pkgs[i]

    # if not vanilla, we need to now discover items in the specified package
    if pkg.name != "vanilla":
        print(f"Discovering items in '{pkg.name}'...")
        ow_paths, ot_paths, oc_paths = _discover_items(pkg.path)
        print(f"Found {len(ow_paths)} weapon, {len(ot_paths)} projectile, and {len(oc_paths)} carry item paths.")

    # overlay! dict union a | b combines key:values from a & b
    # if key appears in both dicts, right-hand b wins
    weapon_paths = vw_paths | ow_paths
    projectile_paths = vt_paths | ot_paths
    carryitems_paths = vc_paths | oc_paths

    print(f"{weapon_paths=}\n{projectile_paths=}\n{carryitems_paths=}")

    # todo: ask user for {prefix}all_*.*
    # todo: load {prefix}all_weapons.xml, parse as xml, get <weapon file="*.weapon"/>'s as list
    # todo: for each *.weapon, find in item_paths dict, load xml from path, find <weapon> defs in *.weapon
    # todo: add an entry to an items list (item: (class, index, key))
    # todo: repeat for throwables et carry items, populating the items list
    # todo: write out all the items to a csv itemdefs

