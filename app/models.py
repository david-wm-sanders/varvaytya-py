from app import db


class Realm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True)
    digest = db.Column(db.String(64))


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.Integer, index=True, unique=True)
    username = db.Column(db.String(32), index=True, unique=True)
    rid = db.Column(db.String(64))

    def __repr__(self):
        return f"<Player [{self.id}] hash={self.hash} username='{self.username}'>"
