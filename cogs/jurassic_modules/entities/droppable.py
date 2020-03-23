from .entity import ProfileEntity
import discord
from datetime import datetime, timedelta
from ...utils.dbconnector import DatabaseHandler as Dbh
from ..guild_settings import JGuildSettings as JGS
import random


class Droppable: #Doesnt work when not inherited by class that inherits from Entity
    
    DROPS_AS = ProfileEntity
    SECRET_DROP = False
    
    async def _dropEvent(self,member,profile,**kwargs):
        count = kwargs.get('count', 1)
        self._drop(profile,count)
        embed = self.dropEmbed(member, count)
        gs = kwargs.get('gs', None) or JGS.get(member.guild.id)
        await self.__class__.sendEmbed(member,embed,gs)
            
    def _drop(self, profile, count=1):
        self.__class__.DROPS_AS.add(profile,self,count)
            
    def dropEmbed(self,member,count=1):
        base = self.__class__.baseEmbed(member)
        c = str(count) if count > 1 else ''
        base.description = f"{self.briefText} {c}"
        return base
    

    @classmethod
    async def sendEmbed(cls,member,embed,gs):
        if cls.SECRET_DROP:
            await member.send(embed=embed)
        else:
            await gs.send(embed=embed)
        
    @classmethod
    async def dropEvent(cls,member,profile,**kwargs):
        
        items = kwargs.get('items', None)
        if not items:
            count = kwargs.get('count', 1)
            items = []
            for _ in range(count):
                items.append(cls.selectForDrop())

        embed = cls.combinedDropEmbed(member,items)
        gs = kwargs.get('gs', None) or JGS.get(member.guild.id)
        
        for item in items:
            item._drop(profile)
        if not kwargs.get('silent',None):
            await cls.sendEmbed(member,embed,gs)
        
        return items
        
    @classmethod
    def selectForDrop(cls):
        return random.choice(cls.get())
        
    @classmethod
    def baseEmbed(cls,member):
        e = discord.Embed(title=f"Drop for {member.display_name}",description='')
        footer = str((datetime.now()+timedelta(hours=1)).time())[:5] + " Check !lab."
        e.set_footer(text=footer)
        return e
        
    @classmethod
    def combinedDropEmbed(cls,member,static_items=[]):
        base = cls.baseEmbed(member)
        for item in list(set(static_items)):
            c = " x"+str(static_items.count(item)) if static_items.count(item) > 1 else ''
            base.description += f'{item.briefText}{c}\n'
        return base
    
    
        
    