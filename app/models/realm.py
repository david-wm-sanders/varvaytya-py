from app import db


class Realm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True, nullable=False)
    digest = db.Column(db.String(64), nullable=False)
    itemgroup_id = db.Column(db.Integer, db.ForeignKey("item_group.id"), nullable=False)
    accounts = db.relationship("BasicAccount", backref="realm", lazy="dynamic")
