import pathlib
from datetime import datetime
import xml.etree.ElementTree as XmlET

from sqlalchemy.orm.exc import NoResultFound
from flask import request, abort

from app import app, db
from app.models import Realm, Player, Account
from app.dc import PlayerDc
from app.exc import EnlistdValidationError, DigestNotSupportedError, GetMissingArgError, \
                    HashNotIntError, RealmNotFoundError, RealmDigestIncorrectError, \
                    PlayerNotFound, AccountNotFoundError, RidIncorrectError
from app.util import get_realm, get_player, get_account, validate_realm_digest

from loguru import logger


def _validate_set_request_args() -> tuple[str, str]:
    realm_name, realm_digest = request.args.get("realm"), request.args.get("realm_digest")
    validate_realm_digest(realm_digest)
    return realm_name, realm_digest


@app.route("/set_profile.php", methods=["POST"])
def set_profile():
    logger.debug(f"set_profile req args: {request.args}")
    # get the validated request args
    try:
        realm_name, realm_digest = _validate_set_request_args()
    except EnlistdValidationError as e:
        logger.error(f"[set] {e}")
        return f"""<data ok="0" issue="{e.issue}"></data>\n"""

    # get the realm, failing with issue if realm not found or realm digest doesn't match
    try:
        realm: Realm = get_realm(realm_name, realm_digest)
    except (RealmNotFoundError, RealmDigestIncorrectError) as e:
        logger.error(f"[set] {e}")
        return f"""<data ok="0" issue="{e.issue}"></data>\n"""

    # extract the data from the request form body zeroth item key
    data = next(request.form.items())[0]
    # print(f"{data}")
    # hack: output data here during debugging
    (pathlib.Path(__file__).parent / "data.xml").write_text(data, encoding="utf-8")
    # todo: should probably handle failures of XmlET.fromstring better :D
    data_xml = XmlET.fromstring(data)
    player_elements = data_xml.findall("./player")
    # todo: check to make sure we have some data here
    # print(f"{players=}")
    updated_accounts = []
    for player_elem in player_elements:
        playerdc = PlayerDc.from_element(player_elem)

        # get the player
        try:
            player: Player = get_player(playerdc.hash_, playerdc.profile.username,
                                        playerdc.profile.sid, playerdc.rid)
        except (PlayerNotFound, RidIncorrectError) as e:
            logger.error(f"[set] {e}")
            # todo: improve logging here - security alert on incorrect rid sent to set_profile?
            continue

        # check hash in db for realm and rid matches for hash
        try:
            account = get_account(realm.id, playerdc.hash_)
        except NoResultFound as e:
            # this account doesn't exist
            logger.error(f"[set] account ({realm.id}, {playerdc.hash_}) not found, won't update, skipping...")
            continue

        # todo: check steam id
        # issue: sid not set at get, sent first time in a set_profile, will be null/None
        # if playerdc.profile.sid != account.sid:
        #     # print(f"set profile error: account ({realm.id}, {playerdc.hash_}) sid mismatch")
        #     continue

        # create a account mapping for bulk_update_mappings
        # we need to specify (realm_id, hash) because they constitute the primary key
        # todo: the sid needs to be set for the Player, not Account now :/
        # we must "update" the sid because it is not specified in the original get
        # i.e. this could be the first set for a specific profile
        i = playerdc.person.items
        item0, item1, item2, item4, item5 = i[0], i[1], i[2], i[4], i[5]
        s = playerdc.profile.stats
        # todo: create bitstrings for backpack and stash items
        am = dict(realm_id=realm.id, player_hash=playerdc.hash_,
                  last_set_at=datetime.now(),
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
                  # blockx=None, blocky=None, order_moving=None, order_target=None, order_class=None,
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

        logger.debug(f"{am=}")
        updated_accounts.append(am)

    logger.info(f"[set] updating {len(updated_accounts)} accounts...")
    db.session.bulk_update_mappings(Account, updated_accounts)
    logger.info(f"[set] committing account updates...")
    db.session.commit()
    logger.success(f"[set] committed accounts!")

    # todo: return proper response here...
    return ""
