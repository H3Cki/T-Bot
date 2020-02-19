import discord
from datetime import datetime, timedelta
import random


from .jurassicprofile import JurassicProfile as JP
from .dino_info import StaticDino
from .discovery import Discovery
from .part_info import StaticPart
from .resources import Rewards
from ..utils.dbconnector import DatabaseHandler as Dbh
from .guild_settings import JGuildSettings
from .embeds import *

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
        
        self.jcog.visitors[self.member.guild.id][self.member.id].append(self.after.channel.id)
        
        static_dino = StaticDino.getDinoFromChannelName(self.after.channel.name)
        
        nostorage = False
        
        drops = []
        
        if static_dino:
            
            
            gs = JGuildSettings.get(self.member.guild.id)
            if not gs.active:
                return
            
            profile = JP.getProfile(self.member)
            if not profile:
                profile = JP(self.member.id,self.member.guild.id)
                Dbh.session.add(profile)



            # #DROP CHEST
            # if random.uniform(0,100) < 8:
            #     chest = DinoChest(profile,StaticDino.getRandomSetDinoTierWise())
            #     drops.append(chest)
            #     Dbh.session.add(chest)
            #     #await ctx.send(ctx.message.author.mention,embed=itemDropEmbed(target,chest))

    
    
            dropped, static = StaticPart.drop(static_dino,profile)
            if dropped:
                dwp = profile.getDinosWithParts()
              
                if static_dino not in dwp and len(dwp) >= 10:
                    nostorage = True
                    
                    above_perc = ((100*(len(dwp)-10))/10)/2
                    if random.uniform(0.1,100) <= above_perc:
                        await gs.send(embed=destructionEmbed(self.member))
                        profile.eraseAllParts()
                        Dbh.session.commit()
                        return 
                profile.addExp(1)
                drops.append(static)
                #await gs.send(embed=dropEmbed(self.member,static,nostorage))
                Dbh.session.add(dropped)
                     
            
            
            await gs.send(embed=itemDropEmbed(self.member,drops,nostorage))         
            dino = profile.buildDino(static_dino)
            if dino:
                if not static_dino.isDiscovered(self.member.guild.id):
                    disc = Discovery(static_dino.name,profile.id,profile.guild_id)
                    profile.addExp(5)
                    Dbh.session.add(disc)
                    reward = Rewards.rewards['discovery']
                    profile.resources.addResources(reward)
                    await gs.send(embed=discoveryEmbed(self.member,static_dino))

                
                e = dino.getEmbed()
                e.set_thumbnail(url=static_dino.image_url)
                try:
                    await self.member.send(embed = e)
                except:
                    await gs.send(self.member.mention,embed = e)
            
        Dbh.commit()