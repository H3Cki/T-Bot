from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from ..utils.dbconnector import DatabaseHandler as Dbh
import os

class Discovery(Dbh.Base):
    __tablename__ = 'discovery'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    dino_name = Column(String, ForeignKey('dino.name'))
    guild_id = Column(BigInteger)
    timestamp = Column(TIMESTAMP)

    def __init__(self, dino_name, profile_id, guild_id, timestamp=datetime.now(), in_progress=True):
        self.dino_name = dino_name
        self.profile_id = profile_id
        self.guild_id = guild_id
        self.timestamp = timestamp


    @classmethod
    def getAll(cls):
        res = Dbh.session.query(cls).all() 
        return res

    @classmethod
    def _getAllInGuild(cls,guild_id):
        all = Dbh.session.query(cls).filter(cls.guild_id == guild_id)
        return all
   
    @classmethod
    def getByProfileId(cls,profile_id):
        results = list(Dbh.session.query(cls).filter(Discovery.profile_id == profile_id))
        return results

    @classmethod
    def _getByDinoName(cls,dino_name):
        results = Dbh.session.query(cls).filter(Discovery.dino_name == dino_name)
        return results

    @classmethod
    def getByProfileDino(cls,profile_id,dino_name):
        results = list(Dbh.session.query(cls).filter(Discovery.dino_name == dino_name).filter(Discovery.profile_id == profile_id))
        return results
