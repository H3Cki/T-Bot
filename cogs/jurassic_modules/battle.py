from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean, insert
from ..utils.dbconnector import DatabaseHandler as Dbh
from datetime import datetime

class Battle:
    __tablename__ = "battle"
    
    id = Column(Integer,primary_key=True)
    attacker_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    defender_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    timestamp = Column(TIMESTAMP)
    
    def __init__(self,attacker,defender):
        self.attacker_id = attacker.id
        self.defender_id = defender.id
        self.timestamp = datetime.now()