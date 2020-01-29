from discord.ext import commands
import discord
import asyncio
#from gtts import gTTS
import random
import os
import math
import time
from datetime import datetime
from datetime import timedelta
import urllib
from difflib import SequenceMatcher
from operator import itemgetter
import aiohttp
import re
from pythonping import ping
from cogs.utils.Book import *
from discord import Webhook, AsyncWebhookAdapter
import aiohttp
#import PIL.ImageGrab

async def foo(text,name,avatar,hook):
    async with aiohttp.ClientSession() as session:
        #webhook = Webhook.from_url(hook, adapter=AsyncWebhookAdapter(session))
        await hook.send(text, username=name,avatar_url=avatar,tts=True)
class MemberBook(Book):
    pass

class Poll:
    polls = {}
    def __init__(self,msg,title,answers):
        Poll.polls[msg.channel.id] = self
        self.title = title
        i = 1
        self.answers = []
        for ans in answers:
            self.answers.append((ans,[],i))
            i+=1
        self.msg = msg
        self.on_timer = False
        self.timer_duration = 0

    def sort_answers(self):

        self.answers = sorted(self.answers, key=itemgetter(1),reverse=True)

    def add_answer(self,msg,answer):
        poll = Poll.polls[msg.id]
        poll.answers.append((answer,[],self.answers[-1][2]+1))
    def remove_answer(self,msg,key):
        poll = Poll.polls[msg.channel.id]
        if key.isdigit():
            key = int(key)
            i = 0
            for ans in self.answers:
                if ans[2] == key:
                    poll.answers.pop(i)
                    break
                i+=1
            
        else:
            for i,answer in enumerate(poll.answers):
                if key in answer:
                    poll.answers.pop(i)
    
    async def end(self,msg,text=""):
        if msg == True or self.msg.author == msg.author: 
            Poll.polls.pop(self.msg.channel.id,None)
            await self.msg.channel.send(self.create_poll_text(text))
        else:
            await self.msg.channel.send("You can't end a poll in this channel.")
            return
    
    def timer_time_left(self):
        delta = round(self.timer["start_time"]+self.timer["duration"]-time.time(),1)
        return delta
    
    def timer_time_left_text(self,mins=" minutes",secs=" seconds"):
        minutes = math.floor(self.timer_time_left()/60)
        seconds = int(self.timer_time_left()%60)
        m_text = ""
        s_text = ""
        if minutes:
            m_text = " {}{}".format(minutes,mins)
        if seconds:
            s_text = " {}{}".format(seconds,secs)
        text = "{}{} left.".format(m_text,s_text)
        
        return text


    async def set_timer(self,msg,timer):
        poll = Poll.polls[msg.channel.id]
        if self.on_timer:
            return
        if poll.msg.author == msg.author: 
            if timer > 300:
                await msg.channel.send("Max timer duration is 300.")
                return
            await poll.msg.channel.send(poll.create_poll_text("Poll will end in {} minutes.".format(timer)))
            self.on_timer = True
            self.timer = {"duration":timer*60,"start_time":time.time()}
            await asyncio.sleep(timer*60)
            if self.on_timer == False:
                return
            self.on_timer = False
            await poll.end(True,"Poll time has ended.")
           
        else:
            await msg.channel.send("You can't edit a poll in this channel.")

    def create_bar(self,answer):
        total_votes = 0
        for ans in self.answers:
            total_votes += len(ans[1])
        total_votes = max([len(a[1]) for a in self.answers])
        if total_votes != 0:
            m = len(answer[1])/total_votes
        else:
            m = 0
        mc = int(20*m)
        return ("■"*mc)+(" "*(20-mc))

    def spacer(self,deff,maxx):
        m = int(maxx) - int(deff)
        if m > 15:
            return "\n"
        return " "*m

    def create_poll_text(self,addon=""):
        self.sort_answers()
        text = "```glsl\n#{}\n".format(self.title)
        longest = len(max([a[0] for a in self.answers], key=len))
        
        #longets_nr = max([len(str(ans[2])) for ans in self.answers])
        longets_nr = 2
        for i,answer in enumerate(self.answers):
            text += "\n{}{}. {}".format(self.spacer(len(str(answer[2])),longets_nr),answer[2],answer[0])
            
            vote_text = "["+self.create_bar(answer)+"]"

            text += "{} - {}{}".format(self.spacer(len(answer[0]),longest),vote_text,len(answer[1]))
        if addon != "":
            addon = "\n#" + addon + "\n"
        if addon == "" and self.on_timer:
            minutes = math.floor(self.timer_time_left()/60)
            seconds = int(self.timer_time_left()%60)
            m_text = ""
            s_text = ""
            if minutes:
                m_text = " {} minutes".format(minutes)
            if seconds:
                s_text = " {} seconds".format(seconds)
            addon = "\n#Time left:{}{}.".format(m_text,s_text)
        text += "\n{}\n-created by {}```".format(addon,self.msg.author.display_name)
        return text
        
    def vote_possible(self,msg,answer):
        if msg.author.id in answer[1]:
            return False
        return True

    async def vote(self,msg,key):
        if msg.channel.id not in Poll.polls:
            await msg.channel.send("No poll in this channel")
            return

        if not key.isdigit(): 
            key_found = False
            for i,answer in enumerate(self.answers):
                if key in answer[0]:
                    key_found = True
                    if self.vote_possible(msg,self.answers[i]):
                        self.answers[i][1].append(msg.author.id)
                        return True
                    else:
                        return False
            if not key_found:
                self.add_answer(msg.channel,key)
                self.answers[-1][1].append(msg.author.id)
                return True
        else:   
            key = int(key)
            ans = self.get_answer_by_id(key)
            if ans:
                if self.vote_possible(msg,ans):
                    ans[1].append(msg.author.id)
                    return True
                else:
                    #await msg.channel.send("You already voted for {}".format(self.answers[key-1][0]))
                    return False

            
      
        return False

    def get_answer_by_id(self,idd):
        for answer in self.answers:
            if answer[2] == int(idd):
                return answer
        return None

    async def vote_clear(self,msg,key=None):
        if msg.channel.id not in Poll.polls:
            await msg.channel.send("No poll in this channel")
            return
        poll = Poll.polls[msg.channel.id]
        try:
            if key == "clear":
                found = False
                for i,answer in enumerate(self.answers):
                    try:
                        self.answers[i][1].remove(msg.author.id)
                        found = True
                    except:
                        pass
                if found:
                    await msg.add_reaction(msg,"✅")
                else:
                    await msg.add_reaction(msg,"❌")
                return

            if key.isdigit():
                key = int(key)
                ans = self.get_answer_by_id(key)
                if ans:
                    if self.vote_possible(msg,poll.answers[key-1]):
                        ans[1].remove(msg.author.id)
                    else:
                        await msg.channel.send("You didn't even vote.")
                        return
            else:
                for i,answer in enumerate(self.answers):
                    if key in answer[0]:
                        if self.vote_possible(msg,poll.answers[i]):
                            self.answers[i][1].remove(msg.author.id)
                        else:
                            await msg.channel.send("You didn't even vote.")
                            return
        except Exception as e:
            await msg.channel.send(str(e))
        await msg.add_reaction(msg,"✅")


