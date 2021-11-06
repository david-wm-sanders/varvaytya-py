from datetime import datetime
from xml.etree import ElementTree as XmlET

from app import db


class Account(db.Model):
    # an account combines a person+profile in a single table
    # special magic handles summing et subtracting the accounts held by an individual
    # player in order for xp, rp, etc to be shared between the realms of a world
    realm_id = db.Column(db.Integer, db.ForeignKey("realm.id"), primary_key=True)
    realm = db.relationship("Realm", back_populates="accounts")

    player_hash = db.Column(db.Integer, db.ForeignKey("player.hash"), primary_key=True)
    player = db.relationship("Player", back_populates="accounts")

    world_id = db.Column(db.Integer, db.ForeignKey("world.id"))
    world = db.relationship("World", back_populates="accounts")

    # access time related columns :clock:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_get_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_set_at = db.Column(db.DateTime)

    # the following columns are optional and will be populated
    # when set_profile receives data to save for the account
    # basic profile stuff:
    game_version = db.Column(db.Integer)
    squad_tag = db.Column(db.String(3))
    # todo: store color better?
    color = db.Column(db.String(16))
    # basic person stuff:
    max_authority_reached = db.Column(db.Float)
    authority = db.Column(db.Float)
    job_points = db.Column(db.Float)
    faction = db.Column(db.Integer)
    name = db.Column(db.String(32))
    # todo: may not even need to store alive for mp server contexts...
    alive = db.Column(db.Boolean)
    soldier_group_id = db.Column(db.Integer)
    soldier_group_name = db.Column(db.String(32))
    squad_size_setting = db.Column(db.Integer)
    # no squad config index for now :(
    # squad_config_index = db.Column(db.Integer)
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
    # perhaps remove index+key and store item{x}_item_def_id instead?
    # tradeoff of readability of the raw tables and storage efficiency?
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

    def __str__(self):
        return f"Account (world={self.world.name}, realm={self.realm.name}, username={self.player.username})"

    def as_xml_data(self):
        # make xml get_profile response from player
        # make data element
        data_element = XmlET.Element("data", {"ok": "1"})

        # handle edge case where we can receive 2nd (or more) get for account before any set
        # last_set_at will be null until the first set occurs
        if not self.last_set_at:
            # make the init profile for the game server
            profile_element = XmlET.Element("profile", {"username": self.player.username,
                                                        "rid": self.player.rid})
            data_element.append(profile_element)
            xml_string = XmlET.tostring(data_element, encoding="unicode")
            # we return the data with a \n - otherwise rwr_server will not like it xd
            return f"{xml_string}\n"

        # make full profile element
        profile_element = XmlET.Element("profile",
                                        {"game_version": str(self.game_version),
                                         "username": self.player.username,
                                         "digest": "",
                                         "sid": str(self.player.sid), "rid": self.player.rid,
                                         "squad_tag": self.squad_tag, "color": self.color})
        # make stats element
        stats_element = XmlET.Element("stats",
                                      {"kills": str(self.kills), "deaths": str(self.deaths),
                                       "time_played": str(self.time_played),
                                       "player_kills": str(self.player_kills), "teamkills": str(self.teamkills),
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
        # insert stats element into profile element
        profile_element.append(stats_element)
        # insert profile element into data element
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
        # make active equipment item elements and insert them into person element
        i0 = XmlET.Element("item", {"slot": "0",
                                    "index": str(self.item0_index), "amount": str(self.item0_amount),
                                    "key": self.item0_key})
        i1 = XmlET.Element("item", {"slot": "1",
                                    "index": str(self.item1_index), "amount": str(self.item1_amount),
                                    "key": self.item1_key})
        i2 = XmlET.Element("item", {"slot": "2",
                                    "index": str(self.item2_index), "amount": str(self.item2_amount),
                                    "key": self.item2_key})
        i4 = XmlET.Element("item", {"slot": "4",
                                    "index": str(self.item4_index), "amount": str(self.item4_amount),
                                    "key": self.item4_key})
        i5 = XmlET.Element("item", {"slot": "5",
                                    "index": str(self.item5_index), "amount": str(self.item5_amount),
                                    "key": self.item5_key})
        person_element.extend([i0, i1, i2, i4, i5])
        # todo: add stash and backpack elements
        # insert the person element into the data element
        data_element.append(person_element)
        # return the player to the game server
        xml_string = XmlET.tostring(data_element, encoding="unicode")
        # print(f"{xml_string=}")
        # we return the data with a \n - otherwise rwr_server will not like it xd
        return f"{xml_string}\n"


# todo: idea!: split apart world (realm independent) and realm dependent (items etc)
# class BasicAccount(db.Model):
#     # when get_profile encounters a new username (that validates)
#     # it populates hash, realm_id, username, rid and returns a sparser
#     # <profile> to the game server to confirm that the account <person>
#     # can be created by the server, hence these are not nullable
#     # core player tag and profile tag info:
#     # should hash and realm_id be the other way round? (as there are fewer realms than players)
#

