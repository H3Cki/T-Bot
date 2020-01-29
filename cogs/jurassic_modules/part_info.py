from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean, insert
from ..utils.dbconnector import DatabaseHandler as Dbh
import random

class PartTypes:
    HEAD = "head"
    BONE = "bones"
    TAIL = "tail"

    types = [HEAD,BONE,TAIL]
    emojis = {
        HEAD : "<:head:671895266520989781>",
        BONE : "<:meat:671895522134458378>",
        TAIL : "<:neuron:671896036654055425>"
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
        return Dbh.session.query(StaticPart).filter(StaticPart.id == self.part_id).one()

    def getCount(self):
        result = 0
        try:
            result = Dbh.session.query(ProfilePart).filter(ProfilePart.par_id == self.part_id, ProfilePart.profile_id == self.profile_id).count()
        except Exception as e:
            pass
        return result

    def delete(self):
        Dbh.session.delete(self)

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
    name = Column(String)
    type = Column(String)


    @classmethod
    def getAll(cls):
        res = Dbh.session.query(cls).all()
        return res

    @classmethod
    def getPart(cls,dino_name,type=None):
        if type:
            result = None
            try:
                result = Dbh.session.query(cls).filter(cls.dino_name == dino_name).filter(cls.type == type).first()
            except Exception as e:
                pass
            return result
        else:
            results = result = Dbh.session.query(cls).filter(cls.dino_name == dino_name).all()
            return results


    @classmethod
    def updateParts(cls, dinolist):
        for dino in dinolist:
            for type in PartTypes.types:
                part = cls.getPart(dino.name,type)
                if not part:
                    p = cls(dino.name,type)
                    Dbh.session.add(p)
                    Dbh.session.commit()
                    print(f"CREATED {p.name}")


    @classmethod
    def drop(cls,dino,profile):
        static_parts = dino.getPartsRequired()
        unowned = []
        for sp in static_parts:
            if not profile.getPart(sp):
                unowned.append(sp)

        if len(unowned) == 0:
            unowned = static_parts

        ptd = random.choice(unowned)
        po =ProfilePart(ptd,profile)
        Dbh.session.add(po)

        return po

    def __init__(self,dino_name,type):
        self.dino_name = dino_name
        self.type = type
        self.name = f"{self.dino_name.capitalize()} {self.type.capitalize()}"

    def give(self,profile):
        p =ProfilePart(self,profile)
        Dbh.session.add(p)

    def getEmoji(self):
        return PartTypes.emojis[self.type]

    def getCount(self, profile):
        return Dbh.session.query(ProfilePart).filter(ProfilePart.profile_id == profile.id, ProfilePart.part_id == self.id).count()