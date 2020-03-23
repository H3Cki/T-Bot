import discord
from datetime import datetime, timedelta
import random
import asyncio

from .jurassicprofile import JurassicProfile as JP
from .dino_info import StaticDino, DinoPart
from .discovery import Discovery
from .resources import Rewards
from ..utils.dbconnector import DatabaseHandler as Dbh
from .guild_settings import JGuildSettings
from .embeds import *
from .entities.droppable import Droppable


class voiceStateUpdateHandler:
    def __init__(self,member,before,after,jcog):
        self.member = member
        self.before = before
        self.after  = after
        self.bot = jcog.bot
        self.jcog = jcog

    
    async def handle(self):
        if not self.after.channel:
            return
        if self.after.channel == self.before.channel:
            return
        
        if self.member.guild.id not in self.jcog.visitors.keys():
            self.jcog.visitors[self.member.guild.id] = {}
        if self.member.id not in self.jcog.visitors[self.member.guild.id].keys():
            self.jcog.visitors[self.member.guild.id][self.member.id] = []
        
            
            
        if self.after.channel.id in self.jcog.visitors[self.member.guild.id][self.member.id]:
            return
        
        self.jcog.visitors[self.member.guild.id][self.member.id].append(self.after.channel.id) ###################################################
        
        static_dino = StaticDino.getDinoFromChannelName(self.after.channel.name)
        
        nostorage = False
        
        drops = []
        gs = JGuildSettings.get(self.member.guild.id)
        if not gs.active or self.after.channel.category_id != gs.voice_cat:
            return
            
        if static_dino:
            channel = self.after.channel
            
            
            #if self.before.channel:
                #await self.member.move_to(self.before.channel)
            
            #await asyncio.sleep(3)
            
            try:
                members = self.after.channel.members
            except:
                return
            #try:
                #await self.after.channel.delete()
            #for member in members:
            member = self.member
            l = DinoPart.get(as_list=True,dino_name=static_dino.name)
            
            rang = random.randint(1,3)
            rang = rang*2 if random.uniform(0,1) < 0.1 else rang
            reward = [static_dino,] if random.uniform(0,1) < 0.1 else [random.choice(DinoPart.get(as_list=True,dino_name=static_dino.name)) for _ in range(rang)]
            profile = JP.get(member)
            drop = await Droppable.dropEvent(member,profile,items=reward)
            
            
            for d in drop:
                if isinstance(d,StaticDino):
                    if not d.isDiscovered(member.guild.id):
                        di = Discovery(d.name,profile.id,profile.guild_id)
                        Dbh.session.add(di)
                        await gs.send(content=f'New discovery by {member.display_name}!',embed=d.getEmbed())
                            
            Dbh.commit()
            try:
                await asyncio.sleep(5)
                await channel.delete()
            except:
                pass
                
                
        