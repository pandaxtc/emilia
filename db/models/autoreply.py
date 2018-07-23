from db.models.base import Base
from db.db import db


class Autoreply(Base):
    __tablename__ = "Autoreplies"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.BigInteger, db.ForeignKey("Guilds.id"), primary_key=True)
    pattern = db.Column(db.Text, default="")
    reply = db.Column(db.Text, default="")

    def __repr__(self):
        return f"<Autoreply(regex={self.pattern})>"
