from db.models.base import Base
from db.db import db


class User(Base):
    __tablename__ = "Users"

    id = db.Column(db.BigInteger(), primary_key=True)
    commands_executed = db.Column(db.Integer(), default=0)

    def __repr__(self):
        return f"<User(id={self.id})>"
