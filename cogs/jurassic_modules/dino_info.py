import discord
import random
from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean, insert
from ..utils.dbconnector import DatabaseHandler as Dbh
import requests
from bs4 import BeautifulSoup
from .discovery import Discovery
from threading import Thread

from .entities.entity import Entity

def checkURL(url):
    req = requests.get(url)
    if req.status_code == 200:
        return req.history[-1].url

    return None

class DinoStatEmojis:
    emojis = {
        'damage' : '<:tasak_wkurwienia:557301227436900364>',
        'defense': '<:shield2:671902310972260382>',
        'speed'  : '<:timer2:671902210908749824>',
        'health' : '❤️',
        'blank' : '<:blank:551400844654936095>',
        'dino1' : '🦖',
        'wiki' : '<:wiki:672823456030654476>'
    }

class StaticDino(Entity):
    
    # CLASS ATTRIBUTES --------------------- #
    
    FILE_PATH = 'data/dinos.txt'
    TYPE   = "dino"
    NAME   = "Dinosaur"
    EMOJI  = '🦖'
    TIERED = True
    EXTRAS = []
    
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = "dino"
    
    parent = Column(Integer, ForeignKey(Entity.id))

    name = Column(String, primary_key=True, autoincrement=False)
    link_pl = Column(String)
    link_en = Column(String)
    image_url = Column(String)
    damage = Column(Integer)
    defense = Column(Integer)
    speed = Column(Integer)
    health = Column(Integer)
    tier_idx = Column(Integer)
    is_random = Column(Boolean)
    
    __mapper_args__ = {
        'polymorphic_identity' : TYPE,
    }
    
    
    def __init__(self,dino_name):
        self.name = dino_name
        self.is_random = True


    def setWikiLinks(self):
        self.link_pl = checkURL('https://pl.wikipedia.org/wiki/'+self.name)
        self.link_en = checkURL('https://en.wikipedia.org/wiki/'+self.name)
        
        
    def setImageUrl(self):
        self.image_url = self.getDinoImageUrls(self.name)[0]
    
    
    def setup(self):
        self.setWikiLinks()
        self.setImageUrl()


    def getPartsRequired(self):
        parts = Dbh.session.query(StaticPart).filter(StaticPart.dino_name == self.name).all()
        return parts


    def getPartsOwned(self, profile):
        po = {}
        self_part_ids = Dbh.session.query(StaticPart.id).filter(StaticPart.dino_name == self.name)
        profile_parts = Dbh.session.query(ProfilePart).filter(ProfilePart.profile_id == profile.id, ProfilePart.part_id in self_part_ids).group_by(ProfilePart.part_id).all()
        return profile_parts
        
        
    def isValid(self):
        if self.image_url and (self.link_en or self.link_en) and len(self.name) < 16:
            return True
        return False

    def delete(self):
        Dbh.session.delete(self)

    def getValidUrl(self):
        return self.link_pl or self.link_en

    def getEmbed(self):
        if self.is_random:
            r = "RANDOM"
        else:
            r = "SET"
        d = f"[TIERS] {r}\nDamage: {self.damage_tier+1}\nDefense: {self.defense_tier+1}\nSpeed: {self.speed_tier+1}\nHealth: {self.health_tier+1}\n**Overall Tier: {self.tier+1}**"
        e = discord.Embed(title=f'🦖 {self.name.capitalize()} <- more info',description=d, url= self.getValidUrl(), color=discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        e.set_image(url=self.image_url)
        return e
    
    def isDiscovered(self,guild_id):
        guild_discs = Discovery._getAllInGuild(guild_id)
        return guild_discs.filter(Discovery.dino_name == self.name).first()

    @classmethod
    def getDinoImageUrls(cls,query):
        q = query.capitalize()
        url = f"https://dinosaurpictures.org/{q}-pictures"
        headers={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
        try:
            html = requests.get(url, headers=headers).text
        except requests.ConnectionError:
            print("couldn't reach website")
            return None

        soup = BeautifulSoup(html, 'html.parser')
        images = soup.find_all("img",{"alt": q})
        images = [image['src'] for image in images]
        return images


    @classmethod
    def getAll(cls):
        res = Dbh.session.query(cls).all()
        return res
    
    @classmethod
    def getRandom(cls):
        return random.choice(cls.dinos)

    @classmethod
    def getSetTierDinos(cls,tier_idx):
        al = cls.getSetDinos()
        return [dino for dino in al if dino.tier == tier_idx]

    @classmethod
    def getRandomSetDinoTierWise(cls):
        found = False
        al = cls.getSetDinos()
        t1 = [dino for dino in al if dino.tier == 0]
        t2 = [dino for dino in al if dino.tier == 1]
        t3 = [dino for dino in al if dino.tier == 2]
        t4 = [dino for dino in al if dino.tier == 3]
        t5 = [dino for dino in al if dino.tier == 4]
        ts = [t1,t2,t3,t4,t5]

        tier = Tier.getRandomTier()
        return random.choice(ts[tier])

    @classmethod
    def getDino(cls,dino_name):
        return Dbh.session.query(cls).get(dino_name)
     

    @classmethod
    def removeFromFile(cls,dinos,del_instance=True):
        
        with open(cls.FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        for dino in dinos:
            Thread(target=StaticPart.removeDinoPartComplelty,args=[dino,]).run()
            content = content.replace(dino.name+'\n','')
            print(f"REMOVING {dino.name}")
            if del_instance:
                dino.delete()
        with open(cls.FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        Dbh.session.commit()

    @classmethod
    def getSetDinos(cls,is_random=False):
        result = []
        try:
            result = Dbh.session.query(cls).filter(cls.is_random == is_random).all()
        except Exception as e:
            pass
        return result

    @classmethod
    def getDinosByTier(cls,tier):
        dinos = []
        for dino in cls.getAll():
            if dino.tier == tier:
                dinos.append(dino)
        return dinos

    @classmethod
    def parseName(cls,name):
        alphabet = 'qwertyuiopasdfghjklzxcvbnm'
        name = name.lower()
        for char in name:
            if char not in alphabet:
                name = name.replace(char,'')
        return name

    @classmethod
    def getDinoFromChannelName(cls,name):
        name = cls.parseName(name)
        return cls.getDino(name)
        

    @classmethod
    def updateDinos(cls,limit=-1):
        c = 0
        with open(cls.FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        # with open(cls.FILE_PATH, 'w', encoding='utf-8') as f:
        #     f.write(content.lower())
            
        # with open(cls.FILE_PATH, 'r', encoding='utf-8') as f:
        #     content = f.read()
        
        # d = []
        # for dino in cls.getSetDinos(is_random=True):
        #     d.append(dino)
        # cls.removeFromFile(d,del_instance=True)
        
        
        dinos = content.split('\n')
        dinos = [dino.lower() for dino in dinos if len(dino) > 2]
        
        to_remove = []
        for i,dino_name in enumerate(dinos):
            if i == limit:
                break
            if dino_name is None or " " in dino_name:
                continue

            dino = cls.getDino(dino_name)
            if not dino:
                new_dino = cls(dino_name)
                print(f"{i+1}/{len(dinos)} SETTING UP '{new_dino.name}'")
                new_dino.setup()
                if new_dino.isValid():
                    c += 1
                    Dbh.session.add(new_dino)
                    #Dbh.session.commit()
                else:
                    to_remove.append(new_dino)

        
        cls.removeFromFile(to_remove,del_instance=False)
        Dbh.session.commit()

    
