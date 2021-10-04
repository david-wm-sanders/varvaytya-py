import xml.etree.ElementTree as XmlET

from flask import request

from app import app, db
from app.models import Player
from app.exc import EnlistdValidationError, DigestNotSupportedError, GetMissingArgError, \
                    HashNotIntError, RealmNotFoundError, RealmDigestIncorrectError, \
                    PlayerNotFoundError, RidIncorrectError
from app.util import validate_username, validate_rid, validate_realm_digest, get_realm, get_player


def _get_request_args() -> tuple[int, str, str, str, str]:
    # get the arguments
    digest = request.args.get("digest")
    hash_, username = request.args.get("hash"), request.args.get("username")
    rid = request.args.get("rid")
    realm_name, realm_digest = request.args.get("realm"), request.args.get("realm_digest")
    # validate data (and do any required conversions):
    # digest not allowed, rid only
    if digest:
        raise DigestNotSupportedError("Only rid auth is supported")
    # mandatory parameters
    if not(hash_ and username and rid and realm_name and realm_digest):
        raise GetMissingArgError(f"Missing get arg: {request.args}")
    # hash must be int, attempt conversion here
    try:
        hash_int = int(hash_)
    except ValueError as e:
        raise HashNotIntError(f"Hash '{hash_}' not convertible to int") from e
    # validate username, rid, and realm digest
    validate_username(username)
    validate_rid(rid)
    validate_realm_digest(realm_digest)
    # if no exception raised, return data
    return hash_, username, rid, realm_name, realm_digest


def _create_player(realm_id: int, hash_: int, username: str, rid: str):
    player = Player(hash=hash_, realm_id=realm_id, username=username, rid=rid)
    db.session.add(player)
    db.session.commit()
    # make the init profile for the game server
    init_profile = f"""<profile username="{username}" digest="" rid="{rid}" />"""
    return f"""<data ok="1">{init_profile}</data>\n"""


def _as_xml_data(player: Player) -> str:
    pass


@app.route("/get_profile.php")
def get_profile():
    print(f"get_profile req args: {request.args}")

    hash_, username, rid, realm_name, realm_digest = None, None, None, None, None
    realm, player = None, None
    try:
        hash_, username, rid, realm_name, realm_digest = _get_request_args()
        realm = get_realm(realm_name, realm_digest)
        player = get_player(realm.id, hash_, rid)
        # todo: make xml get_profile response from player
        # make data element
        data_element = XmlET.Element("data", {"ok": "1"})
        # make profile element
        profile_element = XmlET.Element("profile",
                                        {"game_version": str(player.game_version),
                                         "username": player.username,
                                         "digest": "",
                                         "sid": str(player.sid), "rid": player.rid,
                                         "squad_tag": player.squad_tag, "color": player.color})
        # make stats element
        stats_element = XmlET.Element("stats",
                                      {"kills": str(player.kills), "deaths": str(player.deaths),
                                       "time_played": str(player.time_played),
                                       "player_kills": str(player.player_kills), "teamkills": str(player.teamkills),
                                       "longest_kill_streak": str(player.longest_kill_streak),
                                       "targets_destroyed": str(player.targets_destroyed),
                                       "vehicles_destroyed": str(player.vehicles_destroyed),
                                       "soldiers_healed": str(player.soldiers_healed),
                                       "times_got_healed": str(player.times_got_healed),
                                       "distance_moved": str(player.distance_moved),
                                       "shots_fired": str(player.shots_fired),
                                       "throwables_thrown": str(player.throwables_thrown),
                                       "rank_progression": str(player.rank_progression)})
        # todo: monitors
        # adds stats element to profile element
        profile_element.append(stats_element)
        # add profile element to data element
        data_element.append(profile_element)
        # make person element
        person_element = XmlET.Element("person",
                                       {"max_authority_reached": str(player.max_authority_reached),
                                        "authority": str(player.authority), "job_points": str(player.job_points),
                                        "faction": str(player.faction), "name": str(player.name),
                                        "version": str(player.game_version), "alive": str(player.alive),
                                        "soldier_group_id": str(player.soldier_group_id),
                                        "soldier_group_name": str(player.soldier_group_name),
                                        # block here? if required xd
                                        "squad_size_setting": str(player.squad_size_setting)})
        # todo: add order element (if required... can we just fake it due to the way you spawn on join multiplayer?)
        # todo: add item elements to person
        # todo: add stash and backpack elements
        data_element.append(person_element)
        # return the player to the game server
        xml_string = XmlET.tostring(data_element, encoding="unicode")
        print(f"{xml_string=}")
        return f"{xml_string}\n"
        # todo: return the player
    except PlayerNotFoundError as e:
        # player not found, create and return init profile data
        print(f"Creating new player (hash={hash_}, username='{username}') in '{realm_name}'...")
        return _create_player(realm.id, hash_, username, rid)
    except (EnlistdValidationError, RealmNotFoundError,
            RealmDigestIncorrectError, RidIncorrectError) as e:
        # return fail response mit exception issue
        return f"""<data ok="0" issue="{e.issue}"></data>\n"""
