from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean
from ..utils.dbconnector import DatabaseHandler as Dbh
from .discovery import Discovery
from .dino import Dino
from ..botinstance import bot

class JGuildSettings(Dbh.Base):
    __tablename__ = "jguildsettings"

    guild_id = Column(Integer, primary_key=True)
    active = Column(Boolean)
    notify = Column(Boolean)
    j_notif_channel = Column(BigInteger)
    j_voice_cat = Column(BigInteger)

    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.j_notif_channel = False
        self.j_voice_cat = False
        self.notify = False
        self.active = True
    
    @property
    def guild(self):
        return bot.get_guild(self.guild_id)
    
    @property
    def channel(self):
        return self.guild.get_channel(self.j_notif_channel)
    
    async def send(self,content="",embed=None):
        channel = self.channel
        if not self.active or not self.notify or not self.j_notif_channel or not channel:
            return
        await channel.send(content,embed=embed)
        
    @classmethod
    def get(cls,gid):
        return Dbh.session.query(cls).get(gid)
        
    