import asyncio
from discord import Embed
from .entities.entity import ProfileEntity


class JMap:
    def __init__(self,ctx,bot):
        self.bot    = bot
        self.ctx    = ctx
        self.guild  = ctx.message.guild
        self.author = ctx.message.author
        self.author_profile = JP.getProfile(self.author)
        self.message = None
        self.profiles = sorted(JP.getAll(self.guild.id), key = lambda x: x.id)
    
    async def display(self):
        await self.ctx.send(embed=self.embed)
    
    @property  
    def embed(self):
        desc_cont = ""
        
        e = Embed(title='JURASSIC MAP')
        e.set_thumbnail(url='https://i.imgur.com/jujvDF8.jpg')
        for i,profile in enumerate(self.profiles):
            idx = i+1
            member = profile.member
            text = f"Power: {ProfileEntity.valueOfProfile(profile)}"
            e.add_field(name=f"`{idx} 🗺️` {member.display_name}",value=text,inline=True)
        return e
    
        
        