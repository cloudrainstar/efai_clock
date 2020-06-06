import os
import sys
from sqlalchemy import Column, Text, Boolean, BigInteger, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

PG_USER = os.environ.get("PG_USER", None)
PG_PASSWORD = os.environ.get("PG_PASSWORD", None)
PG_HOST = os.environ.get("PG_HOST", None)
PG_PORT = os.environ.get("PG_PORT", "5432")
PG_DB = os.environ.get("PG_DB", None)

# SQLAlchemy
Base = declarative_base()
if PG_USER and PG_PASSWORD and PG_HOST and PG_DB:
    engine = create_engine(
        f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    )
else:
    raise Exception("DB information missing from environmental variables.")
    sys.exit(1)
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = "users"

    userid = Column(BigInteger, primary_key=True, nullable=False)
    apollo_user = Column(Text, nullable=False)
    apollo_password = Column(Text, nullable=False)
    reminder = Column(Boolean, nullable=False, default=False)
    autolog = Column(Boolean, nullable=False, default=False)


Base.metadata.create_all(engine)


class UserQuery:
    def __init__(self, session):
        self.session = session

    def get_user(self, userid: int):
        return self.session.query(User).filter_by(userid=userid).first()

    def get_reminder(self):
        return self.session.query(User).filter_by(reminder=True)

    def get_autolog(self):
        return self.session.query(User).filter_by(autolog=True)

    def add_user(self, user: User):
        self.session.add(user)
        self.session.commit()

    def set_reminder(self, userid: int, newstate: bool):
        current_user = self.session.query(User).filter_by(userid=userid).first()
        current_user.reminder = newstate
        self.session.commit()

    def set_autolog(self, userid: int, newstate: bool):
        current_user = self.session.query(User).filter_by(userid=userid).first()
        current_user.autolog = newstate
        self.session.commit()

    def delete(self, userid: int):
        current_user = self.session.query(User).filter_by(userid=userid).first()
        self.session.delete(current_user)
        self.session.commit()

    def close(self):
        self.session.close()
