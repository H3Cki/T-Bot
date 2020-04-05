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
       
class Slot:
    ingame = []
    
    def __init__(self,emojis,cc=[],ccs=[]):
        self.emojis = emojis
        self.custom_conditions = cc
        self.custom_conditions_sets = ccs
        self.winner = []

    async def slot_game(self,ctx,payment_info='SLOT 🎰'):
        if ctx.message.author.id in self.__class__.ingame:
            await ctx.send(f'{ctx.message.author.mention} Fuck off nigga.')
            return {'message':None,'winner':self.winner}
        slots = 3
        difficulty = 4
        settings = SlotSettings()
        if len(self.__class__.ingame) == 2:
            settings.sleeptime = 1.8
        elif len(self.__class__.ingame) > 2:
            settings.show_progress = False
        self.__class__.ingame.append(ctx.message.author.id)
        emojis = random.sample(self.emojis,difficulty)
        slots = [SlotSlot(emojis,2) for _ in range(int(slots))]
        header = f"{ctx.message.author.mention} {payment_info}\n"
        message = None
        row0 = ''
        row1 = ''
        row2 = ''
        row2 = ''
        row3 = ''
        row4 = ''
        text = ''
        go = True
        message = None
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
        self.__class__.ingame.remove(ctx.message.author.id)
        return {'message':message,'winner':[slot.getEmoji() for slot in slots]}
    def printRow(self,slots,offset=0,sep="` `"):
        return sep + sep.join([str(slot.getEmoji(offset)) for slot in slots]) + sep
    def slotsDone(self,slots):
        for slot in slots:
            if not slot.is_done:
                return False
        return True
    def isWin(self,slots):
        es = [slot.getEmoji() for slot in slots]
        e_set = set(es)
        if len(e_set) == 1 or e_set in self.custom_conditions_sets or es in self.custom_conditions:
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
            return f"🏆 {ctx.message.author.mention} Won a slot. 🎉"
        else:
            return "❌ Unfortunate."
    def getWinChange(self,slots):
        s = 100
        for slot in slots:
            s *= 1/slot.baselen
     
        return f"{s:.6f}%"
    
