from db.models.base import Base
from db.db import db


class Autoreply(Base):
    __tablename__ = "Autoreplies"

    guild_id = db.Column(db.BigInteger, db.ForeignKey("Guilds.id"), primary_key=True)
    regex = db.Column(db.Text, default="", primary_key=True)
    reply = db.Column(db.Text, default="")

    def __repr__(self):
        return f"<Autoreply(regex={self.regex})>"
