from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Boolean, String
from ...utils.dbconnector import DatabaseHandler as Dbh
from ..tiers import Tier
from ..jurassicprofile import JurassicProfile as JP

class Droppable:
    def drop(self, profile):
        profile_me = ProfileEntity(profile,self)
        Dbh.session.add(profile_me)
    

class ProfileEntity(Dbh.Base):
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = "profile_entity"
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    entity_id = Column(Integer, ForeignKey('entity.id'))

    # OBJECT METHODS AND PROPERTIES -------- #
    
    def __init__(self,profile,entity):
        self.profile_id = profile.id
        self.entity_id = entity.id

    @property
    def profile(self):
        return JP.getProfile(self.profile_id)
    
    @property
    def entity(self):
        return Entity.getEntity(self.entity_id)

    # CLASS METHODS ------------------------ #
    
    @classmethod
    def getAllProfileEntitys(cls,profile):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id).all()
    
    @classmethod
    def getProfileEntitys(self,profile,entity):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id, cls.entity_id == entity.id).all()
    
    @classmethod
    def getProfileEntity(self,profile,entity):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id, cls.entity_id == entity.id).first()


class Entity(Dbh.Base):
    # CLASS ATTRIBUTES --------------------- #
    
    TYPE   = "entity"
    NAME   = "Basic Entity"
    EMOJI  = '📦'
    TIERED = True
    EXTRAS = []
    
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = "entity"
    id = Column(Integer, primary_key=True)
    tier_idx = Column(Integer)
    type = Column(String)
    
    __mapper_args__ = {
        'polymorphic_on' : type,
        'polymorphic_identity' : TYPE
    }
    
    # OBJECT METHODS AND PROPERTIES -------- #
    
    def __init__(self,tier_idx=None):
        self.tier_idx = tier_idx
        self.type = self.__class__.TYPE
        for extra in self.__class__.EXTRAS:
            extra()
    
    def requirements(self):
        pass
    
    def inner_use(self):
        pass
    
    def finalize(self):
        pass
    
    async def act(self, ctx):
        a = self.requirements()
        b = self.inner_use()
        c = self.finalize()
        
    
    
    @property
    def name(self):
        return self.__class__.NAME
            
    @property
    def emoji(self):
        if self.__class__.TIERED:  
            return self.__class__.EMOJI[self.tier_idx]
        else:
            return self.__class__.EMOJI
        
    @property
    def dropText(self):
        text = f"{self.emoji} **{self.name}**"
        if self.__class__.TIERED:
            text += f" Tier {self.tier_idx+1}"
        return text
    
    # CLASS METHODS ------------------------ #

    @classmethod
    def getEntity(cls,id):
        return Dbh.session.query(cls).filter(cls.id == id).one()

    @classmethod
    def _getAll(cls):
        return Dbh.session.query(cls)
    
    @classmethod
    def getRandom(cls):
        if cls.TIERED:
            tier = Tier.getRandomTier()
        else:
            tier = None
        
        return Dbh.session.query(cls).filter(cls.tier_idx == tier).one()
    
    @classmethod
    def updateEntitys(cls):
        pass
    
    @classmethod
    def drop(cls, profile):
        random = cls.getRandom()
        random.drop()