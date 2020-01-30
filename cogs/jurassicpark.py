from discord.ext import commands
import discord
import asyncio
import logging
from sqlalchemy.ext.declarative import declarative_base

from .jurassic_modules.dino import Dino
from .jurassic_modules.discovery import Discovery
from .jurassic_modules.jurassicprofile import JurassicProfile as JP
from .jurassic_modules.dino_info import StaticDino, DinoStatEmojis as DSE
from .jurassic_modules.part_info import StaticPart,ProfilePart

import random
from .utils.dbconnector import DatabaseHandler as Dbh
from .jurassic_modules.event_handler import voiceStateUpdateHandler as veh

log = logging.getLogger(name="Jurassic Cog")

class JurrasicPark(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.rating = []

    @commands.command(name='jprofile')
    async def sendMemberProfileImage(self,ctx):
        profile = JP.getProfile(ctx.message.author)
        if profile:
            e = discord.Embed(title=f"{ctx.message.author.display_name}'s PROFILE",color=discord.Color.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
            e.add_field(name="Experience",value=profile.exp)

            await ctx.send(embed=e)
        else:
            await ctx.send("Nie posiadasz profilu Jurassic.")
            return

    @commands.command(name='army')
    async def member_dinos(self,ctx):
        profile = JP.getProfile(ctx.message.author)
        if not profile:
            await ctx.send("Nie posiadasz profilu Jurassic.")
            return
        dl = list(sorted(profile.getOwnedDinos(), key = lambda x: x.tier, reverse=True))

        embed = discord.Embed(title = f"{ctx.message.author.display_name} - {len(dl)} OWNED DINOSAURS" ,color=discord.Color.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        embed.set_thumbnail(url='https://compote.slate.com/images/73f8ce3a-7952-48d5-bbf3-c4e25dc3a144.jpeg')
        lines = []


        for d in dl:
            txt = f"{DSE.emojis['blank']} {DSE.emojis['damage']}{str(d.damage)}{DSE.emojis['blank']}{DSE.emojis['defense']}{str(d.defense)}{DSE.emojis['blank']}{DSE.emojis['health']}{str(d.health)}{DSE.emojis['blank']}{DSE.emojis['speed']}{str(d.speed)}"
            embed.add_field(name=f"`🦖` **{d.name.capitalize()}**#*{d.id}*  Tier {d.tier+1}",value=txt,inline=False)

        # # for i,d in enumerate(dl):
        # #     lines.append( (f"{i+1}. T{d.tier}", f"{d.name.capitalize()}#{d.id}", str(d.damage), str(d.defense), str(d.health), str(d.speed)) )

        # for i,d in enumerate(dl):
        #     lines.append( (f"{i+1}. T{d.tier} **{d.name.capitalize()}**#*{d.id}* {str(d.damage)}, {str(d.defense)}, {str(d.health)}, {str(d.speed)}") )

        # # col_widths = [[] for _ in range(len(lines[0]))]
        # # for line in lines:
        # #     for i,col in enumerate(line):
        # #         col_widths[i].append(len(col))

        # # col_widths = [max(col) for col in col_widths]
        # # print(col_widths)
        # t = ""
        # for line in lines:
        #     #t += ''.join({elem}.ljust(col_widths[i],"-") for i,elem in enumerate(line))
        #     t += line
        #     t += '\n'
        # embed.add_field(name=f"**Army**", value = t)
 

        await ctx.send(embed=embed)


    @commands.command(name='eq')
    async def member_assembly(self,ctx):
        profile = JP.getProfile(ctx.message.author)
        if not profile:
            await ctx.send("Nie posiadasz profilu Jurassic.")
            return

        embed = discord.Embed(title = f"{ctx.message.author.display_name} - DINOSAUR LAB" ,color=discord.Color.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        embed.set_thumbnail(url='https://i.imgur.com/s1xRSYT.png')


        dinos = profile.getDinosWithParts()

        for dino in dinos:
        
            t = ''
            static_parts_req = dino.getPartsRequired()
            for sp in static_parts_req:
                t += sp.getEmoji() + f"x{sp.getCount(profile)} "
            embed.add_field(name=f"**{dino.name.capitalize()}** Tier {dino.tier+1}",value=t, inline= False)
   

        await ctx.send(embed=embed)


    @commands.command(name='info')
    async def dino_info(self,ctx, dino_name):
        dino = StaticDino.getDino(dino_name)
        await ctx.send(embed=dino.getEmbed())


    @commands.command(name='ratedinos')
    async def ratedinos(self,ctx):
        
        dl = StaticDino.getSetDinos(is_random=True)
        # if len(dl) == len(StaticDino.getAll()):
        #     await ctx.send(embed=discord.Embed(description="All dinos set"))
        #     return

        my_channel = self.bot.get_guild(247039921825513472).get_channel(595291660728926218)
        to_remove = []
        for dino in list(random.sample(dl,len(dl))):
            n_total = len(StaticDino.getAll())
            breaker = False
            embed = dino.getEmbed()
            n_set = len(StaticDino.getSetDinos())
            inf = f"{n_set}/{n_total} dinos set."
            embed.set_footer(text=f"[{inf}]\nTiery: 5,4,3,2,1 (5 - best, 1 - worst)\nŻeby wyznaczyć tiery statystyk wpisz: 1231 (cyfry oznaczaja kolejne katerogie tierów)\nOpcjonalnie można dopisać piątą wartość, która będzie odpowiadała Overall Tier, wtedy będzie on ustawiony na sztywno zamiast być liczonym ze średniej tierów.\nskip - kolejny dino\ndel - usuwa dinozaura z listy jeśli ma chujowe zdjecie, albo ogolnie jest meh\nstop - koniec przegladania")
            try:
                msg = await ctx.send(embed=embed)
            except:
                Dbh.session.delete(dino)
                continue

            def check(m):
                return m.channel == ctx.message.channel and m.author.id == ctx.message.author.id

            resp = await self.bot.wait_for('message', check=check, timeout=120.0)
            resp = resp.content
            if resp == 'skip':
                continue
            if resp == 'stop':
                Dbh.session.commit()
                break
            
            if resp == 'del':
                await my_channel.send(f"{ctx.message.author.name} usunal {dino.name}: {dino.getValidUrl()}")
                StaticDino.removeFromFile([dino,])
                e = discord.Embed(description=f"{dino.name.capitalize()} został usunięty.")
                e.colour = discord.Colour.from_rgb(255,0,0)
                await msg.edit(embed=e)
                Dbh.session.commit()
                continue
            
            if len(resp) > 5 or len(resp) < 4:
                await ctx.send(f"Niepoprawna liczba argumentów ({len(resp)}/4)")
                continue
            
            tiers = []
            for char in resp:
          
                try:
                    t = int(char)
                except:
                    await ctx.send(f"Niepoprawny format argumentu (t)")
                    breaker = True
                    break
                if t < 1 or t > 5:
                    await ctx.send(f"Niepoprawna wartość argumentu (t)")
                    breaker = True
                    break

                tiers.append(t-1)

            if breaker:
                break

            dino.setTiers(tiers)
            Dbh.session.commit()
            e = dino.getEmbed()
            e.color = discord.Colour.from_rgb(0,255,0)
            e.set_footer(text="Edycja Pomyślna")
            await msg.edit(embed=e)
            await my_channel.send(f"{ctx.message.author.name} edytował {dino.name} -> {tiers}")
            
        Dbh.session.commit()
        

    async def loop(self):
        g = self.bot.get_guild(551005738877583381)
        for vc in g.voice_channels:
            await vc.edit(name=StaticDino.getRandom().name)
        await asyncio.sleep(60)

    def setupDB(self):
        Dbh.init()
        Dbh.createTables()

        # dl = StaticDino.getSetDinos(is_random=False)
        # for d in dl:
        #     d.fixOverall()

        
        StaticDino.updateDinos()
        StaticPart.updateParts(StaticDino.getAll())
        Dbh.session.commit()

    @commands.Cog.listener()
    async def on_ready(self):   
        self.bot.loop.create_task(self.loop())
    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        veh(member,before,after,self.bot)
    

def setup(bot):
    cog = JurrasicPark(bot)
    cog.setupDB()
    bot.add_cog(cog)
    
