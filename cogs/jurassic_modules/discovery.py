from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from ..utils.dbconnector import DatabaseHandler as Dbh
from .entities.entity import Entity
import os

class Discovery(Entity):
    TYPE = "discovery"
    NAME = "Discovery"
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = TYPE
    parent = Column(Integer, ForeignKey(Entity.entity_id))
    

    __mapper_args__ = {
        'polymorphic_identity' : TYPE
    }

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


