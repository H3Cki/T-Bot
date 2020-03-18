import discord
from discord.ext import commands   
   
class Slot(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        
        
    @commands.command()
    async def getguildemojis(self,ctx):
        t = ''
        for emoji in ctx.message.guild.emojis:
            t+= f"`<:{emoji.name}:{emoji.id}>`\n"
            print(str(emoji))
        await ctx.send(t)
        
    
def setup(bot):
    bot.add_cog(Slot(bot))