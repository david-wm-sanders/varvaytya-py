import dataclasses
import xml.etree.ElementTree as XmlET

from .exc import XmlLoadKeyError, XmlLoadValueError


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
    def from_element(cls, element: XmlET.Element):
        # get the variables stored in <stats> attributes
        x = element.attrib
        try:
            kills = int(x.get("kills"))
            deaths = int(x.get("deaths"))
            # print(f"tp={x.get('time_played', None)}")
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
    def from_element(cls, element: XmlET.Element):
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
