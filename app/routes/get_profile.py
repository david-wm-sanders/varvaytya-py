from datetime import datetime
# import xml.etree.ElementTree as XmlET

from flask import request
# from sqlalchemy.exc import NoResultFound

from app import app, db
from app.models import World, Realm, Player, Account
from app.exc import VarvaytyaValidationError, DigestNotSupportedError, GetMissingArgError, \
                    HashNotIntError, RealmNotFoundError, RealmDigestIncorrectError, \
                    PlayerNotFound, AccountNotFoundError, RidIncorrectError
from app.util import validate_username, validate_rid, validate_realm_digest, \
                     get_realm, get_player, get_account
from app.util import ALERT_LVL

from loguru import logger


def _validate_get_request_args() -> tuple[int, str, str, str, str]:
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
    return hash_int, username, rid, realm_name, realm_digest


# def _create_account(realm_id: int, player_hash: int, world_id: int):
#     account = Account(realm_id=realm_id, player_hash=player_hash, world_id=world_id)
#     db.session.add(account)
#     # remove commit, the caller is expected to commit (with or without other additions or changes)
#     # db.session.commit()
#     return account


@app.route("/get_profile.php")
def get_profile():
    logger.info(f"[get] Processing request from '{request.remote_addr}'...")
    _request_args = ",".join(f"{k}={v}" for k, v in request.args.items() if k not in ["digest", "rid"])
    logger.debug(f"[get] request args: {_request_args}")
    # get the processed+validated request args
    try:
        logger.debug("[get] Validating request args...")
        hash_, username, rid, realm_name, realm_digest = _validate_get_request_args()
    except VarvaytyaValidationError as e:
        logger.log(ALERT_LVL.name, f"[get] {e}")
        return f"""<data ok="0" issue="{e.issue}"></data>\n"""

    # get the realm, failing with issue if realm not found or realm digest doesn't match
    try:
        logger.debug(f"[get] Locating realm '{realm_name}' and checking digest...")
        realm: Realm = get_realm(realm_name, realm_digest)
        logger.debug(f"[get] Realm: {realm}")
    except (RealmNotFoundError, RealmDigestIncorrectError) as e:
        logger.log(ALERT_LVL.name, f"[get] {e}")
        return f"""<data ok="0" issue="{e.issue}"></data>\n"""

    # get the player
    try:
        logger.debug(f"[get] Identifying player '{username}' [{hash_}] and checking papers (rid/sid)...")
        # todo: hack! sid not passed and not checked here until it becomes sent
        player: Player = get_player(hash_, username, 0, rid)
        logger.debug(f"[get] Player: {player}")
    except PlayerNotFound:
        # enlist a new player!
        logger.info(f"[get] Player '{username}' [{hash_}] not found, enlisting...")
        player = Player(hash=hash_, username=username, rid=rid)
        db.session.add(player)
        # if player is newly enlisted no accounts will exist for them,
        # thus we quickly create their first account here
        # and return the init profile for it
        # todo: gonna need to rework init profile handling to fake it if we are sending some world-summed data
        logger.info(f"[get] Creating new account ({realm.id}, {player.hash}) "
                    f"for '{username}' in '{realm_name}'...")
        account = Account(realm_id=realm.id, player_hash=player.hash, world_id=realm.world_id)
        db.session.add(account)
        db.session.commit()
        logger.debug(f"[get] Constructing xml for '{username}' in '{realm_name}' ({realm.id}, {hash_})...")
        xml_data = account.as_xml_data()
        xml_bytes = bytes(xml_data, "utf-8")
        logger.success(f"[get] Sending {len(xml_bytes)}B init profile to '{request.remote_addr}'...")
        return xml_data
    except RidIncorrectError as e:
        # return fail response mit exception issue
        logger.log(ALERT_LVL.name, f"[get] {e}")
        return f"""<data ok="0" issue="{e.issue}"></data>\n"""

    try:
        account: Account = get_account(realm.id, player.hash)
        account.last_get_at = datetime.now()
        # todo: consider should we commit here or later?
        db.session.commit()
        # todo: get the realm item id map
        # will handle the edge case where the game server can make a 2nd get after map load, before any set
        # todo: sum the player's accounts in realm.world_id
        # todo: implement account.as_dict()
        # print(account.as_dict())
        # todo: change to construct xml from dict? or pass summation info to as_xml_data??
        logger.debug(f"[get] Constructing xml for '{username}' in '{realm_name}' ({realm.id}, {hash_})...")
        xml_data = account.as_xml_data()
        xml_bytes = bytes(xml_data, "utf-8")
        logger.success(f"[get] Sending {len(xml_bytes)}B profile-person to '{request.remote_addr}'...")
        return xml_data
    except AccountNotFoundError:
        # account not found, create and return init profile data
        logger.info(f"[get] Creating new account ({realm.id}, {player.hash}) "
                    f"for '{username}' in '{realm_name}'...")
        account = Account(realm_id=realm.id, player_hash=player.hash, world_id=realm.world_id)
        db.session.add(account)
        db.session.commit()
        # todo: sum other accounts?
        # account.as_xml_data() will handle returning an init profile if account not set yet
        logger.debug(f"[get] Constructing xml for '{username}' in '{realm_name}' ({realm.id}, {hash_})...")
        xml_data = account.as_xml_data()
        xml_bytes = bytes(xml_data, "utf-8")
        logger.success(f"[get] Sending {len(xml_bytes)}B init profile to '{request.remote_addr}'...")
        return xml_data
