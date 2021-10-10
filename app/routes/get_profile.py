import xml.etree.ElementTree as XmlET

from flask import request

from app import app, db
from app.models import Account
from app.exc import EnlistdValidationError, DigestNotSupportedError, GetMissingArgError, \
                    HashNotIntError, RealmNotFoundError, RealmDigestIncorrectError, \
                    AccountNotFoundError, RidIncorrectError
from app.util import validate_username, validate_rid, validate_realm_digest, get_realm, get_account


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


def _create_account(realm_id: int, hash_: int, username: str, rid: str):
    account = Account(realm_id=realm_id, hash=hash_, username=username, rid=rid)
    db.session.add(account)
    db.session.commit()
    # make the init profile for the game server
    init_profile = f"""<profile username="{username}" digest="" rid="{rid}" />"""
    return f"""<data ok="1">{init_profile}</data>\n"""


@app.route("/get_profile.php")
def get_profile():
    print(f"get_profile req args: {request.args}")

    hash_, username, rid, realm_name, realm_digest = None, None, None, None, None
    realm, account = None, None
    try:
        hash_, username, rid, realm_name, realm_digest = _get_request_args()
        realm = get_realm(realm_name, realm_digest)
        # todo: get the realm item id map
        # todo: handle the edge case where the game server can make a 2nd get after map load, before any set
        account: Account = get_account(realm.id, hash_, rid)
        return account.as_xml_data()
    except AccountNotFoundError as e:
        # account not found, create and return init profile data
        print(f"Creating new account (hash={hash_}, username='{username}') in '{realm_name}'...")
        return _create_account(realm.id, hash_, username, rid)
    except (EnlistdValidationError, RealmNotFoundError,
            RealmDigestIncorrectError, RidIncorrectError) as e:
        # return fail response mit exception issue
        return f"""<data ok="0" issue="{e.issue}"></data>\n"""