# class VoteKick:
#     votekicks = []
    
#     @classmethod
#     def remove(cls,kick):
#         try:
#             cls.votekicks.remove(kick)
#         except:
#             pass
        

#     @classmethod
#     def createAllEmbed(cls):
#         embed = discord.Embed()
#         embed.set_author(name="Lista aktywnych votekicków.")
#         for i,votekick in enumerate(cls.votekicks):
#             embed.add_field(name=f"[{len(votekick.votes)}/{votekick.threshold}] {votekick.target.display_name}",value=f"Rozpoczęty przez: {votekick.author.display_name}",inline=False)
#         return embed

#     @classmethod
#     def getVotekickByMember(cls,member):
#         for votekick in cls.votekicks:
#             if member == votekick.target:
#                 return votekick
#         return False

#     @classmethod
#     def getVotekickByAuthor(cls,author):
#         for votekick in cls.votekicks:
#             if author == votekick.author:
#                 return votekick
#         return False

#     @classmethod
#     def getVotekickByPosition(cls,position):
#         try:
#             return cls.votekicks[position]
#         except:
#             raise Exception("Not Found.")

#     def __init__(self,bot,message,target,reason):
#         self.bot = bot
#         self.message = message
#         self.author=message.author
#         self.target=target
#         self.votes=[]
#         self.init_time = datetime.now()
#         self.threshold = 6
#         if len(VoteKick.votekicks):
#             self.id = VoteKick.votekicks[-1].id+1
#         else:
#             self.id = 0
#         self.completed = False
#         self.reason=reason
#         self.panelaction = {u"\U000023f0":self.askTimer,u"\U0001f4ac":self.askReason,u"\U00002b06":self.askThreshold,u"\U0001f5d1":self.endVote}
#         self.timer = None
#         self.end_time = None

