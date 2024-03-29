from datetime import datetime
from app import db


class World(db.Model):
    # worlds group realms where the realm-independent aspects of a person-profile
    # will be shared (cumulatively) across the realms within a world
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True, nullable=False)
    summation_mode = db.Column(db.String(16))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # set up sqlalchemy ORM relationships
    realms = db.relationship("Realm", back_populates="world", lazy="dynamic")
    accounts = db.relationship("Account", back_populates="world", lazy="dynamic")

    def __str__(self):
        return f"world '{self.name}' ({self.id}) [summation_mode: {self.summation_mode}]"
