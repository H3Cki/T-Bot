from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean, insert
from ..utils.dbconnector import DatabaseHandler as Dbh
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

class ProfilePart(Dbh.Base):
    __tablename__ = "profile_part"

    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey('static_part.id'))
    profile_id = Column(Integer, ForeignKey('jurassicprofile.id'))

    def __init__(self,part,profile):
        self.part_id = part.id
        self.profile_id = profile.id
        self._static_part = part
    
    @property
    def static_part(self):
        return Dbh.session.query(StaticPart).filter(StaticPart.id == self.part_id).first()

    @property
    def dropText(self):
        sp = self.static_part
        return f"{sp.getEmoji()} **{sp.name}**"

    def getCount(self):
        result = 0
        try:
            result = Dbh.session.query(ProfilePart).filter(ProfilePart.part_id == self.part_id, ProfilePart.profile_id == self.profile_id).count()
        except Exception as e:
            pass
        return result

    def delete(self):
        Dbh.session.delete(self)

    @classmethod
    def getAll(cls):
        return Dbh.session.query(cls).all()

    @classmethod
    def getAllParts(cls,profile):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id).all()

    @classmethod
    def getPart(cls,sp, profile):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id, cls.part_id == sp.id).first()

class StaticPart(Dbh.Base):
    __tablename__ = "static_part"

    id = Column(Integer, primary_key=True)
    dino_name = Column(String, ForeignKey('static_dino.name'))
    type_idx = Column(Integer)


    @classmethod
    def getAll(cls):
        res = Dbh.session.query(cls).all()
        return res

    @classmethod
    def getPart(cls,dino_name,typ=None):
        return Dbh.session.query(cls).filter(cls.dino_name == dino_name, cls.type_idx == typ).first()
    

    @classmethod
    def updateParts(cls, dinolist):
        for dino in dinolist:
            for t in range(0,len(PartTypes.types)):
                part = cls.getPart(dino.name,t)
                if not part:
                    p = cls(dino.name,t)
                    Dbh.session.add(p)
                    Dbh.session.commit()


    @classmethod
    def drop(cls,dino,profile):
        static_parts = dino.getPartsRequired()
        
        if random.randint(0,100) <= 60:
            unowned = []
            for sp in static_parts:
                if not profile.getPart(sp):
                    unowned.append(sp)
        else:
            unowned = static_parts
            
        if len(unowned) == 0:
            unowned = static_parts

        ptd = random.choice(unowned)
        po = ProfilePart(ptd,profile)

        return po,ptd

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

    def __init__(self,dino_name,type_idx):
        self.dino_name = dino_name
        self.type_idx = type_idx

    @property
    def name(self):
        return f"**{self.dino_name.capitalize()}** {self.type}"

    @property
    def dropText(self):
        return f"{self.getEmoji()} {self.name}"

    @property
    def type(self):
        return PartTypes.types[self.type_idx]

    def give(self,profile):
        p =ProfilePart(self,profile)
        Dbh.session.add(p)

    def getEmoji(self,extra=""):
        return PartTypes.emojis[self.type+extra]

    def getCount(self, profile):
        return Dbh.session.query(ProfilePart).filter(ProfilePart.profile_id == profile.id, ProfilePart.part_id == self.id).count()