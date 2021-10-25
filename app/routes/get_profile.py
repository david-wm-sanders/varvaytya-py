from datetime import datetime
import xml.etree.ElementTree as XmlET

from flask import request
from sqlalchemy.exc import NoResultFound

from app import app, db
from app.models import World, Realm, Player, Account
from app.exc import EnlistdValidationError, DigestNotSupportedError, GetMissingArgError, \
                    HashNotIntError, RealmNotFoundError, RealmDigestIncorrectError, \
                    PlayerNotFound, AccountNotFoundError, RidIncorrectError
from app.util import validate_username, validate_rid, validate_realm_digest, get_realm  # get_account


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


def get_player(hash_: int, username: str, sid: int, rid: str) -> Player:
    try:
        player = Player.query.filter_by(hash=hash_).one()
        if rid == player.rid:
            return player
        else:
            raise RidIncorrectError(f"Rid '{rid}' does not match the stored rid for '{player.username}'")
    except NoResultFound as e:
        raise PlayerNotFound(f"Player ({hash_}, {username}) not found") from e


def get_account(world_id: int, realm_id: int, player_id: int) -> Account:
    try:
        account = Account.query.filter_by(world_id=world_id, realm_id=realm_id, player_id=player_id).one()
        return account
    except NoResultFound as e:
        raise AccountNotFoundError(f"Account ({world_id}, {realm_id}, {player_id}) not found") from e


# def _create_account(realm_id: int, hash_: int, username: str, rid: str):
#     account = BasicAccount(realm_id=realm_id, hash=hash_, username=username, rid=rid)
#     db.session.add(account)
#     db.session.commit()
#     return account


def create_account(world_id: int, realm_id: int, player_id: int):
    account = Account(world_id=world_id, realm_id=realm_id, player_id=player_id)
    db.session.add(account)
    db.session.commit()
    return account


@app.route("/get_profile.php")
def get_profile():
    # todo: logging!
    print(f"get_profile req args: {request.args}")
    # get the processed+validated request args
    try:
        hash_, username, rid, realm_name, realm_digest = _get_request_args()
    except EnlistdValidationError as e:
        # todo: logging!
        print(f"Error: {e}")
        return f"""<data ok="0" issue="{e.issue}"></data>\n"""

    # get the realm, failing with issue if realm not found or realm digest doesn't match
    try:
        realm: Realm = get_realm(realm_name, realm_digest)
    except (RealmNotFoundError, RealmDigestIncorrectError) as e:
        # todo: logging!
        print(f"Error: {e}")
        return f"""<data ok="0" issue="{e.issue}"></data>\n"""

    # get the player
    try:
        # todo: hack! sid not passed and not checked here until it becomes sent
        player: Player = get_player(hash_, username, 0, rid)
    except PlayerNotFound:
        # enlist a new player!
        player = Player(hash=hash_, username=username, rid=rid)
        db.session.add(player)
        db.session.commit()
    except RidIncorrectError as e:
        # return fail response mit exception issue
        print(f"Error: {e}")
        # todo: return codes dependent on error?
        return f"""<data ok="0" issue="{e.issue}"></data>\n"""

    try:
        account: Account = get_account(realm.world_id, realm.id, player.id)
        # todo: get the realm item id map
        account.last_get_at = datetime.now()
        db.session.commit()
        # will handle the edge case where the game server can make a 2nd get after map load, before any set
        return account.as_xml_data()
    except AccountNotFoundError:
        # account not found, create and return init profile data
        print(f"Creating new account ({realm.world_id}, {realm.id}, {player.id}) "
              f"for '{username}' in '{realm_name}'...")
        # account = _create_account(realm.id, hash_, username, rid)
        account = create_account(realm.world_id, realm.id, player.id)
        return account.as_xml_data()


# @app.route("/get_profile.php")
# def get_profile():
#     print(f"get_profile req args: {request.args}")
#
#     hash_, username, rid, realm_name, realm_digest = None, None, None, None, None
#     realm, account = None, None
#     try:
#         hash_, username, rid, realm_name, realm_digest = _get_request_args()
#         realm = get_realm(realm_name, realm_digest)
#         # todo: get realm.world here
#         # todo: get the realm item id map
#         # todo: reimplement get_account
#         # account: BasicAccount = get_account(realm.id, hash_, rid)
#         account.last_get_at = datetime.now()
#         db.session.commit()
#         # will handle the edge case where the game server can make a 2nd get after map load, before any set
#         # return account.as_xml_data()
#     except AccountNotFoundError as e:
#         # account not found, create and return init profile data
#         print(f"Creating new account (hash={hash_}, username='{username}') in '{realm_name}'...")
#         # account = _create_account(realm.id, hash_, username, rid)
#         # return account.as_xml_data()
#     except (EnlistdValidationError, RealmNotFoundError,
#             RealmDigestIncorrectError, RidIncorrectError) as e:
#         # return fail response mit exception issue
#         print(f"Error: {e}")
#         # todo: return codes dependent on error?
#         return f"""<data ok="0" issue="{e.issue}"></data>\n"""
