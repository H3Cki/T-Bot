from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger
from ..utils.dbconnector import DatabaseHandler as Dbh
from ..utils.copy import Copy
import time
import discord

class Rewards:
    rewards = {
        'online' : [1,0,0],
        'on_voice_chat' : [3,2,1],
        'playing' : [1,1,1],
        'company' : [0,1,1],
        'discovery' : [400,200,50]
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
            reward[0] += packet[0]*4
            reward[1] += packet[1]*4
            reward[2] += packet[2]*4

        return reward
    

    
class ResourceEmojis:
    SHIT = 'shit'
    WOOD = 'wood'
    GOLD = 'gold'
    names = [SHIT,WOOD,GOLD]
    emojis = {
        SHIT : '<:shit1:674037327101952043>',
        WOOD : '<:wood:674037327399485440>',
        GOLD : '<:gold:674037327118729257>',
        SHIT+'void' : '<:shit_void:689095308499615764>',
        WOOD+'void' : '<:wood_void:689095308231442437>',
        GOLD+'void' : '<:gold_void:689094862045315109>'
    }

class ResourcesBase(Copy):
    @classmethod
    def getAll(cls):
        return Dbh.session.query(cls).all()
    

    @classmethod
    def getResources(cls,profile):
        result = Dbh.session.query(cls).filter(cls.profile_id == profile.id).first()
        if not result:
            result = cls(profile)
            Dbh.session.add(result)
            Dbh.session.commit()
        return result

    @classmethod
    def updateResources(cls,profiles):
        updated = False
        for profile in profiles:
            r = cls.getResources(profile)
            if not r:
                updated = True
                res = cls(profile)
                Dbh.session.add(res)

    def __init__(self,profile=None,cost=[0,0,0]):
        if profile:
            print(profile)
            self.profile_id = profile.id
        self.shit  = cost[0]
        self.wood  = cost[1]
        self.gold  = cost[2]
        
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
    
            
    def asText(self,blank=True):
        blank = '<:blank:551400844654936095>' if blank else ' '
        return f"{ResourceEmojis.emojis['shit']}{self.shit}{blank}{ResourceEmojis.emojis['wood']}{self.wood}{blank}{ResourceEmojis.emojis['gold']}{self.gold}"
    
    
    def compareAsText(self,resources):
        blank = '<:blank:551400844654936095>'
        comps = []
        i = 0
        for this_res, cmp_res in zip(self.resources,resources.resources):
            r_name = ResourceEmojis.names[i]
            
            if cmp_res >= this_res:
                emoji = ResourceEmojis.emojis[r_name]
            else:
                emoji = ResourceEmojis.emojis[r_name+'void']
                
            comps.append(f'{emoji}{cmp_res}/{this_res}')
            
            i += 1
            
        return blank.join(comps)
    
    def steal(self,capacity):
        #bounty = self.__class__()
        
        r = []
        c = []
        for res, cap in zip(self.resources, capacity.resources):
            if res > cap:
                res -= cap
            else:
                cap = res
                res = 0
            r.append(res)
            c.append(cap)
        self.setResources(r)
        capacity.setResources(c)
        
    def addResources(self,res=[0,0,0]):
        self.shit += res[0]
        self.wood += res[1]
        self.gold += res[2]
        return self
        
    def subResources(self,res=[0,0,0]):
        self.shit -= res[0]
        self.wood -= res[1]
        self.gold -= res[2]
        return self
        
    def setResources(self,res=[0,0,0]):
        self.shit = res[0]
        self.wood = res[1]
        self.gold = res[2]
        return self
        
    def __add__(self, res):
        self.shit += res.shit
        self.wood += res.wood
        self.gold += res.gold
        return self
        
    def __sub__(self, res):
        self.shit -= res.shit
        self.wood -= res.wood
        self.gold -= res.gold
        return self
    
    def __mul__(self, multiplier):
        self.shit = int(self.shit * multiplier)
        self.wood = int(self.wood * multiplier)
        self.gold = int(self.gold * multiplier)
        return self

    def __gt__(self, comp_res):
        for res, cres in zip(self.resources,comp_res.resources):
            if res < cres:
                return False
        return True

class Resources(ResourcesBase, Dbh.Base):
    update_interval = 60
    last_update = 0
    
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    shit = Column(Integer)
    wood = Column(Integer)
    gold = Column(Integer)
    
    