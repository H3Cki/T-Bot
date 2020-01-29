from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean
from ..utils.dbconnector import DatabaseHandler as Dbh
from .discovery import Discovery
from .dino import Dino

class JurassicGuildSettings(Dbh.Base):
    __tablename__ = "jurassicguildsettings"

    guild_id = Column(Integer, primary_key=True)
    j_notif_channel = Column(BigInteger)
    j_voice_dino_cat = Column(BigInteger)

  