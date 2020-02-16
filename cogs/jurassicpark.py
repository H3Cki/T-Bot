from discord.ext import commands
import discord
import asyncio
import logging
import random
from datetime import datetime, timedelta

from sqlalchemy.ext.declarative import declarative_base
from .utils.dbconnector import DatabaseHandler as Dbh

# from .jurassic_modules.dino import Dino



# from .jurassic_modules.jmap import JMap
# from .jurassic_modules.resources import *
# from .jurassic_modules.embeds import *
# from .jurassic_modules.event_handler import voiceStateUpdateHandler as veh

from .jurassic_modules.guild_settings import JGuildSettings
from .jurassic_modules.discovery import Discovery
from .jurassic_modules.jurassicprofile import JurassicProfile as JP
from .jurassic_modules.dino_info import StaticDino, DinoStatEmojis as DSE



class JurrasicPark(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.rating = []
        self.visitors = {}
        self.last_shuffle = 0
        self.shuffle_interval = 1200
    #
    #
    # COMBAT HERE ---------------------------
    #
    #      
    
    
     
    @commands.command(name='map')
    async def map(self,ctx):
        m = JMap(ctx,self.bot)
        await m.display()
        
 
    #
    #
    # GUILD SETTINGS HERE ---------------------------
    #
    #
    
    @commands.command(name='gs',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def gs(self,ctx):
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


    @commands.command(name='enablenotif',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def enablenotif(self,ctx):
        gs = JGuildSettings.get(ctx.message.guild.id)
        if not gs:
            await ctx.send("No setting for this server")
            return
        gs.notify = True
        Dbh.session.commit()
        
    @commands.command(name='disablenotif',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def disablenotif(self,ctx):
        gs = JGuildSettings.get(ctx.message.guild.id)
        if not gs:
            await ctx.send("No setting for this server")
            return
        gs.notify = False
        Dbh.session.commit()

    @commands.command(name='setjnotif',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def setnotif(self,ctx):
        gs = JGuildSettings.get(ctx.message.guild.id)
        if not gs:
            await ctx.send("No setting for this server")
            return
        
        gs.j_notif_channel = ctx.message.channel.id
        Dbh.session.commit()


    @commands.command(name='setvoicecat',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def set_vcat(self,ctx,cat_id):
        gs = JGuildSettings.get(ctx.message.guild.id)
        if not gs:
            await ctx.send("No setting for this server")
            return
        
        gs.j_voice_cat = int(cat_id)
        Dbh.session.commit()


    @commands.command(name='givechest',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def givechest(self,ctx,target:discord.Member):
        profile = JP.getProfile(target)
        if not profile:
            await ctx.send(f"{target.display_name} doesn't seem to have a Jurassic Profile.")
            return
        chest = DinoChest(profile,StaticDino.getRandomSetDinoTierWise())
        Dbh.session.add(chest)
        await ctx.send(ctx.message.author.mention,embed=itemDropEmbed(target,chest))
        
    @commands.command(name='givekey',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def givekey(self,ctx,target:discord.Member):
        profile = JP.getProfile(target)
        if not profile:
            await ctx.send(f"{target.display_name} doesn't seem to have a Jurassic Profile.")
            return
        key = Key(profile)
        Dbh.session.add(key)
        await ctx.send(ctx.message.author.mention,embed=itemDropEmbed(target,key))


    #
    #
    # MODERATION AND TESTING ---------------------------
    #
    #
    
    @commands.command(name='swaptiers',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def swaptiers(self,ctx):
        rev = {
            0 : 4,
            1 : 3,
            2 : 2,
            3 : 1,
            4 : 0
        }
        dinos = StaticDino.getSetDinos()
        for dino in dinos:
            dmg = rev[dino.damage_tier]
            defe = rev[dino.defense_tier]
            speed = rev[dino.speed_tier]
            health = rev[dino.health_tier]
            dino.setTiers([dmg,defe,speed,health])
        Dbh.session.commit()
    

    @commands.command(name='droptable',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def droptable(self,ctx,table):
        Dbh.session.execute(f"DROP TABLE {table};")
        Dbh.session.commit()
        print("DONE")
        
    @commands.command(name='createtables',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def createtables(self,ctx):
        Dbh.createTables()
        print("READY")
    
    @commands.command(name='emojiid',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def emojiid(self,ctx,name):
        for emoji in ctx.message.guild.emojis:
            if name in emoji.name:
                print(f"{emoji.name} {emoji.id}")

    #
    #
    # MEMBER COMMANDS HERE ---------------------------
    #
    #

    @commands.command(name='dinostiers')
    async def dtr(self,ctx):
        t = "Dinos By tier:\n"
        for x in range(0,5):
            t += f"Tier {x+1}: {len(StaticDino.getSetTierDinos(x))}\n"
        await ctx.send(t)
        
        
    @commands.command(name='chests')
    async def chests(self,ctx):
        profile = JP.getProfile(ctx.message.author)
        if not profile:
            await ctx.send(f"{target.display_name} doesn't seem to have a Jurassic Profile.")
            return     
        
        keys   = sorted(Key.getAll(profile), key = lambda x: x.tier_idx)
        chests = sorted(DinoChest.getProfileChests(profile), key = lambda x: x.tier_idx)
        cv = ''
        kv = ''
        for i,chest in enumerate(chests):
            cv += f'\n`{i+1}` {chest.dropText}'
        for i,key in enumerate(keys):
            kv += f'\n`{i+1}` {key.dropText}'
        
        embed = discord.Embed(title=f"{ctx.message.author.display_name} - {len(chests)} CHESTS")
        embed.set_thumbnail(url='https://i.pinimg.com/236x/d2/ca/d6/d2cad6a7be1e22593fa8c9f61da32b22--game-props-d-models.jpg')
        embed.add_field(name="Chests",value=cv or '-')
        embed.add_field(name="Keys",value=kv or '-')
        embed.set_footer(text='!open')          
        await ctx.send(embed=embed)

    @commands.command(name='open')
    async def openchest(self,ctx,idx=None):
        pass
        
        
        
        # if not idx:
        #     await ctx.send(embed=discord.Embed(description=f"{ctx.message.author.mention} !open <chest_index>"))
        #     return
        
        # gs = JGuildSettings.get(ctx.message.author.guild.id)
        # profile = JP.getProfile(ctx.message.author)
        # if not profile:
        #     await ctx.send(f"{target.display_name} doesn't seem to have a Jurassic Profile.")
        #     return
        
        # try:
        #     idx = int(idx)
        # except:
        #     return
        
        # chests = sorted(DinoChest.getProfileChests(profile), key = lambda x: x.tier_idx)
        
        # try:
        #     chest = chests[idx-1]
        #     reward = chest.open()
        # except Exception as e:
        #     await ctx.send(embed=discord.Embed(description=str(e), colour=discord.Colour.from_rgb(255,30, 15)))
        #     return
        
        # Dbh.session.add(reward)
        # Dbh.session.commit()
        
        # if isinstance(reward,Dino):
        #     dino = reward
        #     static_dino = reward.static_dino
        #     if not static_dino.isDiscovered(self.member.guild.id):
        #         disc = Discovery(static_dino.name,profile.id,profile.guild_id)
        #         profile.addExp(5)
        #         Dbh.session.add(disc)
        #         reward = Rewards.rewards['discovery']
        #         profile.resources.addResources(reward)
        #         await gs.send(embed=discoveryEmbed(self.member,static_dino))

        #     e = dino.getEmbed()
        #     e.set_thumbnail(url=static_dino.image_url)
        #     try:
        #         await self.member.send(embed = e)
        #     except:
        #         await gs.send(self.member.mention,embed = e)
            
            
        # if isinstance(reward,ProfilePart):
        #     static_part = reward.static_part
        #     await ctx.send(embed=itemDropEmbed(ctx.message.author,static_part))
            
        
            
            
    @commands.command(name='jprofile',aliases=['jp','profile'])
    async def jprofile(self,ctx,target:discord.Member=None):
        """
        Shows member's jurassic profile
        """
        if not target:
            target = ctx.message.author
        profile = JP.getProfile(target)
        if profile:
            e = discord.Embed(title=f"{ctx.message.author.display_name}'s PROFILE",color=discord.Color.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
            e.set_thumbnail(url=target.avatar_url_as(format='png'))
            e.add_field(name="Resources (Shit, Wood, Gold)",value=profile.resources.asText(),inline=False)
            e.add_field(name="Value",value=profile.pointsAsText,inline=False)
            e.add_field(name="Dinos", value=f"{len(profile.getOwnedDinos())} owned\n{len(profile.getDiscoveries())} discovered")
            e.add_field(name="Parts", value=f"{len(profile.getAllParts())} owned")
            await ctx.send(embed=e)
        else:
            await ctx.send("Nie posiadasz profilu Jurassic.")
            return

    @commands.command(name='army')
    async def member_dinos(self,ctx,member:discord.Member=None):
        """
        Shows dinos owned by member
        """
        if not member:
            member = ctx.message.author
        profile = JP.getProfile(member)
        if not profile:
            await ctx.send(f"No jurassic profile found for {member.display_name}. Join jurassic voice channel to create profile.")
            return
        dl = list(sorted(profile.getOwnedDinos(), key = lambda x: x.power_level, reverse=True))

        embed = discord.Embed(title = f"{ctx.message.author.display_name} - {len(dl)} OWNED DINOSAURS" ,color=discord.Color.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        embed.set_thumbnail(url='https://compote.slate.com/images/73f8ce3a-7952-48d5-bbf3-c4e25dc3a144.jpeg')
        lines = []


        for i,d in enumerate(dl):
            if d.static_dino:
                info = f"[{DSE.emojis['wiki']}]({d.static_dino.getValidUrl()})[📷]({d.static_dino.image_url})"
            else:
                info = "EXTINCT"
            info = ''
            txt = f"{DSE.emojis['blank']}{DSE.emojis['damage']}{str(d.damage)}{DSE.emojis['blank']}{DSE.emojis['defense']}{str(d.defense)}{DSE.emojis['blank']}{DSE.emojis['health']}{str(d.health)}{DSE.emojis['blank']}{DSE.emojis['speed']}{str(d.speed)}{DSE.emojis['blank']}{info}"
            embed.add_field(name=f"`{i+1} 🦖` **{d.name.capitalize()}**#{d.id} - Tier {d.tier+1}",value=txt,inline=False)
        #embed.set_footer(text=f"Click wiki icon for more info about dinos.")
        await ctx.send(embed=embed)

    def isDinoLive(self,guild,member,dino_name):
        gs = JGuildSettings.get(guild.id)
        for vc in guild.voice_channels:
            if not vc.category:
                continue
            if vc.category.id != gs.j_voice_cat:
                continue
            dn = StaticDino.parseName(vc.name)
            try:
                visitors = self.visitors[guild.id][member.id]
            except:
                visitors = []
            if dn == dino_name and vc.id not in visitors:
                return True
        return False

    @commands.command(name='lab')
    async def member_assembly(self,ctx):
        """
        Shows member's dino lab
        """
        profile = JP.getProfile(ctx.message.author)
        if not profile:
            await ctx.send("Nie posiadasz profilu Jurassic.")
            return
        
        dinos = profile.getDinosWithParts()
        dinos = sorted(dinos, key = lambda x: len(x.getPartsOwned(profile)), reverse=True)
        n_slots = len(dinos)
        embed = discord.Embed(title = f"{ctx.message.author.display_name} - DINOSAUR LAB [{n_slots}/10] Slots." ,color=discord.Color.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        embed.set_thumbnail(url='https://i.imgur.com/s1xRSYT.png')
        
        if n_slots >= 10:
            embed.set_footer(text="❗ Your lab is full! Clean up some space by building currently unfinished dinos. Storing more parts than your lab can contain can lead to explosion 💥 which will destroy everything inside it.")

        

        for dino in dinos:
        
            t = ''
            static_parts_req = dino.getPartsRequired()
            for sp in static_parts_req:
                count = sp.getCount(profile)
                
                if count > 0:
                    extra = ""
                else:
                    extra = "void"
                
                if count > 1:
                    count_text = f"{count} "
                else:
                    count_text = " "
                    
                if dino.isDiscovered(ctx.message.guild.id):
                    emoji = DSE.emojis['dino1']
                    tier = f" - Tier {dino.tier+1}"
                else:
                    emoji = '❓'
                    tier = ''
                    
                islive = self.isDinoLive(ctx.message.guild,ctx.message.author,dino.name)
                if islive:
                    ilt = " ⏰ LIVE!"
                else:
                    ilt = ""
                t += sp.getEmoji(extra=extra) + count_text
            embed.add_field(name=f"{emoji} **{dino.name.capitalize()}**{tier}"+ilt,value=DSE.emojis['blank']+t, inline= False)
   

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
                t = ' DELETED'
                info = ''
            else:
                info = f"{[DSE.emojis['wiki']]}({dino.getValidUrl()})[📷]({dino.image_url})"
            embed.add_field(name=f"🦖 **{disc.dino_name.upper()}**"+t, value=f"{info} *Discovered by {member.display_name}*")
        await ctx.send(embed=embed)
        
    @commands.command(name='dinoinfo')
    async def dino_info(self,ctx, dino_name):
        """
        Shows profile of a dino by its name
        """
        dino = StaticDino.getDino(dino_name.lower())
        if not dino:
            await ctx.send(embed=discord.Embed(description=f'No information about {dino.name.capitalize()}.'))
        if dino.isDiscovered(ctx.message.guild.id):# or ctx.message.author.id == 139839031402823680:
            await ctx.send(embed=dino.getEmbed())
        else:
            await ctx.send(embed=discord.Embed(description=f'{dino.name.capitalize()} has not been discovered yet.'))
            
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
    async def ratedinos(self,ctx,review=''):
        
        if len(review):
            review = False
        else:
            review = True
        # if len(dl) == len(StaticDino.getAll()):
        #     await ctx.send(embed=discord.Embed(description="All dinos set"))
        #     return

        my_channel = self.bot.get_guild(247039921825513472).get_channel(595291660728926218)
        to_remove = []
        
        dinolist = StaticDino.getSetDinos(is_random=review)
        while len(dinolist):
            dinolist = StaticDino.getSetDinos(is_random=review)
            dino = random.choice(dinolist)
            n_total = len(StaticDino.getAll())
            breaker = False
            embed = dino.getEmbed()
            n_set = len(StaticDino.getSetDinos())
            inf = f"{n_set}/{n_total} dinos set."
            embed.set_footer(text=f"[{inf}]\n❗❗❗ Tiery: 1,2,3,4,5 (1 - best, 5 - worst)\nŻeby wyznaczyć tiery statystyk wpisz: 1231 (cyfry oznaczaja kolejne katerogie tierów)\nOpcjonalnie można dopisać piątą wartość, która będzie odpowiadała Overall Tier, wtedy będzie on ustawiony na sztywno zamiast być liczonym ze średniej tierów.\bset - zatwierdza obecne (losowe) statystyki\nskip - kolejny dino\ndel - usuwa dinozaura z listy jeśli ma chujowe zdjecie, albo ogolnie jest meh\nstop - koniec przegladania")
            try:
                msg = await ctx.send(embed=embed)
            except:
                Dbh.session.delete(dino)
                continue

            def check(m):
                return m.channel == ctx.message.channel and m.author.id == ctx.message.author.id

            try:
                resp = await self.bot.wait_for('message', check=check, timeout=160.0)
            except:
                await ctx.send(f"{ctx.message.author.name} TIMEOUT")
                return
            resp = resp.content
            if resp == 'set':
                dino.is_random = False
                continue
            if resp == 'skip':
                continue
            if resp == 'stop':
                Dbh.session.commit()
                break
            
            if resp == 'del':
                #await my_channel.send(f"{ctx.message.author.name} usunal {dino.name}: {dino.getValidUrl()}")
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
        Dbh.session.commit()
            
            
            
            
            
        
    async def shuffle_channels(self,bot,g,gs):
        #dinos = StaticDino.getSetDinos(is_random=False)
        time = str((datetime.now()+timedelta(hours=1)).time())[:5]
        category = None
        self.visitors[g.id] = {}
        for vc in g.voice_channels:
            if not vc.category:
                continue
            if vc.category.id == gs.j_voice_cat:
                dino = StaticDino.getRandomSetDinoTierWise()
                category = vc.category
                
                if dino.isDiscovered(g.id):
                    emoji = DSE.emojis['dino1']
                    tier = f" ᴛ{dino.tier+1}"
                else:
                    emoji = '❓'
                    tier = ''
                await vc.edit(name=f"{emoji} {dino.name.capitalize()}"+tier)
        await category.edit(name=f"Jurassic Park @{time}")
        
        
    @commands.command(name='shuffle')
    @commands.has_guild_permissions(manage_guild=True)
    async def shuffle_command(self,ctx):
        gs = JGuildSettings.get(ctx.message.guild.id)
        await self.shuffle_channels(self,ctx.message.guild,gs)
        
        
        
    @commands.command(name='tc')
    @commands.has_guild_permissions(manage_guild=True)
    async def tc(self,ctx):
        Rewards.getMemberReward(ctx.message.author)

    async def loop(self):
        while True:
            shuffled = False
            rewarded = False
            
            for g in self.bot.guilds:
            
                if time.time() - self.last_shuffle > self.shuffle_interval:
                    gs = JGuildSettings.get(g.id)
                    if not gs:
                        o = JGuildSettings(guild.id)
                        Dbh.session.add(o)
                        Dbh.session.commit()
                    if not gs.active or not gs.j_voice_cat:
                        continue
                    await self.shuffle_channels(self,g,gs)
                    shuffled = True

                    
                if time.time() - Resources.last_update > Resources.update_interval:
                    for profile in JP.getAll(g.id):
                        member = g.get_member(profile.member_id)
                        if not member:
                            continue
                        rewards = Rewards.getMemberReward(member)
                        profile.resources.addResources(rewards)
                    rewarded = True

            if shuffled:
                self.last_shuffle = time.time()
            if rewarded:
                Resources.last_update = time.time()
                Dbh.session.commit()
            await asyncio.sleep(60)

    def setupDB(self):
        Dbh.init()
        Dbh.Base.metadata.clear()
        #Dbh.session.execute('DROP TABLE static_part;')
        #Dbh.session.execute('DROP TABLE profile_part;')
        Dbh.createTables()
        StaticDino.updateDinos(limit=10)
        
        #StaticPart.updateParts(StaticDino.getAll())
        #Resources.updateResources(JP.getAll())
        
            
        
        
        
        #print(f"{len(JP.getAll())} Profiles IN TOTAL")
        #print(f"{len(Resources.getAll())} Resources IN TOTAL")
        print(f"{len(StaticDino.getAll())} Dinos IN TOTAL")
        #print(f"{len(StaticPart.getAll())} PARTS IN TOTAL")
       

            
        Dbh.session.commit()
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

def setup(_bot):
    global bot
    bot = _bot
    cog = JurrasicPark(_bot)
    cog.setupDB()
    bot.add_cog(cog)
    