#     async def setTimer(self,message,t):
#         if len(t.split(" ")) == 1:
#             t+=f" {datetime.now().day}.{datetime.now().month}.{datetime.now().year}"
#         try:
#             self.end_time = datetime.strptime(t, "%H:%M %d.%m.%Y")
#         except:
#             raise Exception("Niepoprawny format.")

#         td =  self.end_time - self.init_time
#         if td.total_seconds()/3600 > 12 or td.total_seconds() < 60:
#             self.end_time+=timedelta(days=1)
#             td =  self.end_time - self.init_time
#             if td.total_seconds()/3600 > 12 or td.total_seconds() < 60:
#                 raise Exception("Nie można ustawić takiego progu.") 


#         self.timer = td.seconds
#         await message.add_reaction("✅")
#         await asyncio.sleep(self.timer)
#         await self.endVote(message)

#     async def askTimer(self,message):
#         if self.timer:
#             await message.channel.send(f"{self.author.mention} Timer już ustawiony.")
#         await message.channel.send(f"{self.author.mention} Kiedy votekick wygasa [hh:mm]: ")

#         def check(msg):
#             if msg.author.id==self.author.id and msg.channel==message.channel:
#                 return True

#         try:
#             msg = await self.bot.wait_for('message',timeout=30,check=check)
#         except:
#             return

#         try:
#             await self.setTimer(msg,msg.content)
#         except Exception as e:
#             await message.channel.send(str(e))
#             return
#     def setReason(self,reason):
#         self.reason=reason

#     def setThreshold(self,t):
#         if not t.isdigit():
#             raise Exception("Niepoprawna wartość.")
#         t = int(t)
#         if (t < 9 and self.author.id != 139839031402823680) or t > len(self.message.guild.members):
#             raise Exception("Nie można ustawić takiego progu.") 
#         self.threshold = int(t)
        
#     async def askThreshold(self,message):
#         await message.channel.send(f"{self.author.mention} Edycja progu votekicka: ")

#         def check(msg):
#             if msg.author.id==self.author.id and msg.channel==message.channel:
#                 return True

#         try:
#             msg = await self.bot.wait_for('message',timeout=30,check=check)
#         except:
#             return

#         try:
#             self.setThreshold(msg.content)
#             await msg.add_reaction("✅")
#         except Exception as e:
#             await message.channel.send(str(e))

#     async def askReason(self,message):
#         await message.channel.send(f"{self.author.mention} Edycja powodu: ")

#         def check(msg):
#             if msg.author.id == self.author.id and msg.channel==message.channel:
#                 return True

#         try:
#             msg = await self.bot.wait_for('message',timeout=30,check=check)
#         except:
#             return
#         try:
#             self.setReason(msg.content)
#         except:
#             await message.channel.send("Nie udało się edytować powodu.")
#             return
#     async def endVote(self,message=None):
#         if self.completed:
#             return
#         await self.message.guild.system_channel.send(embed=self.createembed(message,"Votekick zakończony."))
#         VoteKick.remove(self)
#         await message.add_reaction("✅")
#         self.completed = True
#     def checkViable(self):
#         if self.target.bot or self.target.id == 139839031402823680:
#             raise Exception("Nie można dodać takiego głosowania.")
#         if len(VoteKick.votekicks) == 10:
#             raise Exception("Nie można dodać więcej głosowań.")
#         for kick in  VoteKick.votekicks:
#             if kick.author == self.author:
#                 raise Exception("Rozpocząłeś już jedno głosowanie.")
#         VoteKick.votekicks.append(self)

#     def checkVoteDuplicate(self,author):
#         for voter in self.votes:
#             if voter.id == author.id:
#                 return False
#         return True

#     async def addReactions(self,message):
#         for reaction in self.panelaction.keys():
#             await message.add_reaction(reaction)

#     async def addVote(self,message,author):
#         if not self.checkVoteDuplicate(author):
#             text = f"{author.display_name}, głosowałeś już tutaj."
#             if author == self.author:
#                 text = f"{author.display_name} - Panel twórcy."
            
#             message = await message.channel.send(embed=self.createembed(message,text))
#             if author != self.author:
#                 return
#             def check(reaction,user):
#                 if user.id == self.author.id:
#                     return True
#             task = self.bot.loop.create_task(self.addReactions(message))
#             try:
#                 r,user = await self.bot.wait_for('reaction_add', timeout=20.0,check=check)
#             except:
#                 return
#             if r.me:
#                 await self.panelaction[r.emoji](message)
#             return
#         self.votes.append(author)
#         self.completed = await self.checkCondition()
#         if self.completed:
#             VoteKick.remove(self)
#             await self.message.guild.system_channel.send(embed=self.createembed(message,f"{author.display_name} zadecydował."))
#             return
#         if len(self.votes) > 1:
#             await self.message.guild.system_channel.send(embed=self.createembed(message,f"{author.display_name} oddał głos."))
#         else:
#             await self.message.guild.system_channel.send(embed=self.createembed(message,f"{author.display_name} utworzył nowego votekicka."))

