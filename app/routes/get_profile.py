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
        # todo: get the realm item id map
        # todo: handle the edge case where the game server can make a 2nd get after map load, before any set
        player: Player = get_player(realm.id, hash_, rid)
        return player.as_xml_data()
    except PlayerNotFoundError as e:
        # player not found, create and return init profile data
        print(f"Creating new player (hash={hash_}, username='{username}') in '{realm_name}'...")
        return _create_player(realm.id, hash_, username, rid)
    except (EnlistdValidationError, RealmNotFoundError,
            RealmDigestIncorrectError, RidIncorrectError) as e:
        # return fail response mit exception issue
        return f"""<data ok="0" issue="{e.issue}"></data>\n"""
