from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean
from ..utils.dbconnector import DatabaseHandler as Dbh
from .discovery import Discovery
# from .part_info import StaticPart,ProfilePart, PartTypes
# from .dino import Dino
from .dino_info import StaticDino
from .resources import Resources
from ..botinstance import bot

class JurassicProfile(Dbh.Base):
    __tablename__ = "jurassicprofile"

    id = Column(Integer, primary_key=True)
    member_id = Column(BigInteger)
    guild_id = Column(BigInteger)
    send_notification = Column(Boolean)
    exp = Column(Float)

  
    @classmethod
    def getProfile(cls, member):
        try:
            result = list(Dbh.session.query(cls).filter(JurassicProfile.member_id == member.id, JurassicProfile.guild_id == member.guild.id))
            if len(result):
                return result[0]
        except:
            pass
        return None
    
    @classmethod
    def getProfileById(cls, prof_id):
        return Dbh.session.query(cls).get(prof_id)

        
    @classmethod
    def getAll(cls,guild_id=None):
        result = None
        try:
            result = Dbh.session.query(cls)
            if guild_id:
                result = result.filter(cls.guild_id == guild_id)
            
            result = result.all()
        except:
            pass
        return result

    def __init__(self, member_id, guild_id):
        self.member_id = member_id
        self.guild_id = guild_id
        self.exp = 0.0
    
    @property
    def points(self):
        return int(sum([dino.power_level for dino in self.getOwnedDinos()])) + self.resources.value
    
    @property
    def pointsAsText(self):
        return f"{self.points} ({int(sum([dino.power_level for dino in self.getOwnedDinos()]))} - Dinos, {self.resources.value} - Resources)"

    @property
    def resources(self):
        return Resources.getResources(self)

    @property
    def guild(self):
        return bot.get_guild(self.guild_id)
    
    @property
    def member(self):
        return self.guild.get_member(self.member_id)

    def getDinosWithParts(self):
        d = []
        for part in self.getAllParts():
            dino = StaticDino.getDino(part.static_part.dino_name)
            if not dino:
                part.delete()
                Dbh.session.commit()
                continue
            if dino not in d:
                d.append(dino)
        return d

    def getPartsOwnedForDino(self,dino):
        return dino.getParsOwned(self)

    def buildDino(self,static_dino):
        static_parts_req = static_dino.getPartsRequired()
        owned = []
        for sp in static_parts_req:
            po = self.getPart(sp)
            if po:
                owned.append(po)

        if set(static_parts_req).issubset(set([e.static_part for e in owned])):
            dino = Dino(static_dino,self)
            self.addExp(10)
            Dbh.session.add(dino)
            for item in owned:
                item.delete()
            return dino
        return False
    
    def getPart(self,static_part):
        return ProfilePart.getPart(static_part,self)

    def eraseAllParts(self):
        for part in ProfilePart.getAllParts(self):
            part.delete()

    def getAllParts(self):
        return ProfilePart.getAllParts(self)

    def addExp(self,amount):
        self.exp += amount

    def text(self):
        return f"[PROFIL {self.id}]\n {self.member_id}] in {self.guild_id}: {self.exp} exp."

    def getDiscoveries(self):
        result = []
        try:
            result = list(Dbh.session.query(Discovery).filter(Discovery.profile_id == self.id))
        except:
            pass
        return result

    def getOwnedDinos(self):
        result = []
        try:
            result = Dbh.session.query(Dino).filter(Dino.profile_id == self.id).group_by(Dino.name).all()
        except:
            pass
        return result
    
    def delete(self):
        Dbh.session.delete(self)




        