import xml.etree.ElementTree as XmlET

from app import db


class Realm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True, nullable=False)
    digest = db.Column(db.String(64), nullable=False)
    accounts = db.relationship("Account", backref="realm", lazy="dynamic")


class Account(db.Model):
    # when get_profile encounters a new username (that validates)
    # it populates hash, realm_id, username, rid and returns a sparser
    # <profile> to the game server to confirm that the account <person>
    # can be created by the server, hence these are not nullable
    # core player tag and profile tag info:
    # should hash and realm_id be the other way round? (as there are fewer realms than players)
    hash = db.Column(db.Integer, primary_key=True)
    realm_id = db.Column(db.Integer, db.ForeignKey("realm.id"), primary_key=True)
    username = db.Column(db.String(32), index=True, nullable=False)
    rid = db.Column(db.String(64), nullable=False)

    # the following columns are optional and will be populated
    # when set_profile receives data to save for the (hash, realm_id)
    # basic profile stuff:
    sid = db.Column(db.Integer, index=True)
    game_version = db.Column(db.Integer)
    squad_tag = db.Column(db.String(3))
    color = db.Column(db.String(16))
    # basic person stuff:
    max_authority_reached = db.Column(db.Float)
    authority = db.Column(db.Float)
    job_points = db.Column(db.Float)
    faction = db.Column(db.Integer)
    name = db.Column(db.String(32))
    alive = db.Column(db.Boolean)
    soldier_group_id = db.Column(db.Integer)
    soldier_group_name = db.Column(db.String(32))
    squad_size_setting = db.Column(db.Integer)
    squad_config_index = db.Column(db.Integer)
    # block info may also be irrelevant? can we just return fixed "0 0"?
    # blockx = db.Column(db.Integer)
    # blocky = db.Column(db.Integer)
    # person order info:
    # suspect these aren't relevant for player characters
    # can we just not save/return them?
    # order_moving = db.Column(db.Boolean)
    # order_target = db.Column(db.String(32))
    # order_class = db.Column(db.Integer)
    # person item info:
    item0_index = db.Column(db.Integer)
    item0_amount = db.Column(db.Integer)
    item0_key = db.Column(db.String(32))
    item1_index = db.Column(db.Integer)
    item1_amount = db.Column(db.Integer)
    item1_key = db.Column(db.String(32))
    item2_index = db.Column(db.Integer)
    item2_amount = db.Column(db.Integer)
    item2_key = db.Column(db.String(32))
    # why is item slot 3 missing?!
    item4_index = db.Column(db.Integer)
    item4_amount = db.Column(db.Integer)
    item4_key = db.Column(db.String(32))
    item5_index = db.Column(db.Integer)
    item5_amount = db.Column(db.Integer)
    item5_key = db.Column(db.String(32))
    # todo: backpack and stash stuff?
    # backpack should be binary blob up to length 255*10 bits (318.75 bytes)
    # stash should be binary blob up to length 300*10 bits (375 bytes)
    # backpack blob will consume 319 bytes but 319+375 = 694 bytes max to store full backpack and full stash contents
    # sounds alright bitstring field length could be shorter
    # 10 bits allows for 1024 different item_ids to be stored where item_id is joined with realm_id
    # to access the items table that contains the class, index, and key info for the item_id
    # profile stats info:
    kills = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    time_played = db.Column(db.Integer)
    player_kills = db.Column(db.Integer)
    teamkills = db.Column(db.Integer)
    longest_kill_streak = db.Column(db.Integer)
    targets_destroyed = db.Column(db.Integer)
    vehicles_destroyed = db.Column(db.Integer)
    soldiers_healed = db.Column(db.Integer)
    times_got_healed = db.Column(db.Integer)
    distance_moved = db.Column(db.Float)
    shots_fired = db.Column(db.Integer)
    throwables_thrown = db.Column(db.Integer)
    rank_progression = db.Column(db.Float)
    # todo: stats monitors

    def __repr__(self):
        return f"<Account [{self.realm.name}] hash={self.hash} username='{self.username}'>"

    def as_xml_data(self):
        # todo: make xml get_profile response from player
        # make data element
        data_element = XmlET.Element("data", {"ok": "1"})
        # make profile element
        profile_element = XmlET.Element("profile",
                                        {"game_version": str(self.game_version),
                                         "username": self.username,
                                         "digest": "",
                                         "sid": str(self.sid), "rid": self.rid,
                                         "squad_tag": self.squad_tag, "color": self.color})
        # make stats element
        stats_element = XmlET.Element("stats",
                                      {"kills": str(self.kills), "deaths": str(self.deaths),
                                       "time_played": str(self.time_played),
                                       "self_kills": str(self.self_kills), "teamkills": str(self.teamkills),
                                       "longest_kill_streak": str(self.longest_kill_streak),
                                       "targets_destroyed": str(self.targets_destroyed),
                                       "vehicles_destroyed": str(self.vehicles_destroyed),
                                       "soldiers_healed": str(self.soldiers_healed),
                                       "times_got_healed": str(self.times_got_healed),
                                       "distance_moved": str(self.distance_moved),
                                       "shots_fired": str(self.shots_fired),
                                       "throwables_thrown": str(self.throwables_thrown),
                                       "rank_progression": str(self.rank_progression)})
        # todo: monitors
        # adds stats element to profile element
        profile_element.append(stats_element)
        # add profile element to data element
        data_element.append(profile_element)
        # make person element
        person_element = XmlET.Element("person",
                                       {"max_authority_reached": str(self.max_authority_reached),
                                        "authority": str(self.authority), "job_points": str(self.job_points),
                                        "faction": str(self.faction), "name": self.name,
                                        "version": str(self.game_version), "alive": str(self.alive),
                                        "soldier_group_id": str(self.soldier_group_id),
                                        "soldier_group_name": self.soldier_group_name,
                                        # block here? if required xd
                                        "squad_size_setting": str(self.squad_size_setting)})
        # todo: add order element (if required... can we just fake it due to the way you spawn on join multiplayer?)
        # todo: add item elements to person
        # todo: add stash and backpack elements
        data_element.append(person_element)
        # return the player to the game server
        xml_string = XmlET.tostring(data_element, encoding="unicode")
        # print(f"{xml_string=}")
        # we return the data with a \n - otherwise rwr_server will not like it xd
        return f"{xml_string}\n"
