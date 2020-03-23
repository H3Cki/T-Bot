from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Boolean, String, orm
from sqlalchemy.events import event
from ...utils.dbconnector import DatabaseHandler as Dbh
from ..jurassicprofile import JurassicProfile



class ProfileEntity(Dbh.Base):
    TYPE = "profile_entity"
    ENTITY_TYPE = "entity"
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = TYPE
    
    profile_entity_id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    entity_id = Column(Integer, ForeignKey(f'{ENTITY_TYPE}.entity_id'))
    pe_count = Column(Integer, default=0)

    __mapper_args__ = {
        'polymorphic_identity' : TYPE
    }

    # OBJECT METHODS AND PROPERTIES -------- #
    
    def __init__(self,profile,entity,count=1):
        self.profile_id = profile.id
        self.entity_id = entity.entity_id
        self.pe_count = count


    @property
    def entity(self):
        return Entity.get(entity_id=self.entity_id)
        
    @property
    def profile(self):
        return JurassicProfile.getProfile(self.profile_id)   
        
    @property
    def count(self):
        return self.pe_count
    
    @count.setter
    def count(self,value):
        
        if value <= 0:
            print(f'DELETING {self}')
            self.delete()
        else:
            self.pe_count = value
        
    @property
    def briefText(self):
        return self.entity.briefText + f" x{self.count}"


    def delete(self,commit=False):
        Dbh.session.delete(self)
        if commit:
            Dbh.commit()

    # CLASS METHODS ------------------------ #
    
    @classmethod
    def valueOfProfile(cls,profile):
        countable = ['dino']
        assets = cls.get(as_list=True,profile_id=profile.id)
        v = 0
        for asset in assets:
            asset = asset.entity
            if asset.entity_type in countable:
                res = asset.buildCost(profile.guild_id).resources
                for r in res:
                    v += r
        return v
    
    @classmethod
    def add(cls,profile,entity,count=1):
        this = cls.get(profile_id=profile.id,entity_id=entity.entity_id)
        if not this:
            this = cls(profile,entity,count)
            Dbh.session.add(this)
        else:
            if isinstance(this,list):
                this = this[0]
            this.count += count
        Dbh.session.commit()    
        return this
    
    @classmethod
    def get(cls,as_list=False,get_static=False,raw=False,**kwargs):
        query = Dbh.session.query(cls)
        for attr,value in kwargs.items():
            query = query.filter(getattr(cls,  attr) == value)
        if raw:
            return query
        result = query.all()
        if get_static:
            statics = []
            for r in result:
                statics.append(r.entity)
            result = statics
        return result
    
    @classmethod
    def getCount(cls,**kwargs):
        query = Dbh.session.query(cls)
        for attr,value in kwargs.items():
            query = query.filter(getattr(cls,  attr) == value)
        return query.count()

class EntityBase:
    def delete(self):
        Dbh.session.delete(self)

    @classmethod
    def get(cls,as_list=False,raw=False,**kwargs):
        query = Dbh.session.query(cls)
        for attr,value in kwargs.items():
            query = query.filter(getattr(cls,  attr) == value)
        if raw:
            return query
        result = query.all()
        if as_list == False:
            if len(result) == 0:
                result = None
            elif len(result) == 1:
                result = result[0]
        return result

class Entity(Dbh.Base, EntityBase):
    # CLASS ATTRIBUTES --------------------- #
    TYPE   = "entity"
    NAME   = "Basic Entity"
    EMOJI  = '📦'
    TIERED = False
    
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = "entity"
    entity_id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String, default=TYPE)
    
    __mapper_args__ = {
        'polymorphic_on' : entity_type,
        'polymorphic_identity' : TYPE
    }
    
    # OBJECT METHODS AND PROPERTIES -------- #
    
    @property
    def _name(self):
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
    
    def count(self,profile):
        return self.__class__.DROPS_AS.getAll(profile,self).count

        
    def delete(self):
        Dbh.session.delete(self)
    
    def getEmoji(self,**kwg):
        return self.emoji

    # CLASS METHODS ------------------------ #

    @classmethod
    def query(cls,**kwargs):
        query = Dbh.session.query(cls)
        for attr,value in kwargs.items():
            query = query.filter(getattr(cls,  attr) == value)
        return query

    @classmethod
    def update(cls):
        pass
    
  
    
    
        
    