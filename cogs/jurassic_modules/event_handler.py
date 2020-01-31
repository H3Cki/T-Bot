from .jurassicprofile import JurassicProfile as JP
from .dino_info import StaticDino
from .discovery import Discovery
from .part_info import StaticPart
from ..utils.dbconnector import DatabaseHandler as Dbh
from .guild_settings import JGuildSettings
import discord

def dropEmbed(member,static_part):
    return discord.Embed(title=member.display_name,description=f'{static_part.getEmoji()} **{static_part.dino_name.capitalize()}** {static_part.type}')

def discoveryEmbed(member,static_dino):
    de = static_dino.getEmbed()
    de.set_footer(text=f'New discovery by {member.display_name}')
    return de

def dinoDropEmbed(member,dino):
    de = dino.getEmbed()
    return de

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
        
        if self.member.id not in self.jcog.visitors.keys():
            self.jcog.visitors[self.member.guild.id] = {}
            self.jcog.visitors[self.member.guild.id][self.member.id] = []
            
        if self.after.channel.id in self.jcog.visitors[self.member.guild.id][self.member.id]:
            return
        
        self.jcog.visitors[self.member.guild.id][self.member.id].append(self.after.channel.id)
        
        static_dino = StaticDino.getDinoFromChannelName(self.after.channel.name)
        
        if static_dino:
            gs = JGuildSettings.get(self.member.guild.id)
            if not gs.active:
                return
            
            profile = JP.getProfile(self.member)
            if not profile:
                profile = JP(self.member.id,self.member.guild.id)
                Dbh.session.add(profile)

            dropped, static = StaticPart.drop(static_dino,profile)
            if dropped:
                profile.addExp(1)
                if gs.notify and gs.j_notif_channel:
                    channel = self.bot.get_channel(gs.j_notif_channel)
                    await channel.send(embed=dropEmbed(self.member,static))

                     
            dino = profile.buildDino(static_dino)
            if dino:
                if gs.notify and gs.j_notif_channel:
                    channel = self.bot.get_channel(gs.j_notif_channel)
                        
                if not static_dino.isDiscovered(self.member.guild.id):
                    disc = Discovery(static_dino.name,profile.id,profile.guild_id)
                    profile.addExp(5)
                    Dbh.session.add(disc)
                    
                    if channel:
                        await channel.send(embed=discoveryEmbed(self.member,static_dino))

                if channel:  
                    e = dinoDropEmbed(self.member, dino)
                    e.set_thumbnail(url=static_dino.image_url)
                    try:
                        await self.member.send(self.member.mention,embed = e)
                    except:
                        await channel.send(self.member.mention,embed = e)
            
        Dbh.commit()