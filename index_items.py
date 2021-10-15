import sys
import dataclasses
import pathlib
from xml.etree import ElementTree as XmlET

VERSION = 0.002
DEFAULT_WIN_INSTALL_PATH = pathlib.Path(r"C:\Program Files (x86)\Steam\steamapps\common\RunningWithRifles")
PACKAGE_PATH = DEFAULT_WIN_INSTALL_PATH / "media/packages"
VANILLA_PATH = PACKAGE_PATH / "vanilla"


# def ask(q: str, cls_, default=None):
#     i = input(f"> {q} ")
#     return cls_(i) if i else cls_(default)


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
    # pass


if __name__ == '__main__':
    print(f"enlistd/värväytyä item indexer ({VERSION})!")
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

    # todo: discover items in vanilla

    # ask user which package they want to index
    i = input("> Which package should be indexed? ")
    if i not in pkgs:
        print(f"Error: '{i}' is not a located package :/")
        sys.exit(3)
    pkg = pkgs[i]
    # todo: if not vanilla, ask if overlays vanilla or something else?!
    # base_package_name = None
    # if pkg.name != "vanilla":
    #     i = input("Does this seem like a bad idea? [y/Y] ")
    # todo: ask user for {prefix}all_*.*
    # todo: glob for all weapons, projectiles/throwables, et carry items in base package to make dict (name: path)
    # todo: as above for specified package, then overlay^base dict
    # todo: load {prefix}all_weapons.xml, parse as xml, get <weapon file="*.weapon"/>'s as list
    # todo: for each *.weapon, find in item_paths dict, load xml from path, find <weapon> defs in *.weapon
    # todo: add an entry to an items list (item: (class, index, key))
    # todo: repeat for throwables et carry items, populating the items list
    # todo: write out all the items to a csv itemdefs

