import xml.etree.ElementTree as XmlET

from sqlalchemy.orm.exc import NoResultFound

from flask import request, abort
from app import app, db
from app.models import Realm, Player
from app.dc import PlayerBag


@app.route("/")
@app.route("/index")
def index():
    # todo: make it beautiful
    print(f"index request args: {request.args}")
    return "index"


@app.route("/get_profile.php")
def get_profile():
    print(f"get_profile req args: {request.args}")

    # get the arguments
    digest = request.args.get("digest")
    hash_, username = request.args.get("hash"), request.args.get("username")
    rid = request.args.get("rid")
    realm_name, realm_digest = request.args.get("realm"), request.args.get("realm_digest")

    # validate data at each step, if validation fails send <data ok=0> with issue:
    # todo: add better error logging
    # if not all required args specified, fail
    if not (hash_ and username and rid and realm_name and realm_digest):
        print("get profile error: missing arguments :/")
        return """<data ok="0" issue="missing arguments :/"></data>\n"""
    # if hash not int, fail
    try:
        hash_ = int(hash_)
    except ValueError as e:
        print(f"get profile error: hash '{hash_} cannot be converted to int")
        return """<data ok="0" issue="hash not int"></data>\n"""
    # if username too long, fail
    if username and len(username) > 32:
        print(f"get profile error: username '{username}' > 32 characters")
        return """<data ok="0" issue="username too long"></data>\n"""
    # if digest supplied, fail
    if digest:
        print("get profile error: digest unsupported")
        return """<data ok="0" issue="rid auth only"></data>\n"""
    # if rid not correct length, fail
    if len(rid) != 64:
        print(f"get profile error: rid '{rid}' not 64 characters long")
        return """<data ok="0" issue="evil rid length"></data>\n"""
    # todo: check the rid is a hexadecimal string

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

    # return the player to the game server
    # todo: return the player


@app.route("/set_profile.php", methods=["POST"])
def set_profile():
    print(f"set_profile req args: {request.args}")

    realm_name, realm_digest = request.args.get("realm"), request.args.get("realm_digest")
    # check db for the specified realm name
    try:
        realm = Realm.query.filter_by(name=realm_name).one()
    except NoResultFound as e:
        # if realm doesn't exist, fail
        print(f"set profile error: realm '{realm_name}' not in realms table")
        # todo: is this the right form of error response here?
        return """<data ok="0" issue="imaginary realm xd"></data>\n"""

    # if realm digest is bad :eyes:, fail
    # todo: ensure this is constant time for security reasons?
    if realm_digest != realm.digest:
        print(f"set profile error: bad realm digest '{realm_digest}")
        return """<data ok="0" issue="indigestible"></data>\n"""

    data = next(request.form.items())[0]
    print(data)
    data_xml = XmlET.fromstring(data)
    player_elements = data_xml.findall("./player")
    # todo: check to make sure we have some data here
    # print(f"{players=}")
    for player_elem in player_elements:
        player = PlayerBag.from_element(player_elem)
        print(player)
        print(player.person)
        # hash_, rid = player.attrib["hash"], player.attrib["rid"]
        # # todo: check hash in db for realm and rid matches for hash
        # # get stuff from <person>
        # person = player.find("person")
        # p = person.attrib
        # todo: check we actually have a person
        # print(f"{person=}")
        # todo: convert these xml string attributes into their expected types
        # max_auth = p.get("max_authority_reached", None)
        # authority = p.get("authority", None)
        # job_points = p.get("job_points", None)
        # faction = p.get("faction", None)
        # name = p.get("name", None)
        # alive = p.get("alive", None)
        # soldier_group_id = p.get("soldier_group_id", None)
        # soldier_group_name = p.get("soldier_group_name", None)
        # squad_size_setting = p.get("squad_size_setting", None)
        # squad_config_index = p.get("squad_config_index", None)
        # block = p.get("block", None)

    return ""

