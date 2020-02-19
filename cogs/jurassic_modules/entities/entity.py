from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Boolean, String
from ...utils.dbconnector import DatabaseHandler as Dbh
from ..jurassicprofile import *



class ProfileEntity(Dbh.Base):
    TYPE = "profile_entity"
    ENTITY_TYPE = "entity"
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = TYPE
    
    profile_entity_id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    entity_id = Column(Integer, ForeignKey(f'{ENTITY_TYPE}.entity_id'))

    __mapper_args__ = {
        'polymorphic_identity' : TYPE
    }

    # OBJECT METHODS AND PROPERTIES -------- #
    
    def __init__(self,profile,entity):
        self.profile_id = profile.id
        self.entity_id = entity.entity_id


    @property
    def profile(self):
        return JP.getProfile(self.profile_id)
    
    @property
    def entity(self):
        return Entity.getEntity(self.entity_id)
    
    def getCount(self, profile):
        c = self.__class__
        return Dbh.session.query(c).filter(c.profile_id == profile.id, c.entity_id == self.entity_id).count()

    # CLASS METHODS ------------------------ #
    
    @classmethod
    def getAllProfileEntities(cls,profile):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id).all()
    
    @classmethod
    def getProfileEntities(cls,profile,entity):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id, cls.entity_id == entity.id).all()
    
    @classmethod
    def getProfileEntity(cls,profile,entity):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id, cls.entity_id == entity.id).first()


class Entity(Dbh.Base):
    # CLASS ATTRIBUTES --------------------- #
    TYPE   = "entity"
    NAME   = "Basic Entity"
    EMOJI  = '📦'
    TIERED = False
    EXTRAS = []
    
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = "entity"
    entity_id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String, default=TYPE)
    
    __mapper_args__ = {
        'polymorphic_on' : entity_type,
        'polymorphic_identity' : TYPE
    }
    
    # OBJECT METHODS AND PROPERTIES -------- #
    
    def __init__(self):
        for extra in self.__class__.EXTRAS:
            extra()
    
    @property
    def name(self):
        return self.__class__.NAME
            
    @property
    def emoji(self):
        if self.__class__.TIERED: 
            if isinstance(self.__class__.EMOJI,list):
                return self.__class__.EMOJI[self.tier-1]
        return self.__class__.EMOJI
        
    @property
    def briefText(self):
        text = f"{self.emoji} **{self.name.capitalize()}**"
        if self.__class__.TIERED:
            text += f" Tier {self.tier}"
        return text
    
    
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
        
    def delete(self):
        Dbh.session.delete(self)
    
    # CLASS METHODS ------------------------ #

    @classmethod
    def getEntity(cls,id):
        return Dbh.session.query(cls).filter(cls.entity_id == id).first()

    @classmethod
    def _getAll(cls):
        return Dbh.session.query(cls)
    
    @classmethod
    def getAll(cls):
        return Dbh.session.query(cls).all()
    
    @classmethod
    def getRandom(cls):
        if cls.TIERED:
            pass
            #tier = Tier.getRandomTier()
        else:
            tier = None
        
        return Dbh.session.query(cls).filter(cls.tier == tier).one()
    
    @classmethod
    def updateEntitys(cls):
        pass
    
    @classmethod
    def drop(cls, profile):
        random = cls.getRandom()
        random.drop()
        
        
    