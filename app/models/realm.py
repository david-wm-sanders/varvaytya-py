from datetime import datetime
from app import db


class Realm(db.Model):
    # the realm name must be unique because, as rwr server has no concept of a world,
    # we must be able to derive the world from the realm name sent to {get,set}_profile.php
    id = db.Column(db.Integer, primary_key=True)
    world_id = db.Column(db.Integer, db.ForeignKey("world.id"))
    name = db.Column(db.String(32), index=True, unique=True, nullable=False)
    digest = db.Column(db.String(64), nullable=False)
    item_group_id = db.Column(db.Integer, db.ForeignKey("item_group.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # set up sqlalchemy ORM relationships
    world = db.relationship("World", back_populates="realms")
    accounts = db.relationship("Account", back_populates="realm", lazy="dynamic")
