import discord
import random
from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean, insert

import requests
from bs4 import BeautifulSoup

from threading import Thread
import selenium.webdriver as webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

from ..utils import imageutils
from ..utils.dbconnector import DatabaseHandler as Dbh
from .discovery import Discovery
from .entities.entity import Entity, ProfileEntity
from .entities.droppable import Droppable
from .entities.buildable import *
from .tiers import getTier
from .resources import ResourcesBase

def checkURL(url):
    req = requests.get(url)
    if req.status_code == 200:
        return req.history[-1].url

    return None

class DinoStatEmojis:
    emojis = {
        'damage' : '<:dino_damage:679747583291293734>',
        'armor': '<:dino_defense:679745488517464120>',
        'speed'  : '<a:dino_speed:679745488521920581>',
        'health' : '<a:dino_health:679745488517464125>',
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



class StaticDino(Entity,Droppable, Buildable):
    # Droppable ATTRIBUTES ----------------- #
    DROPS_AS = ProfileDino
    SECRET_DROP = False
    
    
    # CLASS ATTRIBUTES --------------------- #
    FILE_PATH = 'data/dinos.txt'
    TYPE   = "dino"
    NAME   = "Dinosaur"
    EMOJI  = '🦖'
    TIERED = True
    driver = None
    
    BASE_BUILD_COST = [400,200,50]
    
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = TYPE
    
    parent = Column(Integer, ForeignKey(Entity.entity_id))

    name = Column(String, primary_key=True)
    link_pl = Column(String)
    link_en = Column(String)
    image_url = Column(String)
    other_image_urls = Column(String,default="")
    map_image_url = Column(String,default="")
    description = Column(String,default="")
    facts = Column(String,default="")
    damage = Column(Integer)
    armor = Column(Integer)
    speed = Column(Integer)
    health = Column(Integer)
    tier = Column(Integer)
    is_random = Column(Boolean, default=True)
    is_image_random = Column(Boolean, default=True)
    
    __mapper_args__ = {
        'polymorphic_identity' : TYPE
    }
    
    
    def __init__(self,dino_name):
        self.name = dino_name
        
    @property
    def power(self):
        return (self.damage + self.armor + self.health) * self.speed
    
    @property
    def other_image_urls_list(self):
        return self.other_image_urls.split(' ')

    @property
    def all_image_urls_list(self):
        others = self.other_image_urls.split(' ')
        others = [self.image_url,] + others
        return others

    @property
    def facts_list(self):
        if not self.facts:
            return ''
        return self.facts.split('\n')
    
    @property
    def facts_list_string(self):
        t = ''
        for fact in self.facts_list:
            t += f"- {fact}\n"
        return t


    def stats_as_string(self,emoji=True):
        return f"{DinoStatEmojis.emojis['damage']}{str(self.damage)}{DinoStatEmojis.emojis['blank']}{DinoStatEmojis.emojis['armor']}{str(self.armor)}{DinoStatEmojis.emojis['blank']}{DinoStatEmojis.emojis['health']}{str(self.health)}{DinoStatEmojis.emojis['blank']}{DinoStatEmojis.emojis['speed']}{str(self.speed)}"

    def buildRequirements(self):
        head = DinoPart.get(dino_name=self.name,type_idx=0)
        meat = DinoPart.get(dino_name=self.name,type_idx=1)
        bones = DinoPart.get(dino_name=self.name,type_idx=2)
        r = Requirements([(head,1),(meat,1),(bones,1)])
        return r

    def buildCost(self,guild_id,lab=None):
        is_discovered = self.isDiscovered(guild_id)
        cost = ResourcesBase(cost=self.__class__.BASE_BUILD_COST)
        if lab:
            cost = cost*lab.cost_multiplier
        if is_discovered:
            return cost*(1/(self.tier/3))
        else:
            return cost

    
    def setImage(self,imurl):
        if imurl == self.image_url:
            return
        if imurl in self.other_image_urls:
            self.other_image_urls = self.other_image_urls.replace(imurl,self.image_url)
        else:
            self.other_image_urls += " " + self.image_url
            
        self.image_url = imurl
        self.is_image_random = False


    def randomizeStats(self):
        self.damage = random.randint(1,200)
        self.armor = random.randint(1,200)
        self.health = random.randint(1,200)
        self.speed = round(random.uniform(0.1,2.0),2)
        self.tier = random.randint(1,5)
    
    
    def setWikiLinks(self):
        self.link_pl = checkURL('https://pl.wikipedia.org/wiki/'+self.name)
        self.link_en = checkURL('https://en.wikipedia.org/wiki/'+self.name)
        
        
    def getImageUrls(self):
        return self.__class__.getDinoImageUrls(self.name)
    
    
    def setImageUrls(self):
        urls = self.__class__.getDinoImageUrls(self.name)
        print(f"URLS: {urls}")
        self.map_image_url = urls[1]
        urls = urls[0]
        if not len(urls):
            return
        self.image_url = urls[0]
        if len(urls) > 1:
            self.other_image_urls = " ".join(urls[1:])
    
    
    def setFacts(self):
        self.facts = self.__class__.getDinoFacts(self.name)
    
    
    def setDescription(self):
        self.description = self.__class__.getDinoDescription(self.name)

        
    def setup(self):
        self.setWikiLinks()
        self.setImageUrls()
        self.setDescription()
        self.setFacts()
        self.randomizeStats()


    ################################################# TO DO BUILDERA CHYBA POWINNO ISC
    async def dropParts(self,member,profile):
        item = DinoPart.selectForDrop(profile,self)
        await DinoPart.dropEvent(member,profile,items=[item,])



    def isValid(self):
        if self.image_url and (self.link_en or self.link_en) and len(self.name) < 16:
            return True
        return False

    def delete(self):
        Dbh.session.delete(self)

    def getValidUrl(self):
        return self.link_pl or self.link_en

    def getEmbed(self,descr=True):
        print(f"SENDING EMBED OF {self.name}")
        if self.is_random:
            r = " [RANDOM]"
        else:
            r = ""
            
        tiers = {1:'1️⃣', 2:'2️⃣', 3:'3️⃣', 4:'4️⃣', 5:'5️⃣'}
        d = f"{tiers[self.tier]} Tier"
        
        color = imageutils.averageColor(self.image_url)
        e = discord.Embed(title=f'🦖 {self.name.capitalize()} <- more info',description=d, url= self.getValidUrl(), color=discord.Colour.from_rgb(color[0],color[1],color[2]))
        
        
        
        e.add_field(name="🔸 Stats"+r,value=self.stats_as_string(),inline=False)
        
        if descr:
            if self.description:
                e.add_field(name="🔸 Description",value=self.description,inline=False)
            if self.facts:
                e.add_field(name="🔸 Quick Facts",value=self.facts_list_string,inline=False)
        
        e.set_image(url=self.image_url)
        e.set_thumbnail(url=self.map_image_url)
        if self.is_image_random:
            e.set_footer(text=f"❗ Image is random, {len(self.other_image_urls_list)} replacement images available.")

            
        return e
    
    def isDiscovered(self,guild_id):
        guild_discs = Discovery.get(guild_id=guild_id,dino_name=self.name)
        return guild_discs

    @classmethod
    def sumStats(cls,dinos,as_text=False):
        stats = [0,0,0,0]
        for dino in dinos:
            stats[0] += dino.damage
            stats[1] += dino.armor
            stats[2] += dino.health
            stats[3] += dino.speed
        stats[3] = round(stats[3]/(len(dinos) or 1))
        if as_text:
            stats = f"{DinoStatEmojis.emojis['damage']}{stats[0]}{DinoStatEmojis.emojis['blank']}{DinoStatEmojis.emojis['armor']}{stats[1]}{DinoStatEmojis.emojis['blank']}{DinoStatEmojis.emojis['health']}{stats[2]}{DinoStatEmojis.emojis['blank']}{DinoStatEmojis.emojis['speed']}{stats[3]}"
        return stats

    @classmethod
    def getDinoFacts(cls,query):
        html = cls.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        ul = soup.findAll("ul")
        
        if len(ul) > 2:
            facts = ul[0].findAll('li')
            facts = '\n'.join([fact.text for fact in facts])
            return facts
        
    @classmethod
    def getDinoDescription(cls,query):
        html = cls.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        desc = soup.find("p")
        return desc.text.replace('\n',' ')
    
    @classmethod
    def getDinoImageUrls(cls,query):
        #return 'https://i.imgur.com/iLkEkLe.jpg' #############
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
            time.sleep(0.2)
            elems = cls.driver.find_elements_by_xpath(f'//*[@title="{q}"]')
            for elem in elems:
                y = elem.location['y']
                cls.driver.execute_script(f"window.scrollTo(0, {y});")
            images = [e.get_attribute('src') for e in elems]
            
        try:
            map_image_url = cls.driver.find_element_by_id('map-image').get_attribute('src')
            and_split = map_image_url.split('&')
            map_image_url = '&'.join(and_split[:-1])
            markers = map_image_url.split('%')
            base_url = markers[0]
            markers.pop(0)
            while len(map_image_url) > 2048:
                markers = markers[1:]
                map_image_url = base_url+"%"+'%'.join(markers)
        except:
            map_image_url = ""
        return (images,map_image_url)

    

        
    
    @classmethod
    def getRandomDinoTierWise(cls,pool=None):
        pool = pool or cls.getAll()
        tier = getTier()
        return random.choice(Dbh.session.query(cls).filter(cls.tier == tier).all())


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
        return cls.get(name=name)
        

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

            dino = cls.get(name=dino_name)
            if not dino:
                new_dino = cls(dino_name)
                print(f"{i+1}/{len(dinos)} SETTING UP '{new_dino.name}'")
                try:
                    new_dino.setup()
                except:
                    to_remove.append(new_dino)
                    continue
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

    
    @classmethod
    def removeFromFile(cls,dinos,del_instance=True):
        
        with open(cls.FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        for dino in dinos:
            Thread(target=DinoPart.removeDinoPartComplelty,args=[dino,]).run()
            content = content.replace(dino.name+'\n','')
            print(f"REMOVING {dino.name}")
            if del_instance:
                dino.delete()
        with open(cls.FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        Dbh.session.commit()
    
    
    
    
    
##############################################################################
#  PARTS HERE BO SIE KURWA NIE DA NORMALNIE IMPORTA ZROBIC JEBANEGO W PIZDU  #
##############################################################################    

class DinoPartTypes:
    HEAD = "head"
    MEAT = "meat"
    BONE = "bones"

    types = [HEAD,MEAT,BONE]
    
    name_to_idx = {
        HEAD : 0,
        MEAT : 1,
        BONE : 2
    }
    
    emojis = {
        HEAD : "<:head:671895266520989781>",
        MEAT : "<:meat:671895522134458378>",
        BONE : "<:bones:672476713334341643>",
        HEAD+"void" : '<:head_void:673959867890794535> ',
        MEAT+"void" : '<:meat_void:673959534783496263> ',
        BONE+"void" : '<:bones_void:673959534661992494> '
    }

class ProfileDinoPart(ProfileEntity):
    TYPE = "profile_dino_part"
    ENTITY_TYPE = "part"
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = TYPE
    parent = Column(Integer, ForeignKey(ProfileEntity.entity_id))
    
    id = Column(Integer, primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity' : TYPE
    }


class DinoPart(Entity,Droppable):
    # CLASS ATTRIBUTES --------------------- #
    DROPS_AS = ProfileDinoPart
    PARENT = StaticDino
    
    TYPE   = "part"
    NAME   = "Dino Part"
    TIERED = False
    
    # MAPPER ATTRIBUTES -------------------- #
    
    __tablename__ = TYPE
    
    
    id = Column(Integer, primary_key=True)
    parent_entity_id = Column(Integer, ForeignKey(PARENT.entity_id))
    dino_name = Column(String)
    type_idx = Column(Integer)
    
    __mapper_args__ = {
        'polymorphic_identity' : TYPE
    }
    

    def __init__(self,dino,type_idx):
        self.parent_entity_id = dino.entity_id
        self.dino_name = dino.name
        self.type_idx = type_idx

    @property
    def name(self):
        return f"**{self.dino_name.capitalize()}** {self.type}"

    @property
    def parent(self):
        print(f"GETTING DINO")

        return StaticDino.get(entity_id=self.parent_entity_id)

    @property
    def briefText(self):
        text = f"{self.emoji} {self.name}"
        return text

    @property
    def type(self):
        return DinoPartTypes.types[self.type_idx]

    @property
    def emoji(self):
        return DinoPartTypes.emojis[self.type]
    
    
    @classmethod
    def selectForDrop(cls,profile,dino):
        dino_parts = dino.getPartsRequired()
        
        if random.randint(0,100) <= 60:
            unowned = []
            for sp in dino_parts:
                if not ProfilePart.getProfileEntity(profile,sp):
                    unowned.append(sp)
        else:
            unowned = dino_parts
        if len(unowned) == 0:
            unowned = dino_parts
            
        return random.choice(unowned)
         
    def getEmoji(self,**kwg):
        return DinoPartTypes.emojis[self.type+kwg.get('extra','')]
    
    @classmethod
    def update(cls, dinolist):
        for dino in dinolist:
            for t in range(0,len(DinoPartTypes.types)):
                part = cls.get(dino_name=dino.name,type_idx=t)
                if not part:
                    p = cls(dino,t)
                    Dbh.session.add(p)
                    print(f"CREATING {p.name}")

        Dbh.session.commit()


    @classmethod
    def removeDinoPartComplelty(cls,dino):
        for ppart in DinoPart.get(dino_name=dino.name):
            Dbh.session.delete(ppart)
            print(f"DELETED {ppart.name}")
        Dbh.session.commit()