import re
from sqlalchemy.exc import NoResultFound

from app.exc import UsernameTooLongError, UsernameFormatError, RidLengthError, RidNotHexError, RealmDigestLengthError, \
    RealmDigestNotHexError, RealmDigestIncorrectError, RealmNotFoundError, RidIncorrectError, \
    PlayerNotFound, AccountNotFoundError
from app.models import Realm, Player, Account


def validate_username(username: str):
    if len(username) > 32:
        raise UsernameTooLongError(f"Username '{username}' length > 32 characters")
    if re.match(r"\s", username):
        raise UsernameFormatError(f"Username '{username}' can't begin with whitespace")
    # todo: check against blacklist?


def validate_rid(rid: str):
    # check the length of the rid
    if i := len(rid) != 64:
        # print(f"get profile error: rid '{rid}' not 64 characters long")
        # return """<data ok="0" issue="evil rid length"></data>\n"""
        raise RidLengthError(f"Rid '{rid}' length {i} != 64")
    # check the rid is a hexadecimal string
    try:
        h = int(rid, 16)
    except ValueError as e:
        raise RidNotHexError(f"Rid '{rid}' contains non-hex") from e


def validate_realm_digest(realm_digest: str):
    # check the length of the realm digest
    if i := len(realm_digest) != 64:
        raise RealmDigestLengthError(f"Realm digest '{realm_digest}' length {i} != 64")
    # check the rid is a hexadecimal string
    try:
        h = int(realm_digest, 16)
    except ValueError as e:
        raise RealmDigestNotHexError(f"Realm digest '{realm_digest}' contains non-hex") from e


def get_realm(realm_name: str, realm_digest: str) -> Realm:
    try:
        realm = Realm.query.filter_by(name=realm_name).one()
        # todo: make consistent time?
        if realm_digest == realm.digest:
            return realm
        else:
            raise RealmDigestIncorrectError(f"Realm digest '{realm_digest}' incorrect for '{realm_name}'")
    except NoResultFound as e:
        raise RealmNotFoundError(f"Realm '{realm_name}' doesn't exist") from e


# todo: change get_* to use session.get
def get_player(hash_: int, username: str, sid: int, rid: str) -> Player:
    try:
        # todo: the hash will need to be the primary key for session.get(Player, hash_) to work
        # player = Player.query.filter_by(hash=hash_).one()
        player = db.session.get(Player, hash_)
        if rid == player.rid:
            return player
        else:
            raise RidIncorrectError(f"Rid '{rid}' does not match the stored rid for '{player.username}'")
    except NoResultFound as e:
        raise PlayerNotFound(f"Player ({hash_}, {username}) not found") from e


def get_account(realm_id: int, player_id: int) -> Account:
    try:
        account = Account.query.filter_by(realm_id=realm_id, player_id=player_id).one()
        return account
    except NoResultFound as e:
        raise AccountNotFoundError(f"Account ({realm_id}, {player_id}) not found") from e