#     async def checkCondition(self):
#         if len(self.votes) == self.threshold:
#             await self.target.guild.kick(self.target)
#             return True
#         return False

#     def createembed(self,message,addon=None):
#         embed = discord.Embed(description=f"Powód: {self.reason}")
#         text = f'[{len(self.votes)}/{self.threshold}]'
#         if self.completed:
#             text = f'[KICKED!]'
#         timer = ''
#         if self.timer:
#             timer = f"\nWygasa {':'.join(str(self.end_time.time()).split(':')[:2])}"
#         embed.set_author(name=f"Votekick na {self.target.display_name} {text} {timer}")
#         embed.set_thumbnail(url=self.target.avatar_url)
#         if addon:
#             embed.set_footer(text=addon,icon_url=message.author.avatar_url)
#         return embed

class General(commands.Cog):

    @commands.Cog.listener()
    async def on_reaction_add(self,reaction,user):
        for MemberBook in self.bookList.books():
            await MemberBook.handleReaction(reaction,user)
    @commands.Cog.listener()
    async def on_reaction_remove(self,reaction,user):
        for MemberBook in self.bookList.books():
            await MemberBook.handleReaction(reaction,user)


    @commands.command(name='members')
    async def bk(self,ctx,goto=None):
        mb = MemberBook(self.bookList,ctx.message.author,'Membersi',ctx.message.guild.members,10)
        if goto:
            mb.goto(str(goto))
        mb.message = await ctx.send(embed=mb.pageEmbed())
        
        await mb.message.add_reaction(u"\U000025c0")
        await mb.message.add_reaction(u"\U000023f9")
        await mb.message.add_reaction(u"\U000025b6")
    
    async def gather_dave_msgs(self):
        
        tatax = self.bot.get_guild(237638376138866688)
        print(f"GATHERING MSGS FROM {tatax.name}")
        bef = datetime(2017, 12, 1, 12, 0, 0)
        me = tatax.get_member(139839031402823680)
        for channel in tatax.text_channels:
            print(f"[{channel.name}]")
            async for message in channel.history(limit=None,before=bef):
                if message.author.id == 178078849408434177 and len(message.content.split(" ")) > 2:
                    embed = discord.Embed(title=str(message.created_at),description=message.content,url=message.jump_url,color=discord.Colour.from_rgb(random.randint(1,255),random.randint(1,255),random.randint(1,255)))
                    embed.set_author(name='fckudave',icon_url=message.author.avatar_url)
                    await me.send(embed=embed)
                    
                    
                    
    def __init__(self, bot):
        self.bot = bot
        self.feeding = False
        self.number = 0
        self.last_tts = ''
        self.nc={}
        self.ping = 0
        self.pings = [0,0,0,0]
        self.bookList = BookList()
        self.hourList = {'4:20':{'emoji':'<:PogChamp:442716951169466400>','sent':False},
                        '6:19': {'emoji':'<:PogChamp:442716951169466400>','sent':False},
                        '14:20':{'emoji':'<:PogChamp:442716951169466400>','sent':False},
                        '14:21':{'emoji':'<:PogChamp:442716951169466400>','sent':False},
                        '14:22':{'emoji':'<:PepeHands:533286916523556894>','sent':False}}
        self.channel_hooks = {}

    @commands.command(name='ping')
    async def pin(self,ctx):
        # t = "???"
        # s = time.time()* 100
        # m = await ctx.send(f"Zajebisty pomiar.")
        # await m.delete()
        # e = time.time()* 100
        # t = int(e-s)
        # self.ping = t
        # m = await ctx.send(f"Ostatni zmierzony ping: **{self.ping}ms**\nPing discordowy: **{t}ms**\nPing internetowy: **{t}ms**")
        # s2 = time.time()* 100
        # urllib.request.urlopen("https://www.onet.pl")
        # e2 = time.time()* 100
        # t2 = int(e2-s2)

        # await m.edit(content=f"Ostatni zmierzony ping: **{self.ping}ms**\nPing discordowy: **{t}ms**\nPing internetowy: **{t2}ms**")
        p = ping('151.101.113.7',count=5)
        self.ping = p.rtt_avg
        await ctx.send(f"```go\n{p}```")

    async def checkTime(self):
        prev = None
        while True:

            
                
        
            print("FOR GUILD")
            for guild in self.bot.guilds:
                timeString = f"{datetime.now().hour}:{datetime.now().minute}"
                if timeString in self.hourList.keys():
                    prev = timeString
                    if self.hourList[timeString]['sent'] == False:
                        try:
                            await guild.get_channel(551503910767165460).send(f"@here {timeString} {self.hourList[timeString]['emoji']}")
                        except:
                            pass
                        #await guild.system_channel.send(f"@here {timeString} {self.hourList[timeString]['emoji']}")
                        
                        self.hourList[timeString]['sent'] = True
                else:
                    
                    if prev:
                        print(f'{prev} RESET')
                        self.hourList[prev]['sent'] = False
                        prev = None
                    break
                    
            await asyncio.sleep(1)
    @commands.Cog.listener()        
    async def on_ready(self):
        #await self.gather_dave_msgs()
        #self.bot.loop.create_task(self.checkTime())
        self.command_names = [c.name for c in self.bot.commands]
        self.bot.loop.create_task(self.loop())
        for guild in self.bot.guilds:
            await self.check_webhooks(guild)
    @commands.command(name='eid')
    async def eid(self,ctx,emoji:discord.Emoji):
        await ctx.send(str(emoji.id))
    
    async def check_ping(self):
        self.ping = int(ping('151.101.113.7',count=3).rtt_avg*1000)
        return self.ping

    def avg_ping(self):
        suma = 0
        for p in self.pings:
            suma += p
        self.ping = int(suma/len(self.pings))
    def add_ping(self,p):
        self.pings = [p] + self.pings
        self.pings.pop(-1)
        print(self.pings)
        self.avg_ping()
        print(f"Avg {self.ping}")
    # async def measure_ping(self):
    #     spm = self.bot.get_channel(535206002010882084)
    #     start = time.time()*100
    #     m = await spm.send('Measuring ping...')
    #     await m.delete() 
    #     self.ping = int(time.time()*100 - start)




    async def loop(self):
        while True:
            await self.check_ping()
            await asyncio.sleep(90)

    def swap(self,stri):
        s = stri
        e = False
        if stri.endswith('ą'):
            e = True
        whites = ('.',',',';',':','"',"'",'`','-','_','+','=','[',']')
        text = []
        for word in stri.split(" "):
            ws = []
            for w in whites:
                while word.endswith(w):
                    word = word[:-1]
                    ws.append(w)
            if word.endswith("ą"):
                word = word[:-1] + '.-15-.'
            text.append(word + "".join(list(reversed(ws))))
        stri = " ".join(text)
        swap0 = (('łu','u'),('rz','ż'),('ch','h'),('cz','dż'),('sz','ż'),('ie','je'),('ia','ja'),('iu','ju'),('io','jo'),('c','dz'),('ć','dź'),('p','b'),('ł','u'),('k','g'),('ą','on'),('.-15-.','om'),('ął','oł'),('f','w'),('t','d'),('s','z'),('ś','ź'))
        #stri = re.compile(stri, re.IGNORECASE)
        for i in swap0:
            stri = re.sub(i[0], i[1], stri, flags=re.IGNORECASE)
        if stri == s:
            return (stri,False)
        return (stri,True)

    def unswap(self,stri):
        s = stri
        swap0 = (('łu','u'),('rz','ż'),('ch','h'),('cz','dż'),('sz','ż'),('ie','je'),('ia','ja'),('iu','ju'),('io','jo'),('c','dz'),('ć','dź'),('p','b'),('ł','u'),('k','g'),('ął','oł'),('ą','on'),('f','w'),('t','d'),('s','z'),('ś','ź'))
        #stri = re.compile(stri, re.IGNORECASE)
        for i in list(reversed(swap0)):
            stri = re.sub(i[1], i[0], stri, flags=re.IGNORECASE)
        if stri == s:
            return (stri,False)
        return (stri,True)


    @commands.command(name='invite')
    async def invite(self,ctx):
        """Invite me to your server"""
        url = discord.utils.oauth_url("342463161770704897")
        await ctx.send(url)
    @commands.command(name='leave')
    async def lv(self,ctx,name=None):
        if ctx.message.author.id == 139839031402823680:
        
            
            if name == None:
                try:
                    await ctx.message.guild.system_channel.send('@everyone wypierdalam, elo!')
                except:
                    pass
                await ctx.message.guild.leave()
            else:
                for guild in self.bot.guilds:
                    if name.lower() in guild.name.lower():
                        try:
                            await guild.system_channel.send('Wypierdalam, elo.')
                        except:
                            pass
                        await guild.leave()
                        print(f"Wykurwiłem z {guild.name}")
                        return
            print("Nie znalazłem takiego serwera.")

    async def change_region(self,guild,region=None,ctx=None):

        regions = {'amsterdam':discord.VoiceRegion.amsterdam,'eu_central':discord.VoiceRegion.eu_central,'eu_west':discord.VoiceRegion.eu_west,'frankfurt':discord.VoiceRegion.frankfurt,'london':discord.VoiceRegion.london,'russia':discord.VoiceRegion.russia}

        if ctx:
            if region is None:
                await ctx.send(f'Regiony: {", ".join(list(regions.keys()))}')
                return

            if region is None:
                region = random.choice(list(regions.values()))
            else:
                try:
                    region = regions[region]
                except:
                    await ctx.send('Zły region')
                    return
            
            if guild is None:
                guild = ctx.message.guild

        else:
            region = random.choice(list(regions.values()))

    
        await guild.edit(region=region)



    @commands.command(name='region')
    async def region(self,ctx,region=None):
        if ctx.message.author.id not in [139839031402823680,197039120604725249,247110014303469578]:
            return

        await self.change_region(ctx.message.guild,ctx=ctx,region=region)        

    @commands.command(name='xd')
    async def ret(self,ctx,*,stri):
        await ctx.send(self.swap(stri)[0])

    def create_message_embed(self,author,content,message=None):
        hour = str(message.created_at + timedelta(hours=2)).split(' ')[1].split(":")[0]
        minute = str(message.created_at.time()).split(":")[1]
        time = hour + ':' + minute
        tt = f"⦁ {time}"
        embed = discord.Embed(description=content,color=discord.Colour.from_rgb(random.randint(1,255),random.randint(1,255),random.randint(1,255)))
        embed.set_author(name=f"{author.display_name} {tt}",icon_url=author.avatar_url)
        
        #if message:
            #embed.set_footer(text=)
        return embed

    def is_command(self,message):
        if message.content.startswith('!'):
            if message.content.split(" ")[0][1:] in self.command_names:
                return True

        return False

    def is_emoji_only(self,message):
        stri = message.content
        for emoji in message.guild.emojis:
            stri = stri.replace(str(emoji),'')
        stri = stri.replace(' ','')
        if len(stri):
            return False
        else:
            return True


    async def check_webhooks(self,guild):

        for channel in guild.text_channels:

            channel_hooks = await channel.webhooks()
            hook = None
            for hk in channel_hooks:
                if hk.name == 'hook':

                    hook = hk
                    break
            if hook == None:

                hook = await channel.create_webhook(name='hook')
            self.channel_hooks[channel.id] = hook

    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author.bot:
            return
        start = time.time()*100
        try:
            message.guild.me
        except:
            return
        if message.author.id != message.guild.me.id and not self.is_command(message) and random.randint(1,50) == 1:
    
            r = self.swap(message.content)
            if not self.is_emoji_only(message) and not message.content.startswith("!"):
                    
                if r[1] and not len(message.attachments) and self.ping < 80 and 'http' not in message.content:
                    try:
                        hook = self.channel_hooks[message.channel.id]
                    except:
                        await self.check_webhooks(message.guild)
                        return
                    await message.delete()
                    
                    #await message.channel.send(f"**{message.author.display_name}**: {r[0]}")
                    content = r[0]
                    author = message.author
                    c = ""
                    # for mention in list(set(message.mentions)):
                    #     c += " " + mention.mention
                        #content = content.replace(mention.mention,f"**@{mention.display_name}**")
                        

                    await foo(content,message.author.display_name,message.author.avatar_url,hook)
                    #await message.channel.send(embed=self.create_message_embed(author,content,message),content=c)
                    self.add_ping(int(time.time()*100 - start))
        #await self.bot.process_commands(message)

    @commands.command(name='polls')
    async def polls(self,ctx):
        if len(Poll.polls.keys())==0:
            await ctx.send("No polls active in this server.")
        else:
            t = "```css\n[Channel] Poll title\n"
            for key in Poll.polls.keys():
                t += "\n[{}] {}".format(ctx.message.guild.get_channel(key).name,Poll.polls[key].title)
                if Poll.polls[key].on_timer:
                    t += " | " + Poll.polls[key].timer_time_left_text("m","s") + ".."
            t += "```"
            await ctx.send(t)

    @commands.group(name='poll')
    async def poll(self,ctx):
        if ctx.invoked_subcommand is None:
            if ctx.message.channel.id in Poll.polls.keys():
                await ctx.send(Poll.create_poll_text(Poll.polls[ctx.message.channel.id]))
            else:
                await ctx.send("No poll active in this channel.")

    @poll.command(name='start')
    async def start(self,ctx,*,args):
        args = args.split(";")
        if len(args) == 0:
            await ctx.send("start title;answer1;answer2;answer3...")
            return
        if ctx.message.channel.id in Poll.polls:
            if Poll.polls[ctx.message.channel.id].on_timer:
                await ctx.send("A poll already exist in this channel.")
                return
        title = args[0].upper()
        args = args[0:]
        argsold = list(args)
        args = []
        for arg in argsold:
            if arg not in args:
                args.append(arg)
        if len(args) < 3:
            await ctx.send("Need more answers.")
            return


        if len(title) == 0:
            await ctx.send("No title.")
            return

        answers = args[1:]

        _poll = Poll(ctx.message,title,answers)
        await ctx.send("Poll created.")
        await ctx.message.delete()
        await ctx.send(Poll.create_poll_text(Poll.polls[ctx.message.channel.id]))
    @poll.command(name='kill')
    async def kill(self,ctx,*args):
        if len(args) == 0:
            text = "Poll ended manually."
        else:
            text = " ".join(args)
            text = text.capitalize()
        await Poll.end(Poll.polls[ctx.message.channel.id],ctx.message,text)
    @poll.command(name='vote')
    async def vote(self,ctx,*,args):
        if ctx.message.channel.id not in Poll.polls.keys():
            await ctx.send("Brak aktywnego polla na tym kanale. (!polls)")
            return
        if not len(args):
            await ctx.send("vote [key/number/clear]")
            return
        if args[0].lower() == "clear":
            await Poll.vote_clear(Poll.polls[ctx.message.channel.id],ctx.message," ".join(args))
            return
        c = 0
        t = 0
        if ";" in args:
            if len(args.split(";"))>1:
                for v in args.split(";"):
                    if len(v) > 0:
                        t+=1
                        x = await Poll.vote(Poll.polls[ctx.message.channel.id],ctx.message,v)
                        if x:
                            c+=1
                await ctx.send("{}/{} votes saved.".format(c,t))
                return
        x = await Poll.vote(Poll.polls[ctx.message.channel.id],ctx.message,args)
        if x:
            await ctx.message.add_reaction("✅")
        else:
            await ctx.message.add_reaction("❌")
            
    @poll.command(name='add_answer')
    async def add_answer(self,ctx,*,args):
        for arg in args.split(";"):
            Poll.add_answer(Poll.polls[ctx.message.channel.id],ctx.message.channel,arg)

    @poll.command(name='del_answer')
    async def del_answer(self,ctx,*,args):
        for arg in args.split(";"):
            Poll.remove_answer(Poll.polls[ctx.message.channel.id],ctx.message.channel," ".join(args))

    @poll.command(name='timer')
    async def timer(self,ctx,t):
        poll = Poll.polls[ctx.message.channel.id]
        if t == "stop":
            poll.on_timer = False
            return
        if poll.on_timer:
            await ctx.send("Poll already on timer, {} minutes left.")
            return
        await Poll.set_timer(poll,ctx.message,int(t))


    #--------------------------------------------------------- 
    @commands.command(name='send')
    async def tsdfsdfsdr(self,ctx,id,*,string):

        await self.bot.get_user(int(id)).send(string)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        
        #if after.id == 330100510730354689 and before.display_name != after.display_name:
        # if before.display_name != after.display_name:
        #     p = 'C:\\Arkowiec-rewrite\\slowa2.txt'
        #     with open(p,'r',encoding="utf-8") as f:
	    #         content = f.read()

        #     if after.id not in self.nc.keys():
        #         self.nc[after.id] = False

        #     if self.nc[after.id]:
        #         self.nc[after.id] = False
        #     else:
        #         self.nc[after.id] = True
        #         await after.edit(nick=random.choice(content.split("\n")).capitalize())
        #     content = None
            
        
        tts = None

        if after.display_name != before.display_name:
            tts = f"{before.display_name} zmienił nick na {after.display_name}."
            await self.play(after.guild,tts)
            return
        if after.status != before.status:
            tts = f"{before.display_name} jest {after.status}."
            await self.play(after.guild,tts)
            return
        
        if after.activity and not before.activity or (after.activity and before.activity):
            if not before.activity:
                tts = f"{before.display_name} gra w {after.activity.name}."
            elif after.activity.name != before.activity.name:
                tts = f"{before.display_name} gra w {after.activity.name}."
        if not after.activity and before.activity:
            tts = f"{before.display_name} zakończył grę w {before.activity.name}."
        if tts:
            await self.play(after.guild,tts)


    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before, after):
        if after.channel:
            if 'HECki Zjeb' in after.channel.name:
                await after.channel.edit(name=after.channel.name.replace('HECki Zjeb','HECki Mocarz'))
        if before.channel:
            if before.channel.name == '😘 HECki Mocarz' and not len(before.channel.members):
                await before.channel.edit(name='😘 HECki Zjeb')
        if member.id in [139839031402823680,197039120604725249,247110014303469578]:
            if after:
                if not before.self_deaf and after.self_deaf:
                    await self.change_region(member.guild)
        if member.bot or not self.feeding:
            return
        tts = ''
        if after.channel and not before.channel:
            tts = f"{member.display_name} dołączył na kanał {after.channel.name.split(' ')[1:]}"
        elif not after.channel and before.channel:
            tts = f"{member.display_name} opuścił kanał {before.channel.name.split(' ')[1:]}"
        elif after.channel and before.channel:
            if after.channel != before.channel:
                tts = f"{member.display_name} przeniusł się z kanału {before.channel.name.split(' ')[1:]} na {after.channel.name.split(' ')[1:]}"
        
        if tts:
            await self.play(member.guild,tts)
            return

    
    
    async def play(self,guild,say):
        if say == self.last_tts:
            return
        else:
            self.last_tts = say
        number = self.number
        tts = gTTS(say, 'pl')
        vc = guild.voice_client
        waiting = 0
        
        if vc:
            tts.save(f'\data\audio\{number}.wav')
            #self.number+=1
            while vc.is_playing():
                await asyncio.sleep(0.05)
                waiting += 0.05
                if waiting > 5:
                    return
            
            vc.play(discord.FFmpegPCMAudio(f'{number}.wav'))

            while not os.path.exists(f'{number}.wav') or vc.is_playing():
                await asyncio.sleep(0.1)
            os.remove(f'{number}.wav')
    
    @commands.command(name='savembrs')
    async def savembrs(self,ctx):
        self.mbrs = []
        for member in ctx.message.guild.members:
            self.mbrs.append(member)
    
    @commands.command(name='cmpmbrs')
    async def cmpmbrs(self,ctx):
        cmbrs = ctx.message.guild.members
        t = ''
        for member in self.mbrs:
            if member not in cmbrs:
                t += f'{member.mention}\n'
        await ctx.send(t)

    @commands.command(name='say')
    async def say(self,ctx,*,text):
        vc = ctx.message.guild.voice_client
        if vc is None:
            return
        tts = gTTS(text, 'pl')
        tts.save(f'text.wav')
        waiting = 0
        while vc.is_playing():
            await asyncio.sleep(0.05)
            waiting += 0.05
            if waiting > 5:
                return
        vc.play(discord.FFmpegPCMAudio(f'text.wav'))
    @commands.command(name='feedme')
    async def feed(self,ctx):
        member = ctx.message.author
        if member.voice is None:
            return
        self.feeding = True
        vc = member.guild.voice_client
        if vc is None:
            await member.voice.channel.connect()
        else:
            await vc.move_to(member.voice.channel)

    
    @commands.command(name='avatar')
    async def avatar(self,ctx,member:discord.Member):
        await ctx.send(member.avatar_url_as(format='png'))

    @commands.command(name='setnames')
    async def setnames(self,ctx,*,name):
        for member in ctx.message.guild.members:
            try:
                if member.nick != name:
                    await member.edit(nick=str(name))
            except:
                pass
    
    @commands.command(name='resetnames')
    async def resetnames(self,ctx):
        for member in ctx.message.guild.members:
            try:
                await member.edit(nick=str(member.name))
            except Exception as e:
                print(str(e))

    @commands.command(name='pm')
    async def pm(self,ctx,arg,*,text):
        member = None
        if arg.isdigit():
            memberid = int(arg)
            member = self.bot.get_user(memberid)
        else:
            member = arg
        try:
            await member.send(text)
        except:
            await ctx.send(f'{member.name} zablokował mnie.')
    @commands.command(name='wh')
    async def gds(self,ctx):
        m = random.choice(ctx.message.guild.members)
        await foo(m.display_name,m.avatar_url)

    @commands.command(name='serverinfo')
    async def os(self,ctx):
        await ctx.send(ctx.message.guild.created_at.strftime("%d %b %Y %H:%M"))
    
    @commands.command(name='scrn')
    async def scrn(self,ctx):
        im = PIL.ImageGrab.grab()
        im.save('C:\\Users\\HECki\\Desktop\\s.png')
        await ctx.send(file=discord.File('C:\\Users\\HECki\\Desktop\\s.png'))

def setup(bot):
    bot.add_cog(General(bot))