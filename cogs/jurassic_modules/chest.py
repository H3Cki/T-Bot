from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Boolean, String
from ..utils.dbconnector import DatabaseHandler as Dbh
from .dino_info import StaticDino
from .dino import Dino
from .jurassicprofile import JurassicProfile as JP
from .part_info import ProfilePart
from .tiers import Tier

from discord import Embed
import random

class ChestEmojis:
    emojis = {
        'not_open' : '🔒',
        'open' : '🔓',
        'not_open_key' : '🔐'
    }
    
class KeyEmojis:
    
    emojis = {
        0 : '<:key_t1:674685548362858531>',
        1 : '<:key_t2:674685548656328714>',
        2 : '<:key_t3:674685548593545216>',
        3 : '<:key_t4:674685548337561635>',
        4 : '<:key_t5:674685548350275596>'
    }


class Key(Dbh.Base):
    name = "Chest Key"
    __tablename__ = "key"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    tier_idx = Column(Integer)
    
    def __init__(self,profile,tier=None):
        self.profile_id = profile.id
        self.tier_idx = tier or Tier.getRandomTier()
    
    @classmethod
    def getAll(cls,profile):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id).all()
    
    @property
    def emoji(self):
        return KeyEmojis.emojis[self.tier_idx]
    
    @property
    def dropText(self):
        return f"{self.emoji} {Key.name} **Tier {self.tier_idx+1}**"
    
    @classmethod
    def getTierKey(cls,profile,tier_idx):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id, cls.tier_idx == tier_idx).first()

class ProfileChest:
    pass


CHESTS_TYPES = [DinoChest,]
CHESTS = []
for CT in CHESTS_TYPES:
    for tier_idx in range(Tier.n_tiers):
        c = CT(tier_idx)
        CHESTS.append(c)

class StaticChest(Dbh.Base):
    name = "Chest"
    _code = "chest"
    
    rewards = []
    
    __tablename__ = "chest"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    name = Column(String)
    code = Column(String)
    tier_idx = Column(Integer)
    require_key = Column(Boolean)
    
    def __init__(self,tier,require_key=False):
        self.code = self.__class__.code
        self.name = self.__class__.name
        self.tier_idx = tier
        self.require_key = require_key
    
    @property
    def code(self):
        return self.__class__._code+str(self.tier_idx)
    
    @property
    def profile(self):
        return Dbh.session.query(JP).filter(JP.id == self.profile_id).first()
    
    @property
    def emoji(self):
        if self.opened:
            return ChestEmojis.emojis['open']
        else:
            if self.require_key:
                return ChestEmojis.emojis['not_open_key']
            else:
                return ChestEmojis.emojis['not_open']
    
    @property
    def dropText(self):
        return f"{self.emoji} {DinoChest.name} **Tier {self.tier_idx+1}**"
    
    def getKey(self):
        pass
    
    def generateReward(self):
        return random.choice(rewards)
    
    def open(self):
        if self.require_key:
            key = self.getKey()
            if not key:
                raise Exception(f"❗ You do not have a matching key for {self.dropText}.")
            
        reward = self.generateReward()
        
        Dbh.session.delete(key)
        Dbh.session.delete(self)

        return reward
    
    @classmethod
    def getProfileChests(cls,profile):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id,cls.opened == False).all()
    
    @classmethod
    def getChest(cls,code):
        return Dbh.session.query(cls).filter(cls.code == code).first()
    
    @classmethod
    def updateChests(cls):
        for chest in CHESTS:
            c = cls.getChest(c.code)
            if not c:
                
    
class DinoChest(StaticChest):
    name = "Dino Chest"
    code = "dino_chest"
    
    def generateReward(self):
        sdino = self.static_dino
        if random.uniform(0,100) < 75:
            return ProfilePart(random.choice(sdino.getPartsRequired()),JP.getProfileById(self.profile_id))
        else:
            return Dino(sdino,JP.getProfileById(self.profile_id))
        
        