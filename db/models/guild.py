from db.models.base import Base
from db.db import db


class Guild(Base):
    __tablename__ = "Guilds"

    id = db.Column(db.BigInteger, primary_key=True)
    prefix = db.Column(db.Text, default="$")
    autoreply_on = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Guild(id={self.id})>"
