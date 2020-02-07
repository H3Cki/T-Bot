from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger
from ..utils.dbconnector import DatabaseHandler as Dbh
import time
import discord

class Rewards:
    rewards = {
        'online' : [1,0,0],
        'on_voice_chat' : [1,1,1],
        'playing' : [0,0,1],
        'company' : [1,1,0],
        'discovery' : [0,0,25]
    }
    
    @classmethod
    def getMemberReward(cls,member):
        reward = [0,0,0]
        packets = []
        if member.status == discord.Status.online:
            packets.append(cls.rewards['online'])
        if member.voice:
            if member.guild.afk_channel:
                if member.voice.channel.id == member.guild.afk_channel.id:
                    return reward
            if len(member.voice.channel.members):
                packets.append(cls.rewards['company'])
            packets.append(cls.rewards['on_voice_chat'])
            if member.activity:
                packets.append(cls.rewards['playing'])
        
        
        
        for packet in packets:
            reward[0] += packet[0]
            reward[1] += packet[1]
            reward[2] += packet[2]

        return reward
    

    
class ResourceEmojis:
    
    emojis = {
        'shit' : '<:shit1:674037327101952043>',
        'wood' : '<:wood:674037327399485440>',
        'gold' : '<:gold:674037327118729257>'
    }


class Resources(Dbh.Base):
    update_interval = 300
    last_update = 0
    
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    shit = Column(Integer)
    wood = Column(Integer)
    gold = Column(Integer)
    
    @classmethod
    def getAll(cls):
        return Dbh.session.query(cls).all()
    
    
    @classmethod
    def getResources(cls,profile):
        return Dbh.session.query(cls).filter(cls.profile_id == profile.id).first()

    @classmethod
    def updateResources(cls,profiles):
        updated = False
        for profile in profiles:
            r = cls.getResources(profile)
            if not r:
                updated = True
                res = cls(profile)
                Dbh.session.add(res)
                print(f"\nCREATED RESOURCES: profile_id = {res.profile_id}")
            else:
                print(f"\nFOUND RESOURCES: profile_id = {r.profile_id}")    
                
    def __init__(self,profile):
        self.profile_id = profile.id
        self.shit  = 0
        self.wood  = 0
        self.gold  = 0
        
    @property
    def resources(self):
        return [self.shit,self.wood,self.gold]
        
    @property
    def value(self):    
        return self.shit+self.wood+self.gold
    
    def isGreaterThan(self,cost):
        for res,cost in zip(self.resources,cost):
            if not res >= cost:
                return False
        return True    
    
            
    def asText(self):
        return f"{ResourceEmojis.emojis['shit']}{self.shit} {ResourceEmojis.emojis['wood']}{self.wood} {ResourceEmojis.emojis['gold']}{self.gold}"
        
        
    def addResources(self,res=[0,0,0]):
        self.shit += res[0]
        self.wood += res[1]
        self.gold += res[2]
        
    def subResources(self,res=[0,0,0]):
        self.shit -= res[0]
        self.wood -= res[1]
        self.gold -= res[2]
        
    def setResources(self,res=[0,0,0]):
        self.shit = res[0]
        self.wood = res[1]
        self.gold = res[2]