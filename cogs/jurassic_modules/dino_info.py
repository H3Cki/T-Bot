import discord
import random
from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean, insert

import requests
from bs4 import BeautifulSoup

from threading import Thread
import selenium.webdriver as webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

from ..utils.dbconnector import DatabaseHandler as Dbh
from .discovery import Discovery
from .entities.entity import Entity, ProfileEntity
from .part_info import StaticPart


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

class ProfileDino(ProfileEntity):
    TYPE = "profile_dino"
    ENTITY_TYPE = "dino"
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = TYPE
    parent = Column(Integer, ForeignKey(ProfileEntity.entity_id))
    
    id = Column(Integer, primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity' : TYPE
    }

class StaticDino(Entity):
    
    # CLASS ATTRIBUTES --------------------- #
    
    FILE_PATH = 'data/dinos.txt'
    TYPE   = "dino"
    NAME   = "Dinosaur"
    EMOJI  = '🦖'
    TIERED = True
    driver = None
    
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = TYPE
    
    parent = Column(Integer, ForeignKey(Entity.entity_id))

    name = Column(String, primary_key=True)
    link_pl = Column(String)
    link_en = Column(String)
    image_url = Column(String)
    other_image_urls = Column(String)
    description = Column(String)
    facts = Column(String)
    damage = Column(Integer)
    defense = Column(Integer)
    speed = Column(Integer)
    health = Column(Integer)
    tier = Column(Integer)
    is_random = Column(Boolean)
    
    __mapper_args__ = {
        'polymorphic_identity' : TYPE
    }
    
    
    def __init__(self,dino_name):
        self.name = dino_name
        self.is_random = True

    @property
    def other_image_urls_list(self):
        return self.other_image_urls.split(' ')

    @property
    def facts_list(self):
        return self.facts.split('\n')

    def randomizeStats(self):
        self.damage = random.randint(1,200)
        self.defense = random.randint(1,200)
        self.health = random.randint(1,200)
        self.speed = round(random.uniform(0.0,2.0),2)
        self.tier = random.randint(1,5)
    
    def setWikiLinks(self):
        self.link_pl = checkURL('https://pl.wikipedia.org/wiki/'+self.name)
        self.link_en = checkURL('https://en.wikipedia.org/wiki/'+self.name)
        
    def getImageUrls(self):
        return self.__class__.getDinoImageUrls(self.name)
    
    def setImageUrls(self):
        urls = self.__class__.getDinoImageUrls(self.name)
        self.image_url = urls[0]
        if len(urls) > 1:
            self.other_image_urls = " ".join(urls[1:])
    
    def setFacts(self):
        facts = self.__class__.getDinoFacts(self.name)
  
        
    def setDescription(self):
        self.description = self.__class__.getDinoFacts(self.name)
    
        
    def setup(self):
        self.setWikiLinks()
        self.setImageUrls()
        self.setDescription()
        self.setFacts()
        self.randomizeStats()

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

    def getEmbed(self,descr=True):
        if self.is_random:
            r = "RANDOM"
        else:
            r = "SET"
        d = f"STATS: {r}\nDamage: {self.damage}\nDefense: {self.defense}\nSpeed: {self.speed}\nHealth: {self.health}\n**Overall Tier: {self.tier}**"
        if descr:
            if self.description:
                d += f'\n[Facts]\n' + self.description
            if self.facts:
                d += f'\n' + '\n-'.join(self.facts_list)
        e = discord.Embed(title=f'🦖 {self.name.capitalize()} <- more info',description=d, url= self.getValidUrl(), color=discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        e.set_image(url=self.image_url)
        e.set_footer(text=f"{len(self.other_image_urls_list)} replacement images available.")
        return e
    
    def isDiscovered(self,guild_id):
        guild_discs = Discovery._getAllInGuild(guild_id)
        return guild_discs.filter(Discovery.dino_name == self.name).first()

    @classmethod
    def getDinoFacts(cls,query):
        html = cls.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        ul = soup.findAll("ul")
        
        if len(ul) > 2:
            facts = ul[0].findAll('li')
            facts = '\n'.join([fact.text for fact in facts])
            print(facts)
            return facts
        
    @classmethod
    def getDinoDescription(cls,query):
        html = cls.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        desc = soup.find("p")
        print(desc)
        return desc.text
    
    @classmethod
    def getDinoImageUrls(cls,query):
        q = query.capitalize()
        url = f"https://dinosaurpictures.org/{q}-pictures"
        
        if not cls.driver:
            cls.driver = webdriver.Firefox()
        
        cls.driver.get(url)
        builder = ActionChains(cls.driver)
        
        elems = cls.driver.find_elements_by_xpath(f'//*[@title="{q}"]')
        images = [e.get_attribute('src') for e in elems]

        while 'https://i.imgur.com/Vmxsx1H.gif' in images:
            print(f"IMAGES LOADING")
            time.sleep(0.5)
            elems = cls.driver.find_elements_by_xpath(f'//*[@title="{q}"]')
            for elem in elems:
                y = elem.location['y']
                cls.driver.execute_script(f"window.scrollTo(0, {y});")
            images = [e.get_attribute('src') for e in elems]
        
        return images

    

    @classmethod
    def getSetTierDinos(cls,tier_idx):
        al = cls.getSetDinos()
        return [dino for dino in al if dino.tier == tier_idx]

    @classmethod
    def getRandomDinoTierWise(cls,pool=None):
        return random.choice(cls.getAll())
        found = False
        al = pool or cls.getSetDinos()
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
        return Dbh.session.query(cls).filter(cls.name == dino_name).first()
    
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

        if cls.driver:
            cls.driver.close()
        cls.removeFromFile(to_remove,del_instance=False)
        Dbh.session.commit()

    
