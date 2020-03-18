from ..resources import ResourcesBase
import asyncio
from ..guild_settings import JGuildSettings as JGS
from .droppable import Droppable
import discord
from ..discovery import Discovery
from ...utils.dbconnector import DatabaseHandler as Dbh

class Requirement:
    def __init__(self,item,count=1):
        self.item = item
        self.count = count
    
class Requirements:
    def __init__(self,list_of_tuples=[]):
        self.req = []
        for tup in list_of_tuples:
            self.req.append(Requirement(tup[0],tup[1]))


    def requirementsMet(self,profile,noex=False,boolean=False):
        owneds = []
        exceptions = ["Not enough: "]
        for r in self.req:
            owned = r.item.__class__.DROPS_AS.get(profile_id=profile.id,entity_id=r.item.entity_id)
            if owned:
                owned = owned[0]
                if not (owned.count >= r.count):
                    exceptions.append(f"{r.item.briefText} {owned.count}/{r.count}")
                owneds.append(owned)
            
        if len(owneds) != len(self.req) and noex==False:
            raise Exception("\n".join(exceptions))
        
        if boolean:
            return len(owneds) == len(self.req)
        else:
            return owneds if len(owneds) == len(self.req) else False

    def compareAsText(self,profile,blank=True,only_emoji=True):
        blank = '<:blank:551400844654936095>' if blank == True else ' '
        txts = []
        for r in self.req:
            owned = r.item.__class__.DROPS_AS.get(profile_id=profile.id,entity_id=r.item.entity_id)
            
            if owned:
                owned = owned[0]
                owned_n = owned.count
            else:
                owned_n = 0
            extra = '' if owned_n >= r.count else 'void'
            name = r.item.name.capitalize() if only_emoji == False else ''
            txts.append(f"{r.item.getEmoji(extra=extra)}{name} {owned_n}/{r.count}")
            
        return blank.join(txts)

class Buildable:
    BUILD_REQUIREMENTS = Requirements()
    BUILD_COST = ResourcesBase()
    
    def buildRequirements(self):
        return self.__class__.BUILD_REQUIREMENTS
    
    def buildCost(self):
        return self.__class__.BUILD_COST
    

    def _build(self, profile,lab=None):
        br = self.buildRequirements()
        bc = self.buildCost(profile.guild_id,lab)
        
        owned_items = br.requirementsMet(profile)
        
        if owned_items and profile.resources > bc:
            for owned_item, req_item in zip(owned_items,br.req):
                owned_item.count -= req_item.count
            resources = profile.resources
            resources -= bc
        else:
            raise Exception(f"Not enough resources or parts")
            

    @staticmethod
    async def buildEvent(profile, items, **kwargs):
        member = profile.member
        gs = kwargs.get('gs', None) or JGS.get(member.guild.id)
        lab = kwargs.get('lab', None)
        successfully_built =  []
        unsucces_built = []
        for item in items:
            try:
                item._build(profile,lab)
                successfully_built.append(item)
            except Exception as e:
                unsucces_built.append(item)
                continue
                
        if successfully_built:
            drop = await Droppable.dropEvent(member,profile,items=successfully_built)
            
            for d in drop:
                if d.TYPE == 'dino':
                    if not d.isDiscovered(member.guild.id):
                        di = Discovery(d.name,profile.id,profile.guild_id)
                        Dbh.session.add(di)
                        await gs.send(content=f'New discovery by {member.display_name}!',embed=d.getEmbed())
            Dbh.commit()
        if unsucces_built:
            await gs.send(embed=Buildable.unsuccessfulEmbed(unsucces_built))

    @staticmethod
    def unsuccessfulEmbed(items):
        texts = []
        for item in set(items):
            count = items.count(item)
            count_t = f"x{count}" if count > 1 else ""
            texts.append(f'{item.briefText} {count_t}')
        return discord.Embed(title="Some items can't be built",description="\n".join(texts),color=discord.Color.from_rgb(255,0,0))