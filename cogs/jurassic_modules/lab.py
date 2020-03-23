from .dino_info import StaticDino, ProfileDinoPart, DinoStatEmojis as DSE
import discord
import random
import asyncio
from ..utils.general import splitList
from math import ceil

class Lab:
    
    MAX_CAPACITY = 16
    
    CONTROLS = {
        'prev' : u'◀',
        'next' : u'▶',
        'reload': u'🔃',
        'stop' : u'⏹'
    }
    
    
    
    def __init__(self,profile,cog=None,naked=False):
        self.profile = profile
        self.cog = cog
        
        self.parts = ProfileDinoPart.get(profile_id = profile.id)
        self.dinos_with_parts = []
        
        for part in self.parts:
            part = part.entity
            dino = StaticDino.get(name=part.dino_name)
            if dino not in self.dinos_with_parts:
                self.dinos_with_parts.append(dino)
              
        
              
        self.cost_multiplier = round(1 + ((len(self.dinos_with_parts)-self.MAX_CAPACITY))/4,1) if len(self.dinos_with_parts) > self.MAX_CAPACITY else 1
        self.cost_multiplier_perc = (self.cost_multiplier*100)-100
        
        
        if self.cog:
            self.dinos_with_parts = list(sorted(self.dinos_with_parts,key = lambda x: (self.cog.isDinoLive(profile.guild,profile.member,x.name), x.buildRequirements().requirementsMet(self.profile,noex=True,boolean=True), self.profile.resources > x.buildCost(self.profile.guild_id,self)), reverse=True))
        
        if naked == False:
            self.dino_split_list = splitList(self.dinos_with_parts,8)
            self.page_idx = 0
            self.total_pages = len(self.dino_split_list)
 
    
    def getList(self):
        return self.dino_split_list[self.page_idx] if self.total_pages else self.dino_split_list
    
    async def start(self,ctx):
        embed = self.getEmbed(self.getList())
        msg = await ctx.send(embed=embed)
        if len(self.dino_split_list) <= 1:
            return
        await msg.add_reaction(Lab.CONTROLS['prev'])
        await msg.add_reaction(Lab.CONTROLS['next'])
        await msg.add_reaction(Lab.CONTROLS['reload'])
        await msg.add_reaction(Lab.CONTROLS['stop'])
        
        def check(reaction, user):
            return user.id == ctx.message.author.id and reaction.message.id == msg.id
        
        while True:
            try:
                reaction, user = await self.cog.bot.wait_for('reaction_add', check=check, timeout=35.0)
            except:
                break
            if reaction.emoji == Lab.CONTROLS['stop']:
                await msg.delete()
                return
            if reaction.emoji == Lab.CONTROLS['reload']:
                pass
            
            starting_page_idx = self.page_idx
            
            if reaction.emoji == Lab.CONTROLS['next']:
                self.page_idx = self.page_idx + 1 if self.page_idx < self.total_pages - 1 else self.page_idx
            if reaction.emoji == Lab.CONTROLS['prev']:
                self.page_idx = self.page_idx - 1 if self.page_idx > 0 else self.page_idx
            
            if self.page_idx != starting_page_idx or reaction.emoji == Lab.CONTROLS['reload']:
                embed = self.getEmbed(self.getList())
                await msg.edit(embed=embed)
                await msg.remove_reaction(reaction.emoji,ctx.message.author)
        
        
        
    def getEmbed(self,dinos):
        
        
        desc = None
        if self.cost_multiplier > 1:
            desc = f'❗ Laboratory is overloaded, resource cost is increased by {self.cost_multiplier_perc}%'
        embed = discord.Embed(title = f"LABORATORY - {len(self.dinos_with_parts)} Dinosaurs" ,description=desc,color=discord.Color.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        embed.set_author(name=self.profile.member.display_name,icon_url=self.profile.member.avatar_url_as(format='png'))
        embed.set_thumbnail(url='https://i.imgur.com/s1xRSYT.png')
        
        texts = []
        for dino in dinos:
            
            if dino.isDiscovered(self.profile.guild_id):
                stats_txt = f'`🔥` {dino.stats_as_string()}\n'
                emoji = DSE.emojis['dino1']
                tier = f" T{dino.tier}"
            else:
                stats_txt = ''
                emoji = '❓'
                tier = ''
            
            islive = self.cog.isDinoLive(self.profile.guild,self.profile.member,dino.name) if self.cog else None
            if islive:
                ilt = "  ⏰ LIVE!"
            else:
                ilt = ""
                    
            build_cost = dino.buildCost(self.profile.guild_id,self)
            requirs = dino.buildRequirements()
        
            buildables = [requirs.requirementsMet(self.profile,noex=True,boolean=True),self.profile.resources > build_cost]
            
            reqs = requirs.compareAsText(self.profile)
            reqs_txt = f"`🔸` {reqs}"
            bc = build_cost.compareAsText(self.profile.resources)
            bc_txt = f"\n`🔺` {bc}"
            
            
            if all(buildables):
                build_txt = '\n<:blank:551400844654936095><:high:551205365526691841> Buildable!'
            elif buildables[0]:
                build_txt = '\n<:blank:551400844654936095><:mid:551402984974581763> Not enough resources'
            elif buildables[1]:
                build_txt = '\n<:blank:551400844654936095><:mid:551402984974581763> Missing parts'
            else:
                build_txt = ''
            
            embed.add_field(name=f"{emoji} {dino.name.upper()}{tier}"+ilt,value=stats_txt+reqs_txt+bc_txt+build_txt,inline=False)
        
        warning = f'\n❗ After exceeding {self.MAX_CAPACITY} slots build cost for all dinos will be increased' if len(self.dinos_with_parts) > self.MAX_CAPACITY - 5 else ''
        legend = '\n`🔥` Stats\n`🔸` Parts required\n`🔺` Resources required'
        page_txt = f'[Page: {self.page_idx+1}/{self.total_pages}]\n' if len(self.dino_split_list) > 1 else ''
        embed.set_footer(text=f'{page_txt}Use command !build to build a dino.'+legend+warning)
        return embed
    
    
    
                    
                
                    
                
