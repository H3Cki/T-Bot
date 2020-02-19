from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean, insert, PrimaryKeyConstraint
from ..utils.dbconnector import DatabaseHandler as Dbh
from .entities.entity import Entity, ProfileEntity
import random


class PartTypes:
    HEAD = "head"
    MEAT = "meat"
    BONE = "bones"

    types = [HEAD,MEAT,BONE]
    
    name_to_idx = {
        HEAD : 0,
        MEAT : 1,
        BONE : 2
    }
    
    emojis = {
        HEAD : "<:head:671895266520989781>",
        MEAT : "<:meat:671895522134458378>",
        BONE : "<:bones:672476713334341643>",
        HEAD+"void" : '<:head_void:673959867890794535> ',
        MEAT+"void" : '<:meat_void:673959534783496263> ',
        BONE+"void" : '<:bones_void:673959534661992494> '
    }

class ProfilePart(ProfileEntity):
    TYPE = "profile_part"
    ENTITY_TYPE = "part"
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = TYPE
    parent = Column(Integer, ForeignKey(ProfileEntity.entity_id))
    
    id = Column(Integer, primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity' : TYPE
    }


class StaticPart(Entity):
    # CLASS ATTRIBUTES --------------------- #
    
    TYPE   = "part"
    NAME   = "Dino Part"
    EMOJI  = '🦖'
    TIERED = False
    driver = None
    
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = TYPE
    
    
    parent = Column(Integer, ForeignKey(Entity.entity_id))

    id = Column(Integer, primary_key=True)
    dino_name = Column(String, ForeignKey('dino.name'))
    type_idx = Column(Integer)
    
    __mapper_args__ = {
        'polymorphic_identity' : TYPE
    }
    

    def __init__(self,dino_name,type_idx):
        self.dino_name = dino_name
        self.type_idx = type_idx

    @property
    def name(self):
        return f"**{self.dino_name.capitalize()}** {self.type}"

    @property
    def briefText(self):
        text = f"{self.emoji} {self.name}"
        return text

    @property
    def type(self):
        return PartTypes.types[self.type_idx]

    @property
    def emoji(self):
        return PartTypes.emojis[self.type]

    @classmethod
    def getEntity(cls,dino_name,typ=None):
        return Dbh.session.query(cls).filter(cls.dino_name == dino_name, cls.type_idx == typ).first()
    
        
    @classmethod
    def getEmoji(self,addon=''):
        return PartTypes.emojis[self.type+addon]
    
    @classmethod
    def updateParts(cls, dinolist):
        for dino in dinolist:
            for t in range(0,len(PartTypes.types)):
                part = cls.getEntity(dino.name,t)
                if not part:
                    p = cls(dino.name,t)
                    Dbh.session.add(p)
                    print(f"CREATING {p.name}")

        Dbh.session.commit()


    # @classmethod
    # def drop(cls,dino,profile):
    #     static_parts = dino.getEntitysRequired()
        
    #     if random.randint(0,100) <= 60:
    #         unowned = []
    #         for sp in static_parts:
    #             if not profile.getEntity(sp):
    #                 unowned.append(sp)
    #     else:
    #         unowned = static_parts
            
    #     if len(unowned) == 0:
    #         unowned = static_parts

    #     ptd = random.choice(unowned)
    #     po = ProfilePart(ptd,profile)

    #     return po,ptd

    @classmethod
    def removeDinoPartComplelty(cls,dino):
        for part in StaticPart.getAll():
            if part.dino_name == dino.name:
                for ppart in ProfilePart.getAll():
                    if ppart.part_id == part.id:
                        Dbh.session.delete(ppart)
                        print(f"DELETED OWNED PART")
                Dbh.session.delete(part)
                print(f"DELETED {part.dino_name} {part.type}")
                Dbh.session.commit()


    


    