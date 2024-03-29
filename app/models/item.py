from xml.etree import ElementTree as XmlET

from app import db


class ItemGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    storage_width = db.Column(db.Integer, nullable=False)
    items = db.relationship("ItemDef", backref="group", lazy="dynamic")


class ItemDef(db.Model):
    item_group_id = db.Column(db.Integer, db.ForeignKey("item_group.id"), primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    cls = db.Column(db.Integer, nullable=False)
    dex = db.Column(db.Integer, nullable=False)
    key = db.Column(db.String(32), nullable=False)
