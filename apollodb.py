from sqlalchemy import Column, Text, Boolean, BigInteger
from sqlalchemy import create_engine, select
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLAlchemy
Base = declarative_base()
engine = create_engine('postgresql://efai_clock:apollo@192.168.5.233/efai_clock')
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'

    userid = Column(BigInteger, primary_key=True, nullable=False)
    apollo_user = Column(Text, nullable=False)
    apollo_password = Column(Text, nullable=False)
    reminder = Column(Boolean, nullable=False, default=False)
    autolog = Column(Boolean, nullable=False, default=False)
    
Base.metadata.create_all(engine)

class UserQuery():
    def __init__(self, session):
        self.session = session
    def get_user(self, userid:int):
        return self.session.query(User).filter_by(userid=userid).first()
    def get_reminder(self):
        return self.session.query(User).filter_by(reminder=True)
    def get_autolog(self):
        return self.session.query(User).filter_by(autolog=True)
    def add_user(self, user:User):
        self.session.add(user)
        self.session.commit()
    def set_reminder(self, userid:int, newstate:bool):
        current_user = self.session.query(User).filter_by(userid=userid).first()
        current_user.reminder = newstate
        self.session.commit()
    def set_autolog(self, userid:int, newstate:bool):
        current_user = self.session.query(User).filter_by(userid=userid).first()
        current_user.autolog = newstate
        self.session.commit()
    def delete(self, userid:int):
        current_user = self.session.query(User).filter_by(userid=userid).first()
        self.session.delete(current_user)
        self.session.commit()
    def close(self):
        self.session.close()