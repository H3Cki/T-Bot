from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Boolean, String
from ...utils.dbconnector import DatabaseHandler as Dbh
from ..tiers import Tier
from ..jurassicprofile import JurassicProfile as JP

class ProfileItem(Dbh.Base):
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = "profile_item"
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    static_item_id = Column(Integer, ForeignKey('item.id'))

    # OBJECT METHODS AND PROPERTIES -------- #
    
    def __init__(self,profile,static_item):
        self.profile_id = profile.id
        self.static_item_id = static_item.id

    @property
    def profile(self):
        return JP.getProfile(self.profile_id)
    
    @property
    def item(self):
        return StaticItem.getItem(self.static_item_id)

    # CLASS METHODS ------------------------ #
    
    @classmethod
    def getAllProfileItems(cls,profile):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id).all()
    
    @classmethod
    def getProfileItems(self,profile,static_item):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id, cls.static_item_id == static_item.id).all()
    
    @classmethod
    def getProfileItem(self,profile,static_item):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id, cls.static_item_id == static_item.id).first()


class StaticItem(Dbh.Base):
    # CLASS ATTRIBUTES --------------------- #
    
    TYPE   = "item"
    NAME   = "Basic Item"
    EMOJI = ('📦',)
    TIERED = True
    EXTRAS = []
    
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    tier_idx = Column(Integer)
    type = Column(String)
    
    __mapper_args__ = {
        'polymorphic_on' : type,
        'polymorphic_identity' : TYPE
    }
    
    # OBJECT METHODS AND PROPERTIES -------- #
    
    def __init__(self,tier_idx=0):
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
    
    async def use(self, ctx):
        a = self.requirements()
        b = self.inner_use()
        c = self.finalize()
        
    def drop(self, profile):
        profile_me = ProfileItem(profile,self)
        Dbh.session.add(profile_me)
    
    
    @property
    def name(self):
        return self.__class__.NAME
            
    @property
    def emoji(self):
        return self.__class__.EMOJI[self.tier_idx]
    
    @property
    def dropText(self):
        text = f"{self.emoji} **{self.name}**"
        if self.__class__.TIERED:
            text += f" Tier{self.tier_idx+1}"
        return text
    
    # CLASS METHODS ------------------------ #

    @classmethod
    def getItem(cls,id):
        return Dbh.session.query(cls).filter(cls.id == id).one()

    @classmethod
    def _getAll(cls):
        return Dbh.session.query(cls)
    
    @classmethod
    def getRandom(cls):
        if cls.TIERED:
            tier = Tier.getRandomTier()
        else:
            tier = 0
        
        return Dbh.session.query(cls).filter(cls.tier_idx == tier).one()
    
    @classmethod
    def updateItems(cls):
        pass
    
    @classmethod
    def drop(cls, profile):
        random = cls.getRandom()
        random.drop()