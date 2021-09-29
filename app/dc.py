import dataclasses
import xml.etree.ElementTree


class XmlLoadKeyError(KeyError):
    pass


class XmlLoadValueError(ValueError):
    pass


@dataclasses.dataclass
class PersonItemDc:
    slot: int
    index: int
    amount: int
    key: str

    @classmethod
    def from_element(cls, element: xml.etree.ElementTree.Element):
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
    def from_element(cls, element: xml.etree.ElementTree.Element):
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
        print(f"{item_elements=}")
        for item_element in item_elements:
            item = PersonItemDc.from_element(item_element)
            items[item.slot] = item
        # todo: load the embedded order if required
        # todo: load the stash and backpack

        return cls(max_authority_reached, authority, job_points, faction,
                   name, version, alive, soldier_group_id, soldier_group_name,
                   block, squad_size_setting, squad_config_index, items)


@dataclasses.dataclass
class ProfileStatsDc:
    kills: int
    deaths: int
    time_played: int
    player_kills: int
    teamkills: int
    longest_kill_streak: int
    targets_destroyed: int
    vehicles_destroyed: int
    soldiers_healed: int
    times_got_healed: int
    distance_moved: float
    shots_fired: int
    throwables_thrown: int
    rank_progression: float
    # todo: stats monitors

    @classmethod
    def from_element(cls, element: xml.etree.ElementTree.Element):
        # get the variables stored in <stats> attributes
        x = element.attrib
        try:
            kills = int(x.get("kills"))
            deaths = int(x.get("deaths"))
            print(f"tp={x.get('time_played', None)}")
            time_played = int(float(x.get("time_played")))
            player_kills = int(x.get("player_kills"))
            teamkills = int(x.get("teamkills"))
            longest_kill_streak = int(x.get("longest_kill_streak"))
            targets_destroyed = int(x.get("targets_destroyed"))
            vehicles_destroyed = int(x.get("vehicles_destroyed"))
            soldiers_healed = int(x.get("soldiers_healed"))
            times_got_healed = int(x.get("times_got_healed"))
            distance_moved = float(x.get("distance_moved"))
            shots_fired = int(x.get("shots_fired"))
            throwables_thrown = int(x.get("throwables_thrown"))
            rank_progression = float(x.get("rank_progression"))
        except KeyError as e:
            print(f"ProfileStats attribute key error: {e}")
            raise XmlLoadKeyError() from e
        except ValueError as e:
            print(f"ProfileStats attribute value error: {e}")
            raise XmlLoadValueError() from e
        except Exception as e:
            print(f"ProfileStats attribute load failed: {e}")
            raise

        return cls(kills, deaths, time_played, player_kills, teamkills, longest_kill_streak,
                   targets_destroyed, vehicles_destroyed, soldiers_healed, times_got_healed,
                   distance_moved, shots_fired, throwables_thrown, rank_progression)


@dataclasses.dataclass
class ProfileDc:
    game_version: int
    username: str
    sid: int
    rid: str
    squad_tag: str
    # todo: color should be accessible by part floats somehow? also block?
    color: str
    stats: ProfileStatsDc

    @classmethod
    def from_element(cls, element: xml.etree.ElementTree.Element):
        x = element.attrib
        try:
            game_version = int(x.get("game_version"))
            username = x.get("username")
            sid = int(x.get("sid"))
            rid = x.get("rid")
            squad_tag = x.get("squad_tag")
            color = x.get("color")
        except KeyError as e:
            print(f"Profile attribute key error: {e}")
            raise XmlLoadKeyError() from e
        except ValueError as e:
            print(f"Profile attribute value error: {e}")
            raise XmlLoadValueError() from e
        except Exception as e:
            print(f"Profile attribute load failed: {e}")
            raise

        # todo: load profile stats
        stats_elem = element.find("stats")
        stats = ProfileStatsDc.from_element(stats_elem)

        return cls(game_version, username, sid, rid, squad_tag, color, stats)


@dataclasses.dataclass
class PlayerDc:
    hash_: int
    rid: str
    person: PersonDc
    profile: ProfileDc

    @classmethod
    def from_element(cls, element: xml.etree.ElementTree.Element):
        x = element.attrib
        try:
            hash_ = int(x.get("hash"))
            rid = x.get("rid")
            # todo: more validation
        except KeyError as e:
            print(f"Player attribute key error: {e}")
            raise XmlLoadKeyError() from e
        except ValueError as e:
            print(f"Player attribute value error: {e}")
            raise XmlLoadValueError() from e
        except Exception as e:
            print(f"Player attribute load failed: {e}")
            raise

        person_elem = element.find("person")
        person = PersonDc.from_element(person_elem)

        profile_elem = element.find("profile")
        profile = ProfileDc.from_element(profile_elem)

        return cls(hash_=hash_, rid=rid, person=person, profile=profile)


