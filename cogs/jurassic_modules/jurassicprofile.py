from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean, orm
from ..utils.dbconnector import DatabaseHandler as Dbh
from .resources import Resources
from ..botinstance import bot
from datetime import datetime, timedelta

class JurassicProfile(Dbh.Base):
    __tablename__ = "jurassicprofile"

    id = Column(Integer, primary_key=True)
    member_id = Column(BigInteger)
    guild_id = Column(BigInteger)
    send_notification = Column(Boolean)
    last_attack = Column(TIMESTAMP)
    last_destroyed = Column(TIMESTAMP)


    ATTACKED_COOLDOWN = timedelta(minutes=45)


    @classmethod
    def get(cls,member=None,as_list=False,create=True,**kwargs):
        if member:
            kwargs['member_id'] = member.id
            kwargs['guild_id'] = member.guild.id
        query = Dbh.session.query(cls)
        for attr,value in kwargs.items():
            query = query.filter(getattr(cls,  attr) == value)
        result = query.all()
        if as_list == False:
            if len(result) == 0:
                result = None
            elif len(result) == 1:
                result = result[0]
        
        if result == None and member and create:
            result = cls(member.id,member.guild.id)
            Dbh.session.add(result)
            Dbh.commit()
        
        return result
    

    def __init__(self, member_id, guild_id):
        self.member_id = member_id
        self.guild_id = guild_id
        self.setup()
        
    def setup(self):
        self.battles = []


    @property
    def resources(self):
        return Resources.getResources(profile=self)

    @property
    def guild(self):
        return bot.get_guild(self.guild_id)
    
    @property
    def member(self):
        return self.guild.get_member(self.member_id)

    def text(self):
        return f"[PROFIL {self.id}]\n {self.member_id}] in {self.guild_id}: {self.exp} exp."


    def delete(self):
        Dbh.session.delete(self)


    @classmethod
    def updateProfiles(cls):
        for profile in cls.get(as_list=True):
            profile.setup()


        