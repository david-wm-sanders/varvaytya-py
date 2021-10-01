import re
import xml.etree.ElementTree as XmlET
from sqlalchemy.orm.exc import NoResultFound
from flask import request, abort
from app import app, db
from app.models import Realm, Player
from app.exc import EnlistdException


class EnlistdValidationError(EnlistdException):
    pass


class DigestNotSupportedError(EnlistdValidationError):
    issue = "rid auth only"


class GetMissingArgError(EnlistdValidationError):
    issue = "missing argument(s)"


class HashNotIntError(EnlistdValidationError):
    issue = "hash not int"


class UsernameTooLongError(EnlistdValidationError):
    issue = "username too long"


class UsernameFormatError(EnlistdValidationError):
    issue = "bad username format"


class RidLengthError(EnlistdValidationError):
    issue = "bad rid length"


def _validate_username(username: str):
    if len(username) > 32:
        raise UsernameTooLongError(f"Username '{username}' length > 32 characters")
    if re.match(r"\s", username):
        raise UsernameFormatError(f"Username '{username}' can't begin with whitespace")
    # todo: check against blacklist?


def _validate_rid(rid: str):
    if i := len(rid) != 64:
        # print(f"get profile error: rid '{rid}' not 64 characters long")
        # return """<data ok="0" issue="evil rid length"></data>\n"""
        raise RidLengthError(f"Rid length {i} != 64")
    # todo: check the rid is a hexadecimal string


def _get_request_args():
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
    # validate username and rid
    _validate_username(username)
    _validate_rid(rid)


@app.route("/get_profile.php")
def get_profile():
    print(f"get_profile req args: {request.args}")

    try:
        rargs = _get_request_args()
    except EnlistdValidationError as e:
        # todo: get issue from error and return fail response mit issue
        pass
    # get the arguments
    # digest = request.args.get("digest")
    # hash_, username = request.args.get("hash"), request.args.get("username")
    # rid = request.args.get("rid")
    # realm_name, realm_digest = request.args.get("realm"), request.args.get("realm_digest")

    # validate data at each step, if validation fails send <data ok=0> with issue:
    # todo: add better error logging
    # if not all required args specified, fail
    # if not (hash_ and username and rid and realm_name and realm_digest):
    #     print("get profile error: missing arguments :/")
    #     return """<data ok="0" issue="missing arguments :/"></data>\n"""

    # check db for the specified realm name
    try:
        realm = Realm.query.filter_by(name=realm_name).one()
    except NoResultFound as e:
        # if realm doesn't exist, fail
        print(f"get profile error: realm '{realm_name}' not in realms table")
        return """<data ok="0" issue="imaginary realm xd"></data>\n"""

    # if realm digest is bad :eyes:, fail
    # todo: ensure this is constant time for security reasons?
    if realm_digest != realm.digest:
        print(f"get profile error: bad realm digest '{realm_digest}")
        return """<data ok="0" issue="indigestible"></data>\n"""

    # check db for player by (hash_, realm_id)
    realm_id = realm.id
    try:
        player = Player.query.filter_by(hash=hash_, realm_id=realm_id).one()
    except NoResultFound as e:
        # if no player, create player and return initialisation profile to game server
        print(f"Creating new player (hash={hash_}, username='{username}') in '{realm_name}'...")
        player = Player(hash=hash_, realm_id=realm_id, username=username, rid=rid)
        db.session.add(player)
        db.session.commit()
        # make the init profile for the game server
        init_profile = f"""<profile username="{username}" digest="" rid="{rid}" />"""
        return f"""<data ok="1">{init_profile}</data>\n"""

    # todo: check rid sent matches rid of player returned from db
    # todo: make xml get_profile response from player

    # return the player to the game server
    # todo: return the player
