from app import db


class Realm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True, nullable=False)
    digest = db.Column(db.String(64), nullable=False)
    players = db.relationship("Player", backref="realm", lazy="dynamic")


class Player(db.Model):
    # when get_profile encounters a new username (that validates)
    # it populates hash, realm_id, username, rid and returns a sparser
    # <profile> to the game server to confirm that the account <person>
    # can be created by the server, hence these are not nullable
    # core player tag and profile tag info:
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
    blockx = db.Column(db.Integer)
    blocky = db.Column(db.Integer)
    # person order info:
    # suspect these aren't relevant for player characters
    # can we just not save/return them?
    order_moving = db.Column(db.Boolean)
    order_target = db.Column(db.String(32))
    order_class = db.Column(db.Integer)
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
        return f"<Player [{self.realm.name}] hash={self.hash} username='{self.username}'>"
