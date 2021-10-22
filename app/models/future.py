from datetime import datetime
from app import db


class World(db.Model):
    # worlds group realms where the realm-independent aspects of a person-profile
    # will be shared (cumulatively) across the realms within a world
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True, nullable=False)
    summation_mode = db.Column(db.String(32))


class Realm2(db.Model):
    # the realm name must be unique because, as rwr server has no concept of a world,
    # we must be able to derive the world from the realm name sent to {get,set}_profile.php
    # todo: make this Realm and get rid of classic Realm, remember to update foreign keys in other tables
    world_id = db.Column(db.Integer, db.ForeignKey("world.id"), primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True, nullable=False)
    digest = db.Column(db.String(64), nullable=False)
    itemgroup_id = db.Column(db.Integer, db.ForeignKey("item_group.id"), nullable=False)
    # accounts = db.relationship("BasicAccount", backref="realm", lazy="dynamic")


class Player(db.Model):
    # the same player can exist in multiple worlds/realms
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.Integer, unique=True, nullable=False)
    username = db.Column(db.Integer, index=True, unique=True, nullable=False)
    # sid is nullable until rwr server sends it to get_profile.php endpoint in future update
    sid = db.Column(db.Integer, index=True)
    rid = db.Column(db.String(64), nullable=False)


class Account(db.Model):
    # an account combines a person+profile in a single table
    # special magic handles summing et subtracting the accounts held by an individual
    # player in order for xp, rp, etc to be shared between the realms of a world
    world_id = db.Column(db.Integer, db.ForeignKey("world.id"), primary_key=True)
    realm_id = db.Column(db.Integer, db.ForeignKey("realm2.id"), primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), primary_key=True)

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
