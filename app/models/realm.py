from app import db


class Realm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True, nullable=False)
    digest = db.Column(db.String(64), nullable=False)
    accounts = db.relationship("Account", backref="realm", lazy="dynamic")
