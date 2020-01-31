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
from .jurassic_modules.guild_settings import JGuildSettings

import random
from .utils.dbconnector import DatabaseHandler as Dbh
from .jurassic_modules.event_handler import voiceStateUpdateHandler as veh

log = logging.getLogger(name="Jurassic Cog")

class JurrasicPark(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.rating = []
        self.visitors = {}
        
    #
    #
    # GUILD SETTINGS HERE ---------------------------
    #
    #
    
    @commands.command(name='jsettings')
    @commands.has_guild_permissions(manage_guild=True)
    async def jsettings(self,ctx):
        gs = JGuildSettings.get(ctx.message.guild.id)
        if not gs:
            await ctx.send("No setting for this server")
            return
        
        t = f"""guild_id : {gs.guild_id}
        notif_channel: {gs.j_notif_channel}
        voice_cat: {gs.j_voice_cat}
        notify: {gs.notify}
        active: {gs.active}"""
        await ctx.send(t)


    @commands.command(name='enablenotif')
    @commands.has_guild_permissions(manage_guild=True)
    async def enablenotif(self,ctx):
        gs = JGuildSettings.get(ctx.message.guild.id)
        if not gs:
            await ctx.send("No setting for this server")
            return
        gs.notify = True
        Dbh.session.commit()
        
    @commands.command(name='disablenotif')
    @commands.has_guild_permissions(manage_guild=True)
    async def disablenotif(self,ctx):
        gs = JGuildSettings.get(ctx.message.guild.id)
        if not gs:
            await ctx.send("No setting for this server")
            return
        gs.notify = False
        Dbh.session.commit()

    @commands.command(name='setjnotif')
    @commands.has_guild_permissions(manage_guild=True)
    async def setnotif(self,ctx):
        gs = JGuildSettings.get(ctx.message.guild.id)
        if not gs:
            await ctx.send("No setting for this server")
            return
        
        gs.j_notif_channel = ctx.message.channel.id
        Dbh.session.commit()


    @commands.command(name='setvoicecat')
    @commands.has_guild_permissions(manage_guild=True)
    async def set_vcat(self,ctx,cat_id):
        gs = JGuildSettings.get(ctx.message.guild.id)
        if not gs:
            await ctx.send("No setting for this server")
            return
        
        gs.j_voice_cat = int(cat_id)
        Dbh.session.commit()


    #
    #
    # MODERATION AND TESTING ---------------------------
    #
    #

    @commands.command(name='droptable')
    @commands.has_guild_permissions(manage_guild=True)
    async def drop(self,ctx,table):
        Dbh.session.execute(f"DROP TABLE {table};")
        Dbh.session.commit()
        print("DONE")
        
    @commands.command(name='createtables')
    @commands.has_guild_permissions(manage_guild=True)
    async def drop(self,ctx,table):
        Dbh.createTables()
        print("READY")
    
    
    @commands.command(name='allparts')
    @commands.has_guild_permissions(manage_guild=True)
    async def allparts(self,ctx):
        for part in StaticPart.getAll():
            print(part.name)
    
    @commands.command(name='allpparts')
    @commands.has_guild_permissions(manage_guild=True)
    async def allpparts(self,ctx):
        for part in ProfilePart.getAll():
            sp = part.static_part
            print(sp.name)
    

    #
    #
    # MEMBER COMMANDS HERE ---------------------------
    #
    #


    @commands.command(name='jprofile')
    async def sendMemberProfileImage(self,ctx):
        """
        Shows member's jurassic profile
        """
        profile = JP.getProfile(ctx.message.author)
        if profile:
            e = discord.Embed(title=f"{ctx.message.author.display_name}'s PROFILE",color=discord.Color.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
            e.add_field(name="Experience",value=profile.exp)
            e.add_field(name="Dinos", value=f"{len(profile.getOwnedDinos())} owned\n{len(profile.getDiscoveries())} discovered")
            e.add_field(name="Parts", value=f"{len(profile.getAllParts())} owned")
            await ctx.send(embed=e)
        else:
            await ctx.send("Nie posiadasz profilu Jurassic.")
            return

    @commands.command(name='army')
    async def member_dinos(self,ctx):
        """
        Shows dinos owned by member
        """
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

        await ctx.send(embed=embed)


    @commands.command(name='lab')
    async def member_assembly(self,ctx):
        """
        Shows member's dino lab
        """
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
            print(t)
            embed.add_field(name=f"**{dino.name.capitalize()}**",value=t, inline= False)
   

        await ctx.send(embed=embed)


    @commands.command(name='dinos')
    async def all_dinos(self,ctx):
        """
        Shows list of dinos discovered in given server
        """
        a = Discovery._getAllInGuild(ctx.message.guild.id).all()
        embed = discord.Embed(title=f"{ctx.message.guild.name} - {len(a)} DISCOVERIES")
        for disc in a:
            dino = StaticDino.getDino(disc.dino_name)
            profile = JP.getProfileById(disc.profile_id)
            member = ctx.message.guild.get_member(profile.member_id)
            t = ''
            if not dino:
                t = ' RIP'
            embed.add_field(name=f"🦖**{disc.dino_name.upper()}**"+t, value=f"{DSE.emojis['blank']} *Discovered by {member.display_name}*")
        await ctx.send(embed=embed)
        
    @commands.command(name='dinoinfo')
    async def dino_info(self,ctx, dino_name):
        """
        Shows profile of a dino by its name
        """
        dino = StaticDino.getDino(dino_name.lower())
        await ctx.send(embed=dino.getEmbed())

    @commands.command(name='deletedino')
    async def delete_info(self,ctx, dino_name):
        """
        Shows profile of a dino by its name
        """
        dino = StaticDino.getDino(dino_name.lower())
        StaticDino.removeFromFile([dino,])
        Dbh.session.commit()
        await ctx.send("deleted")

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
            
        
    async def shuffle_channels(self,g,gs):
        for vc in g.voice_channels:
            if not vc.category:
                continue
            if vc.category.id == gs.j_voice_cat:
                await vc.edit(name=f"{DSE.emojis['dino1']} {StaticDino.getRandom().name.capitalize()}")

    @commands.command(name='shuffle')
    @commands.has_guild_permissions(manage_guild=True)
    async def shuffle_command(self,ctx):
        gs = JGuildSettings.get(ctx.message.guild.id)
        await self.shuffle_channels(ctx.message.guild,gs)

    async def loop(self):
        while True:
            for g in self.bot.guilds:
                self.visitors[g.id] = {}
                gs = JGuildSettings.get(g.id)
                if not gs.active or not gs.j_voice_cat:
                    continue
                
                await self.shuffle_channels(g,gs)
                
            await asyncio.sleep(3600)

    def setupDB(self):
        Dbh.init() 
        #Dbh.session.execute('DROP TABLE static_part;')
        #Dbh.session.execute('DROP TABLE profile_part;')
        Dbh.createTables()
        
        StaticDino.updateDinos()
        StaticPart.updateParts(StaticDino.getAll())
        Dbh.session.commit()
        
        print(f"{len(StaticDino.getAll())} Dinos IN TOTAL")
        print(f"{len(StaticPart.getAll())} PARTS IN TOTAL")
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            gs = JGuildSettings.get(guild.id)
            if not gs:
                o = JGuildSettings(guild.id)
                Dbh.session.add(o)
                Dbh.session.commit()
        self.bot.loop.create_task(self.loop())
    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        v = veh(member,before,after,self)
        await v.handle()

def setup(bot):
    cog = JurrasicPark(bot)
    cog.setupDB()
    bot.add_cog(cog)
    
