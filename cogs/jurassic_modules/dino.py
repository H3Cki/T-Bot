from .tiers import DAMAGE_TIERS, DEFENSE_TIERS, SPEED_TIERS, HEALTH_TIERS
from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean, insert
from ..utils.dbconnector import DatabaseHandler as Dbh


class Dino(Dbh.Base):
    __tablename__ = "dino"

    id = Column(Integer,primary_key=True)
    name = Column(String, ForeignKey('static_dino.name'))
    profile_id = Column(String, ForeignKey('jurassicprofile.id'))
    damage = Column(Integer)
    defense = Column(Integer)
    speed = Column(Float)
    health = Column(Integer)
    tier = Column(Integer)
    
    def __init__(self,sd,profile):
        self.name = sd.name
        self.profile_id = profile.id
        self.damage = DAMAGE_TIERS[sd.damage_tier].getValue()
        self.defense = DEFENSE_TIERS[sd.defense_tier].getValue()
        self.speed = round(SPEED_TIERS[sd.speed_tier].getValue(),2)
        self.health = HEALTH_TIERS[sd.health_tier].getValue()
        self.tier = sd.tier
        
    def text(self):
        return f"[DINO {self.name}] \ndamage: {self.damage}\ndef: {self.defense}\nspeed: {self.speed}\nhp: {self.health}"

    def die(self):
        Dbh.session.delete(self)


    def getCount(self):
        result = []
        try:
            result = Dbh.session.query(Dino).filter(Dino.profile_id == self.profile_id).filter(Dino.id == self.id).all()
        except Exception as e:
            pass
        return len(result)
