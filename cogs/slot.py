import discord
from discord.ext import commands
import asyncio
import random
import itertools
 
class SlotSlot():
    def __init__(self,emojis,rows):
        self.rolls = random.randint(1,10)
        self.emojis = random.sample(emojis,len(emojis))
        self.baselen = len(self.emojis)
        while len(self.emojis) < self.rolls+rows+2:
            self.emojis += self.emojis
        self.current_idx = 0
        self.is_done = False
       
       
    def getEmoji(self,ido=0):
        return self.emojis[self.current_idx+ido]
       
    def next(self):
        if self.current_idx == self.rolls:
            self.is_done = True
            return
        self.current_idx += 1
 
class SlotSettings:
    def __init__(self):
        self.show_progress = True
        self.sleeptime = 0.9
       
class Slot(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.ingame = []
       

    @commands.command(name='say')
    async def _say(self,ctx):
        e = discord.Embed(description="<:zwykly_miecz:551107373775847427> x22")
        m = await ctx.send(embed=e)
        await m.add_reaction("<:zwykly_miecz:551107373775847427>")
    @commands.command(name='slot')
    async def slot_game(self,ctx,slots=3, difficulty= 7):
        if int(slots) > 10 or int(slots) < 2 or ctx.message.author.id in self.ingame or int(difficulty) < 2 or int(difficulty) > len(ctx.message.guild.emojis):
            await ctx.send(f"{ctx.message.author.mention} Spierdalaj.")
            return
        settings = SlotSettings()
        if len(self.ingame) == 2:
            settings.sleeptime = 1.8
        elif len(self.ingame) > 2:
            settings.show_progress = False
        self.ingame.append(ctx.message.author.id)
        emojis = random.sample(ctx.message.guild.emojis,difficulty)
        slots = [SlotSlot(emojis,2) for _ in range(int(slots))]
        header = f"{ctx.message.author.mention} SLOT 🎰\n"
        message = None
        row0 = ''
        row1 = ''
        row2 = ''
        row2 = ''
        row3 = ''
        row4 = ''
        text = ''
        go = True
        while go:
            if self.slotsDone(slots):
                go = False
            row0 = self.printRow(slots,2)
            row1 = self.printRow(slots,1)
            row2 = self.printRow(slots,sep="`█`")
            row2 = f"{row2} ⬅️ {self.getSummary(ctx,slots)}"
            row3 = self.printRow(slots,-1)
            row4 = self.printRow(slots,-2)
            text = "\n".join((row0,row1,row2,row3,row4))
            #text += "\n Win chance: " + self.getWinChange(slots)
           
            if settings.show_progress:
                if message is None:
                    message = await ctx.send(header+text)
                else:
                    await message.edit(content=header+text)#+self.printSlotEmojis(slots)
                await asyncio.sleep(settings.sleeptime)
            for slot in slots:
                slot.next()
        if settings.show_progress == False:
            await ctx.send(header+text)
        self.ingame.remove(ctx.message.author.id)
       
    def printRow(self,slots,offset=0,sep="` `"):
        return sep + sep.join([str(slot.getEmoji(offset)) for slot in slots]) + sep
    def slotsDone(self,slots):
        for slot in slots:
            if not slot.is_done:
                return False
        return True
    def isWin(self,slots):
        if len(set([slot.getEmoji() for slot in slots])) == 1:
            return True
        return False
    def printSlotEmojis(self,slots):
        t = "\n"
        for slot in slots:
            t += "".join(str(e) for e in slot.emojis) + "\n"
        return t
           
    def getSummary(self,ctx, slots):
        if not self.slotsDone(slots):
            return "❓"
        if self.isWin(slots):
            return f"🏆 {ctx.message.author.mention} Won a slot. 🎉 @everyone"
        else:
            return "❌ Unfortunate."
    def getWinChange(self,slots):
        s = 100
        for slot in slots:
            s *= 1/slot.baselen
     
        return f"{s:.6f}%"
def setup(bot):
    bot.add_cog(Slot(bot))