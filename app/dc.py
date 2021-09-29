import dataclasses
import xml.etree.ElementTree


class XmlLoadKeyError(KeyError):
    pass


class XmlLoadValueError(ValueError):
    pass


@dataclasses.dataclass
class PersonXml:
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
            raise XmlLoadKeyError() from e
        except ValueError as e:
            print(f"Person attribute value error: {e}")
            raise XmlLoadValueError() from e
        except Exception as e:
            print(f"Person attribute load failed: {e}")
            raise

        # todo: load the person items
        # todo: load the embedded order if required
        # todo: load the stash and backpack

        return cls(max_authority_reached, authority, job_points, faction,
                   name, version, alive, soldier_group_id, soldier_group_name,
                   block, squad_size_setting, squad_config_index)


@dataclasses.dataclass
class ProfileStatsXml:
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
            pass
        except KeyError as e:
            raise XmlLoadKeyError() from e
        except ValueError as e:
            print(f"ProfileStats attribute value error: {e}")
            raise XmlLoadValueError() from e
        except Exception as e:
            print(f"ProfileStats attribute load failed: {e}")
            raise


@dataclasses.dataclass
class ProfileXml:
    game_version: int
    username: str
    sid: int
    rid: str
    squad_tag: str
    # todo: color should be accessible by part floats somehow? also block?
    color: str
    stats: ProfileStatsXml

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
            raise XmlLoadKeyError() from e
        except ValueError as e:
            print(f"Profile attribute value error: {e}")
            raise XmlLoadValueError() from e
        except Exception as e:
            print(f"Profile attribute load failed: {e}")
            raise

        # todo: load profile stats
        stats_elem = element.find("stats")
        stats_xml = ProfileStatsXml.from_element(stats_elem)

        return cls(game_version, username, sid, rid, squad_tag, color,
                   stats_xml)


@dataclasses.dataclass
class PlayerXml:
    hash_: int
    rid: str
    person: PersonXml
    profile: ProfileXml

    @classmethod
    def from_element(cls, element: xml.etree.ElementTree.Element):
        x = element.attrib
        try:
            hash_ = int(x.get("hash"))
            rid = x.get("rid")
            # todo: more validation
        except KeyError as e:
            raise XmlLoadKeyError() from e
        except ValueError as e:
            print(f"Player attribute value error: {e}")
            raise XmlLoadValueError() from e
        except Exception as e:
            print(f"Player attribute load failed: {e}")
            raise

        person_elem = element.find("person")
        person_xml = PersonXml.from_element(person_elem)

        profile_elem = element.find("profile")
        profile_xml = ProfileXml.from_element(profile_elem)

        return cls(hash_=hash_, rid=rid,
                   person=person_xml, profile=profile_xml)


