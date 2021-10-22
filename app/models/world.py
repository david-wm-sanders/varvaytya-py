from datetime import datetime
from app import db


class World(db.Model):
    # worlds group realms where the realm-independent aspects of a person-profile
    # will be shared (cumulatively) across the realms within a world
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True, nullable=False)
    summation_mode = db.Column(db.String(16))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # set up some sqlalchemy ORM relationships
    realms = db.relationship("Realm", backref="world", lazy="dynamic")
