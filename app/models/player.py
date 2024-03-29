from datetime import datetime
from app import db


class Player(db.Model):
    # the same player can exist in multiple worlds/realms
    # make player int hash the primary key
    hash = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True, nullable=False)
    # sid is nullable until rwr server sends it to get_profile.php endpoint in future update
    sid = db.Column(db.Integer, index=True)
    rid = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # set up sqlalchemy ORM relationships
    accounts = db.relationship("Account", back_populates="player", lazy="dynamic")

    def __str__(self):
        return f"player '{self.username}' ({self.hash}) [sid: {self.sid}]"
