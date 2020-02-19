from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean
from ..utils.dbconnector import DatabaseHandler as Dbh
from ..botinstance import bot

class JGuildSettings(Dbh.Base):
    __tablename__ = "jguildsettings"

    guild_id = Column(Integer, primary_key=True)
    active = Column(Boolean)
    notif_channel = Column(BigInteger)
    voice_cat = Column(BigInteger)

    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.notif_channel = False
        self.voice_cat = False
        self.active = True
    
    @property
    def guild(self):
        return bot.get_guild(self.guild_id)
    
    @property
    def channel(self):
        return self.guild.get_channel(self.notif_channel)
    
    @property
    def voiceReady(self):
        return self.active and self.voice_cat
    
    async def send(self,content="",embed=None):
        channel = self.channel
        if not self.active or not self.notif_channel or not channel:
            return
        await channel.send(content,embed=embed)
        
    @classmethod
    def get(cls,gid):
        gs = Dbh.session.query(cls).get(gid)
        if not gs:
            gs = cls(gid)
            Dbh.session.add(gs)
            Dbh.session.commit()
        return gs
        
    