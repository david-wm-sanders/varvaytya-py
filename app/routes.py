import pathlib
import xml.etree.ElementTree as XmlET

from sqlalchemy.orm.exc import NoResultFound

from flask import request, abort
from app import app, db
from app.models import Realm, Player
from app.dc import PlayerDc


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
    # print(f"{data}")
    # hack: output data here during debugging
    # (pathlib.Path(__file__).parent / "data.xml").write_text(data, encoding="utf-8")
    data_xml = XmlET.fromstring(data)
    player_elements = data_xml.findall("./player")
    # todo: check to make sure we have some data here
    # print(f"{players=}")
    updated_players = []
    for player_elem in player_elements:
        playerdc = PlayerDc.from_element(player_elem)

        # check hash in db for realm and rid matches for hash
        try:
            player = Player.query.filter_by(hash=playerdc.hash_, realm_id=realm.id).one()
        except NoResultFound as e:
            # this player doesn't exist
            print(f"set profile error: player ({realm.id}, {playerdc.hash_}) not found, won't update, skipping...")
            continue

        # print(f"{player=}")

        # more validations:
        # check rid
        if playerdc.rid != player.rid:
            print(f"set profile error: player ({realm.id}, {playerdc.hash_}) evil rid")
            continue
        # todo: check steam id
        # issue: sid not set at get, sent first time in a set_profile, will be null/None
        # need to check this and skip if None
        # if playerdc.profile.sid != player.sid:
        #     # print(f"set profile error: player ({realm.id}, {playerdc.hash_}) sid mismatch")
        #     continue

        # create a player mapping for bulk_insert_mappings?
        # we need to specify hash and realm_id because they constitute the primary key
        # we can omit rid because it should stay constant?
        # and the rid check should already have identified a problem with this player set spec
        # we omit username because it was already set by the get and should be immutable
        # we must "update" the sid because it is not specified in the original get
        # i.e. this could be the first set for a specific profile
        i = playerdc.person.items
        item0, item1, item2, item4, item5 = i[0], i[1], i[2], i[4], i[5]
        s = playerdc.profile.stats
        pm = dict(hash=playerdc.hash_, realm_id=realm.id,
                  # basic profile stuff
                  sid=playerdc.profile.sid, game_version=playerdc.profile.game_version,
                  squad_tag=playerdc.profile.squad_tag, color=playerdc.profile.color,
                  # basic person stuff
                  max_authority_reached=playerdc.person.max_authority_reached,
                  authority=playerdc.person.authority, job_points=playerdc.person.job_points,
                  faction=playerdc.person.faction, name=playerdc.person.name, alive=playerdc.person.alive,
                  soldier_group_id=playerdc.person.soldier_group_id,
                  soldier_group_name=playerdc.person.soldier_group_name,
                  squad_size_setting=playerdc.person.squad_size_setting,
                  squad_config_index=playerdc.person.squad_config_index,
                  blockx=None, blocky=None, order_moving=None, order_target=None, order_class=None,
                  item0_index=item0.index, item0_amount=item0.amount, item0_key=item0.key,
                  item1_index=item1.index, item1_amount=item1.amount, item1_key=item1.key,
                  item2_index=item2.index, item2_amount=item2.amount, item2_key=item2.key,
                  item4_index=item4.index, item4_amount=item4.amount, item4_key=item4.key,
                  item5_index=item5.index, item5_amount=item5.amount, item5_key=item5.key,
                  # profile stats
                  kills=s.kills, deaths=s.deaths, time_played=s.time_played,
                  player_kills=s.player_kills, teamkills=s.teamkills, longest_kill_streak=s.longest_kill_streak,
                  targets_destroyed=s.targets_destroyed, vehicles_destroyed=s.vehicles_destroyed,
                  soldiers_healed=s.soldiers_healed, times_got_healed=s.times_got_healed,
                  distance_moved=s.distance_moved,
                  shots_fired=s.shots_fired, throwables_thrown=s.throwables_thrown,
                  rank_progression=s.rank_progression)

        print(f"{pm=}")
        updated_players.append(pm)

    print(f"set profile: updating {len(updated_players)} players...")
    db.session.bulk_update_mappings(Player, updated_players)
    print(f"set profile: committing updates...")
    db.session.commit()

    return ""

