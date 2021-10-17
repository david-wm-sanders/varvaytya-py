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

    # add special sauce
    # if experimental things exist, add them as they might be referenced
    if (ewp := weapons_path / "experimental_weapons.xml").exists():
        _w["experimental_weapons.xml"] = ewp
    if (etp := weapons_path / "experimental_projectiles.xml").exists():
        _t["experimental_projectiles.xml"] = etp
    # add all_throwables.xml as invasion references it
    if (etp := weapons_path / "all_throwables.xml").exists():
        _t["all_throwables.xml"] = etp
    return _w, _t, _c


def _load_xml(xml_path: pathlib.Path, tag: str, file_map: dict[str, pathlib.Path], _loaded=None):
    # keep track of loaded keys so we can avoid yielding duplicates, even if there are dupes in source xml
    loaded = set() if _loaded is None else _loaded
    xml_str = xml_path.read_text(encoding="utf-8")
    try:
        xmlet = XmlET.fromstring(xml_str)
    except XmlET.ParseError as e:
        print(f"Error: {e} for '{xml_path.name}', skipped!")
        # if the file is unloaded as XML (i.e. we have encountered a ParseError^)
        # return early to stop iteration
        return
    if xmlet.tag == f"{tag}s":
        # handle list form: weapons | projectiles | carry_items
        tag_s = xmlet.findall(f"./{tag}")
        for t in tag_s:
            if "file" in t.attrib:
                # handle <weapon file="?" />
                f = t.attrib["file"]
                fp = file_map.get(f, None)
                if fp:
                    yield from _load_xml(fp, tag, file_map, _loaded=loaded)
                else:
                    print(f"Warning: file ref '{f}' not discovered (i.e. not in file map), ignored...")
            elif "key" in t.attrib:
                # handle <weapon key="?" ... >...</
                key = t.attrib["key"]
                if key not in loaded:
                    loaded.add(key)
                    yield key
                else:
                    print(f"Warning: key '{key}' already loaded, skipping...")
            else:
                print(f"Warning: couldn't find required attribute in {t.attrib} of {t}, ignored...")
    elif xmlet.tag == tag:
        # handle singular (weapon | projectile | carry_item) root tag
        if "key" in xmlet.attrib:
            # yield xmlet.attrib["key"]
            key = xmlet.attrib["key"]
            if key not in loaded:
                loaded.add(key)
                yield key
            else:
                print(f"Warning: key '{key}' already loaded, skipping...")
        else:
            print(f"Warning: no key in <weapon> loaded from '{xml_path}', ignored...")
    else:
        print(f"Warning: root tag '{xmlet.tag}' doesn't match '{tag}(s)', ignored...")


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
    i = input("> Which package should be indexed? [default: invasion] ")
    i = i if i else "invasion"
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
    # print(f"{weapon_paths=}\n{projectile_paths=}\n{carryitems_paths=}")

    # ask user if there is a {prefix}all_*.*
    # _prefix_default = f"{pkg.name}_"
    # _prefix = input(f"> [prefix?]all_{{weapons,throwables,carry_items}}.xml, [default: {_prefix_default}]: ")
    prefix = input(f"> [prefix?]all_{{weapons,throwables,carry_items}}.xml, default none: ")
    # print(f"{prefix=}")
    # todo: fix this hack for dev
    # prefix = _prefix if _prefix else _prefix_default

    # load {prefix}all_weapons.xml, parse as xml, extract a list of weapon keys
    all_weapons_xml_path = pkg.path / f"weapons/{prefix}all_weapons.xml"
    if not all_weapons_xml_path.exists():
        print(f"Error: '{all_weapons_xml_path}' doesn't exist :/")
        sys.exit(4)
    print(f"Loading '{all_weapons_xml_path}'...")
    all_weapons = list(_load_xml(all_weapons_xml_path, "weapon", weapon_paths))
    for i, weapon in enumerate(all_weapons):
        print(f"weapon index {i}: {weapon}")

    # load {prefix}all_throwables.xml, parse as xml, extract a list of projectile keys
    all_projectiles_xml_path = pkg.path / f"weapons/{prefix}all_throwables.xml"
    if not all_projectiles_xml_path.exists():
        print(f"Error: '{all_projectiles_xml_path}' doesn't exist :/")
        sys.exit(5)
    print(f"Loading '{all_projectiles_xml_path}'...")
    all_projectiles = list(_load_xml(all_projectiles_xml_path, "projectile", projectile_paths))
    for i, projectile in enumerate(all_projectiles, 50):
        print(f"projectile index {i}: {projectile}")

    # load {prefix}all_carry_items.xml, parse as xml, extract a list of carry_item keys
    all_carryitems_xml_path = pkg.path / f"items/{prefix}all_carry_items.xml"
    if not all_carryitems_xml_path.exists():
        print(f"Error: '{all_carryitems_xml_path}' doesn't exist :/")
        all_carryitems_xml_path = VANILLA_PATH / f"items/{prefix}all_carry_items.xml"
        if not all_carryitems_xml_path.exists():
            print(f"Error: '{all_carryitems_xml_path}' doesn't exist :/")
            sys.exit(6)
    print(f"Loading '{all_carryitems_xml_path}'...")
    all_carryitems = list(_load_xml(all_carryitems_xml_path, "carry_item", carryitems_paths))
    for i, carryitem in enumerate(all_carryitems):
        print(f"carryitem index {i}: {carryitem}")

    # todo: write out all the items to a csv itemdefs

