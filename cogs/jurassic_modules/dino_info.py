import discord
from discord import Embed
import random
from cogs.utils.google_img import get_google_img
from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean, insert
from ..utils.dbconnector import DatabaseHandler as Dbh
import requests
from .part_info import StaticPart, ProfilePart

def checkURL(url,suff):
    req = requests.get(url)
    if req.status_code == 200:
        return url

    req = requests.get(url+suff)
    if req.status_code == 200:
        return url   

    return None

class DinoStatEmojis:
    emojis = {
        'damage' : '<:tasak_wkurwienia:557301227436900364>',
        'defense': '<:shield2:671902310972260382>',
        'speed'  : '<:timer2:671902210908749824>',
        'health' : '❤️',
        'blank' : '<:blank:551400844654936095>'
    }

class StaticDino(Dbh.Base):
    dinos = []
    file_path = 'data/dinos.txt'
    __tablename__ = "static_dino"

    name = Column(String, primary_key=True)
    link_pl = Column(String)
    link_en = Column(String)
    image_url = Column(String)
    damage_tier = Column(Integer)
    defense_tier = Column(Integer)
    speed_tier = Column(Integer)
    health_tier = Column(Integer)
    tier = Column(Integer)
    is_random = Column(Boolean)
    discovered = Column(Boolean)

    @classmethod
    def updateList(cls):
        cls.dinos = cls.getAll()

    @classmethod
    def getAll(cls):
        res = Dbh.session.query(cls).all()
        return res

    @classmethod
    def getRandom(cls):
        return random.choice(cls.dinos)

    @classmethod
    def getDino(cls,dino_name):
        return Dbh.session.query(cls).get(dino_name)
     

    @classmethod
    def removeFromFile(cls,dinos,del_instance=True):
        with open(cls.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        for dino in dinos:
            content = content.replace(dino.name+'\n','')
            if del_instance:
                dino.delete()
            print(f"REMOVED {dino.name}")
        with open(cls.file_path, 'w', encoding='utf-8') as f:
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
    def updateDinos(cls,limit=-1):
        c = 0
        with open(cls.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        
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
                    Dbh.commit()
                else:
                    to_remove.append(new_dino)
            else:
                print(f"{dino.name} EXISTS.")
        
        cls.removeFromFile(to_remove,del_instance=False)
        cls.updateList()

    def __init__(self,dino_name):
        self.name = dino_name
        self.link_pl = None
        self.link_en = None
        self.image_url = None
        self.setTiers([random.randint(0,4) for _ in range(4)])
        self.is_random = True
        self.discovered = False

    def setTiers(self,tierlist):
        if len(tierlist) == 4:
            self.damage_tier, self.defense_tier, self.speed_tier, self.health_tier = tierlist
        elif len(tierlist) == 5:
            self.damage_tier, self.defense_tier, self.speed_tier, self.health_tier, self.tierlist = tierlist
        self.tier = round((sum(tierlist)+len(tierlist))/len(tierlist))
        self.is_random = False

    def setup(self):
        self.link_pl = checkURL('https://pl.wikipedia.org/wiki/'+self.name,suff='_(dinozaur)')
        self.link_en = checkURL('https://en.wikipedia.org/wiki/'+self.name,suff='_(dinosaur)')

        query = self.name
        if len(query) <= 6:
            query += " dinosaur"
        try:
            img_url = get_google_img(query)
            self.image_url = img_url
        except:
            pass

    def text(self):
        return f"[DINO {self.name}] Discovered: {self.discovered}\ndamage: {self.damage_tier}\ndef: {self.defense_tier}\nspeed: {self.speed_tier}\nhp: {self.health_tier}"

    def print(self):
        print(self.text())

    def discover(self):
        self.discovered = True

    def getPartsRequired(self):
        return StaticPart.getPart(self.name)

    def getPartsOwned(self, profile):
        po = {}
        self_part_ids = Dbh.session.query(StaticPart.id).filter(StaticPart.dino_name == self.name)
        profile_parts = Dbh.session.query(ProfilePart).filter(ProfilePart.profile_id == profile.id, ProfilePart.part_id in self_part_ids).group_by(ProfilePart.part_id).all()
        
        return profile_parts
        
    def isValid(self):
        if self.image_url and (self.link_en or self.link_en):
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