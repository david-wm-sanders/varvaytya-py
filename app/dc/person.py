import dataclasses
import xml.etree.ElementTree as XmlET

from .exc import XmlLoadKeyError, XmlLoadValueError


@dataclasses.dataclass
class PersonItemDc:
    slot: int
    index: int
    amount: int
    key: str

    @classmethod
    def from_element(cls, element: XmlET.Element):
        # get the variables stored in <item> attributes
        x = element.attrib
        try:
            slot = int(x.get("slot"))
            index = int(x.get("index"))
            amount = int(x.get("amount"))
            key = x.get("key")
        except KeyError as e:
            print(f"PersonItem attribute key error: {e}")
            raise XmlLoadKeyError() from e
        except ValueError as e:
            print(f"PersonItem attribute value error: {e}")
            raise XmlLoadValueError() from e
        except Exception as e:
            print(f"PersonItem attribute load failed: {e}")
            raise

        return cls(slot, index, amount, key)


@dataclasses.dataclass
class StashedItemDc:
    class_: int
    index: int
    key: str


@dataclasses.dataclass
class PersonDc:
    max_authority_reached: float
    authority: float
    job_points: float
    faction: int
    name: str
    version: int
    alive: bool
    soldier_group_id: int
    soldier_group_name: str
    block: str
    squad_size_setting: int
    squad_config_index: int
    # order: PersonOrderDc
    items: dict[int, PersonItemDc]

    @classmethod
    def from_element(cls, element: XmlET.Element):
        # get the variables stored in <person> attributes
        x = element.attrib
        try:
            max_authority_reached = float(x.get("max_authority_reached"))
            authority = float(x.get("authority"))
            job_points = float(x.get("job_points"))
            faction = int(x.get("faction"))
            name = x.get("name")
            version = int(x.get("version"))
            alive = bool(x.get("alive"))
            soldier_group_id = int(x.get("soldier_group_id"))
            soldier_group_name = x.get("soldier_group_name")
            block = x.get("block")
            squad_size_setting = int(x.get("squad_size_setting"))
            squad_config_index = int(x.get("squad_config_index")) if "squad_config_index" in x else None
        except KeyError as e:
            print(f"Person attribute key error: {e}")
            raise XmlLoadKeyError() from e
        except ValueError as e:
            print(f"Person attribute value error: {e}")
            raise XmlLoadValueError() from e
        except Exception as e:
            print(f"Person attribute load failed: {e}")
            raise

        # todo: load the person items
        items = {}
        item_elements = element.findall("item")
        # todo: validate len(item_elements) == 5
        # print(f"{item_elements=}")
        for item_element in item_elements:
            item = PersonItemDc.from_element(item_element)
            items[item.slot] = item
        # todo: load the embedded order if required
        # todo: load the stash and backpack

        return cls(max_authority_reached, authority, job_points, faction,
                   name, version, alive, soldier_group_id, soldier_group_name,
                   block, squad_size_setting, squad_config_index, items)
