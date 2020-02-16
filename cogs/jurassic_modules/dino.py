from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean, insert
from ..utils.dbconnector import DatabaseHandler as Dbh
from discord import Embed
from .dino_info import DinoStatEmojis as DSE
from .dino_info import StaticDino

class Dino(Dbh.Base):
    __tablename__ = "dino"

    id = Column(Integer,primary_key=True)
    name = Column(String, ForeignKey('static_dino.name'))
    profile_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    damage = Column(Integer)
    defense = Column(Integer)
    speed = Column(Float)
    health = Column(Integer)
    tier = Column(Integer)
    
    def __init__(self,sd,profile):
        self.name = sd.name
        self.profile_id = profile.id
        self.damage = 0
        self.defense = 0
        self.speed = 0
        self.health = 0
        self.tier = 0
    
    @property
    def static_dino(self):
        return Dbh.session.query(StaticDino).filter(StaticDino.name == self.name).first()
    
    @property
    def power_level(self):
        return (self.damage+self.defense+self.health)*self.speed
    
    def getEmbed(self):
        dmg = DSE.emojis['damage']
        deff = DSE.emojis['defense']
        speed = DSE.emojis['speed']
        health = DSE.emojis['health']
        b = DSE.emojis['blank']
        stats = f'{dmg}{self.damage}{b}{deff}{self.defense}{b}{health}{self.health}{b}{speed}{self.speed}'
        e = Embed(title=f'{self.name.capitalize()} [Tier {self.tier+1}]',description=stats)
        return e
    
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
