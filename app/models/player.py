from datetime import datetime
from app import db


class Player(db.Model):
    # the same player can exist in multiple worlds/realms
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.Integer, unique=True, nullable=False)
    username = db.Column(db.String(32), index=True, unique=True, nullable=False)
    # sid is nullable until rwr server sends it to get_profile.php endpoint in future update
    sid = db.Column(db.Integer, index=True)
    rid = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # set up sqlalchemy ORM relationships
    accounts = db.relationship("Account", back_populates="player", lazy="dynamic")
