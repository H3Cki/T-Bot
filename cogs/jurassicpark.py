from discord.ext import commands
import discord
import asyncio
import logging
import random
import time
from threading import Thread
from datetime import datetime, timedelta

from sqlalchemy.ext.declarative import declarative_base
from .utils.dbconnector import DatabaseHandler as Dbh
from sqlalchemy.inspection import inspect

# from .jurassic_modules.dino import Dino



# from .jurassic_modules.jmap import JMap



from .jurassic_modules.guild_settings import JGuildSettings
from .jurassic_modules.discovery import Discovery
from .jurassic_modules.jurassicprofile import JurassicProfile as JP
from .jurassic_modules.dino_info import ProfileDinoPart, DinoPart, StaticDino, ProfileDino, DinoStatEmojis as DSE
from .jurassic_modules.resources import *
from .jurassic_modules.embeds import *
from .jurassic_modules.event_handler import voiceStateUpdateHandler as veh
from .jurassic_modules.entities.entity import ProfileEntity, Entity
from .jurassic_modules.army import *
from .jurassic_modules.lab import Lab
from .jurassic_modules.entities.buildable import Buildable
from .utils.imageutils import *


class JurrasicPark(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.rating = []
        self.visitors = {}
        self.last_shuffle = 0
        self.shuffle_interval = 1200
        self.channels = {}
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
        notif_channel: {gs.notif_channel}
        voice_cat: {gs.voice_cat}
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
        
        gs.notif_channel = ctx.message.channel.id
        Dbh.session.commit()


    @commands.command(name='setvoicecat',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def set_vcat(self,ctx,cat_id):
        gs = JGuildSettings.get(ctx.message.guild.id)
        if not gs:
            await ctx.send("No setting for this server")
            return
        
        gs.voice_cat = int(cat_id)
        Dbh.session.commit()



    #
    #
    # MODERATION AND TESTING ---------------------------
    #
    #
    
    @commands.command(name='startjurassic',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def startjurassic(self,ctx,text_channel_name=None):
        guild = ctx.message.guild
        gs = JGuildSettings.get(guild.id)
        if gs.voice_cat:
            for channel in guild.channels:
                if channel.category:
                    if channel.category.id == gs.voice_cat.id:
                        await channel.delete()
        


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
                
    @commands.command(name='rmparts',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def emojiid(self,ctx):
        for part in ProfileDinoPart.get():
            if part.entity.parent.is_random:
                part.delete()
            

    #
    #
    # MEMBER COMMANDS HERE ---------------------------
    #
    #


        


            
            
    @commands.command(name='jprofile',aliases=['jp','profile'])
    async def jprofile(self,ctx,target:discord.Member=None):
        """
        Shows member's jurassic profile
        """
        if not target:
            target = ctx.message.author
        profile = JP.get(target)
        if profile:
            
            
            
            url = target.avatar_url_as(format='png')
            color = averageColor(url)
            e = discord.Embed(title=f"{target.display_name}'s PROFILE",color=discord.Colour.from_rgb(color[0],color[1],color[2]))
            e.set_thumbnail(url=url)
            e.add_field(name="Resources",value=profile.resources.asText(),inline=False)
            

            
            
            owned_dinos = ProfileDino.get(as_list=True,profile_id=profile.id)
            all_dinos = []
            for pdino in owned_dinos:
                for _ in range(pdino.count):
                    all_dinos.append(pdino.entity)
            e.add_field(name="Value",value=ProfileEntity.valueOfProfile(profile),inline=False)
            discoveries = Discovery.get(as_list=True,profile_id=profile.id)
            e.add_field(name="Dinos", value=f"{len(all_dinos)} owned\n{len(discoveries)} discovered",inline=False)
            
            
            #e.add_field(name="Parts", value=f"{len(ProfilePart.get(profile_id=profile.id))} owned")
            await ctx.send(embed=e)
        else:
            await ctx.send("Nie posiadasz profilu Jurassic.")
            return


    @commands.command()
    async def attack(self,ctx,target:discord.Member=None):    
        if target is None or target == ctx.message.author or target.bot:
            await ctx.send(f'To use this command specify who you want to attack by mentioning them. For example `!attack @{random.choice([str(member) for member in ctx.message.guild.members if not member.bot and not member == ctx.message.author])}`')
            return
        
            
        member = ctx.message.author
        atk_prof = JP.get(member)
        atk_army = ProfileDino.get(profile_id=atk_prof.id)
        if not len(atk_army):
            await ctx.send(embed=discord.Embed(description=f"Dear {member.display_name}, you can't attack without having at least one dino in your army. Check !army or !help"))
            return
        
        def_prof = JP.get(target)
        
        if def_prof.last_destroyed:
            delta = datetime.now() - def_prof.last_destroyed
            td = timedelta(minutes=45)
            if delta < td:
                next_attack = (td - delta)
                next_attack = str(next_attack).split('.')[0]
                await ctx.send(embed=redEmbed(f'{target.display_name} was rekt recently, gods of Jurassic Park are protecting his base. Their power will last {next_attack}'))
                return
        
        
        def_army = ProfileDino.get(profile_id=def_prof.id)
        
        base_army_at = Army(atk_prof,atk_army)
        base_army_df = Army(def_prof,def_army)
        army_at = Army(atk_prof,atk_army)
        army_df = Army(def_prof,def_army)
        
        battle = DinoBattle(army_at,army_df)
        
        battle.start()
        
        await ctx.send(embed=battle.getEmbed())
        
        #print(battle)

    @commands.command(name='army')
    async def member_dinos(self,ctx,member:discord.Member=None):
        """
        Shows dinos owned by member
        """
   
        member = member or ctx.message.author
        profile = JP.get(member)
        dl = list(sorted(ProfileDino.get(profile_id=profile.id), key=lambda x: x.count, reverse=True))
        embed = discord.Embed(title = f"{member.display_name} - {sum([d.count for d in dl])} OWNED DINOSAURS" ,color=discord.Color.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        embed.set_thumbnail(url='https://compote.slate.com/images/73f8ce3a-7952-48d5-bbf3-c4e25dc3a144.jpeg')
        lines = []


        for i,pd in enumerate(dl):
            d = pd.entity
            if d:
                info = f"[{DSE.emojis['wiki']}]({d.getValidUrl()})[📷]({d.image_url})"
            else:
                info = "EXTINCT"
            info = ''
            txt = f"{DSE.emojis['blank']}{DSE.emojis['damage']}{str(d.damage)}{DSE.emojis['blank']}{DSE.emojis['armor']}{str(d.armor)}{DSE.emojis['blank']}{DSE.emojis['health']}{str(d.health)}{DSE.emojis['blank']}{DSE.emojis['speed']}{str(d.speed)}{DSE.emojis['blank']}{info}"
            count_text = f"(x{pd.count})" if pd.count > 1 else ''
            embed.add_field(name=f"`{i+1} {d.emoji}` **{d.name.capitalize()}**#{d.entity_id} - Tier {d.tier} {count_text}",value=txt,inline=False)
        
        all_dinos = []
        for pdino in dl:
            for _ in range(pdino.count):
                all_dinos.append(pdino.entity)
        total_stats = StaticDino.sumStats(all_dinos,as_text=True)
        embed.description = f"`🔥` Power: {total_stats}\nAvgerage Tier: {round(sum([pd.entity.tier for pd in dl])/(len(dl) or 1))}"
        #embed.set_footer(text=f"Click wiki icon for more info about dinos.")
        await ctx.send(embed=embed)

    def isDinoLive(self,guild,member,dino_name):
        gs = JGuildSettings.get(guild.id)
        for vc in guild.voice_channels:
            if not vc.category:
                continue
            if vc.category.id != gs.voice_cat:
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
    async def member_assembly(self,ctx,extra=None,*,args=None):
        """
        Shows member's dino lab
        """
        
        profile = JP.get(ctx.message.author)
        lab = Lab(profile,cog=self)
    
        # if extra == 'build':
        #     if args == 'all':
        #         await Buildable.buildEvent(profile,lab.dinos_with_parts,lab=Lab(profile),no_warning=True)
        #     return
        
        # if extra == 'delete':
        #     for arg in args:
        #         for part in ProfileDinoPart.get(profile_id=profile.id):
        #             if part.entity.parent.is_random:
        #             part.delete()
        
        await lab.start(ctx)


    @commands.command(name='build')
    async def build_item(self,ctx,item_name=None,count=1):
        """
        Builds an item
        """
        if not item_name:
            await ctx.send(f'To use this command specify what you want to build.\nFor example `!build diplodocus`.\nBuilding non-discovered dino always costs {StaticDino.BASE_BUILD_COST} in other cases base cost is dictated by tier.\nUse command `!lab` to check what you have')
            return
        profile = JP.get(ctx.message.author)
        item_name = item_name.lower()
        lab = Lab(profile)
        
        results = []
        
        no_warning = False
        infinite = False
        if item_name == 'all':
            results = lab.dinos_with_parts
            no_warning = True
            infinite = True
        else:
            for c in Buildable.__subclasses__():
                result = c.get(as_list=True,name=item_name)
                if result:
                    result = result[0]
                    for _ in range(count):
                        results.append(result)
    
        await Buildable.buildEvent(profile,results,lab=lab,no_warning=no_warning,infinite=infinite)



    @commands.command(name='discovery')
    async def all_discoveries(self,ctx,member:discord.Member=None):
        """
        Shows list of dinos discovered in given server
        """
        if member:
            profile = JP.get(member)
            a = Discovery.get(as_list=True,guild_id=ctx.message.guild.id,profile_id=profile.id)
            embed = discord.Embed(title=f"{member.display_name} - {len(a)} DISCOVERIES in {ctx.message.guild.name}")
        else:
            a = Discovery.get(as_list=True,guild_id=ctx.message.guild.id)
            embed = discord.Embed(title=f"{ctx.message.guild.name} - {len(a)} DISCOVERIES")
        
        for disc in a:
            dino = StaticDino.get(name=disc.dino_name)
            profile = JP.get(id=disc.profile_id)
            member = ctx.message.guild.get_member(profile.member_id)
            t = ''
            
            if not dino:
                t = ' DELETED'
                info = ''
            else:
                info = f"{[DSE.emojis['wiki']]}({dino.getValidUrl()})[📷]({dino.image_url})"
            embed.add_field(name=f"🦖 **{disc.dino_name.upper()}**"+t, value=f"{info} *Discovered by {member.display_name}*")
        await ctx.send(embed=embed)
        
    @commands.command(name='dino')
    async def dino_info(self,ctx, dino_name=None):
        """
        Shows dino info
        """
        if dino_name:
            dino = StaticDino.get(name=dino_name.lower())
        else:
            dino = random.choice(StaticDino.get())
        if not dino:
            await ctx.send(embed=discord.Embed(description=f'No information about {dino_name.capitalize()}.'))
            return
        if dino.isDiscovered(ctx.message.guild.id) or ctx.message.author.id == 139839031402823680:
            await ctx.send(embed=dino.getEmbed())
        else:
            await ctx.send(embed=discord.Embed(description=f'{dino.name.capitalize()} has not been discovered yet.'))
    
    
    async def ask_for_img(self, ctx, dino_name=None, dino = None):
        """
        Shows profile of a dino by its name and lists all images of it
        """
        if not dino:
            if dino_name:
                dino = StaticDino.get(name=dino_name.lower())
            else:
                dino = random.choice(StaticDino.get())
                
        if not dino:
            await ctx.send(embed=discord.Embed(description=f'No information about {dino_name.capitalize()}.'))
        
        e = dino.getEmbed()
            
        if dino.isDiscovered(ctx.message.guild.id):
            pass
        else:
            e.description = "Not discovered yet."

        
        t = f'`Type the number of an image to set it as the main one. Discord previews only first 5 images.\nFirst image is the current one.`\n'
        for i,iu in enumerate(dino.all_image_urls_list):
            t += f'`{i+1}` {iu}\n'
        msg = await ctx.send(t)
        
        def check(m):
            return m.channel == ctx.message.channel and m.author.id == ctx.message.author.id
        try:
            resp = await self.bot.wait_for('message', check=check, timeout=120.0)
        except:
            await ctx.send(f"{ctx.message.author.name} TIMEOUT")
            return
        try:
            picked_idx = int(resp.content)-1
        except:
            await ctx.send(f"Wrong format.")
            return
        if picked_idx < 0 or picked_idx > len(dino.all_image_urls_list)-1:
            await ctx.send(f"Wrong number.")
            return
        
        picked_img = dino.all_image_urls_list[picked_idx]
        dino.setImage(picked_img)
        dino.is_image_random = False
        Dbh.session.commit()
        await msg.delete()
        await resp.delete()
        await ctx.send(embed=greenEmbed('Image changed'))
        return True
    
    @commands.command(name='dinoimage')
    async def dino_image(self,ctx, dino_name=None):
        """
        Shows dino's replacement images and allows them to be changed
        """
        await self.ask_for_img(ctx,dino_name)
        
    @commands.command(name='dinoimages')
    async def dino_images(self,ctx, dino_name=None):
        """
        Shows dino's replacement images and allows them to be changed in a loop
        """
        s = True
        while s:
            dino = random.choice(StaticDino.get(is_image_random=True))
            s = await self.ask_for_img(ctx,dino=dino)
        
    @commands.command(name='deletedino',hidden=True)
    async def delete_info(self,ctx, dino_name):
        """
        Shows profile of a dino by its name
        """
        dino = StaticDino.getDino(dino_name.lower())
        StaticDino.removeFromFile([dino,])
        Dbh.session.commit()
        await ctx.send("deleted")

        
    @commands.command(name='gibdino',hidden=True)
    async def gibdino(self,ctx,target:discord.Member=None,count=1):
        """
        Shows profile of a dino by its name
        """
        #target = ctx.message.author or target
        profile = JP.get(target)
        # dino = random.choice(StaticDino.getAll())
        # #owned_dino = ProfileDino(profile,dino)
        # #Dbh.session.add(owned_dino)
        # dino._drop(profile)
        for _ in range(count):
            await StaticDino.dropEvent(target,profile,silent=True)
            #pds = ProfileDino.get(profile_id=profile.id)
        #await ctx.send('\n'.join([pd.briefText for pd in pds]))
            
            
    @commands.command(name='gibres',hidden=True)
    async def gibres(self,ctx,a,b,c,target:discord.Member=None):
        a = int(a)
        b = int(b)
        c = int(c)
        target = target or ctx.message.author
        profile = JP.get(target)
        resources = profile.resources
        resources.addResources([a,b,c])
        Dbh.commit()
        
    @commands.command(name='ratedinos')
    async def ratedinos(self,ctx,dino_name=None,review=False):
        """
        Rates dinos which are currently randomized
        """
        if dino_name == "review":
            dino_name = None
            review = True


        my_channel = self.bot.get_guild(247039921825513472).get_channel(595291660728926218)
        to_remove = []
        if dino_name:
            dinolist = StaticDino.get(as_list=True,name=dino_name)
        else:
            dinolist = StaticDino.get(as_list=True,is_random=not review)
        i = -1
        while len(dinolist):
            i += 1
            if not dino_name:
                dinolist = StaticDino.get(as_list=True,is_random=not review)
            dino = random.choice(dinolist)
            n_total = len(StaticDino.get())
            breaker = False
            embed = dino.getEmbed()
            n_set = len(StaticDino.get(as_list=True,is_random=False))
            inf = f"{n_set}/{n_total} dinos set."
            eft = embed.footer.text+"\n" if embed.footer.text else ''
            embed.set_footer(text=eft+f"[{inf}]\n💡 img - wyświetla ponumerowaną listę dostępnych obrazków zamiennych. Aby wybrać obrazek wpisz jego numer na czacie.\n💡 1,2,3,4,5 - ustawia statystyki dinozaura na 1dmg, 2def, 3hp, 4speed, 5tier\n💡 set - zatwierdza obecne statystyki i obrazek\n💡 skip - kolejny dino\n💡 stop - koniec przegladania")
#💡 del - usuwa dinozaura z listy jeśli ma chujowe zdjecia, albo ogolnie jest meh\n
            msg = await ctx.send(embed=embed)

            def check(m):
                return m.channel == ctx.message.channel and m.author.id == ctx.message.author.id
            
            try:
                resp = await self.bot.wait_for('message', check=check, timeout=400.0)
            except:
                await ctx.send(f"{ctx.message.author.name} TIMEOUT")
                return
            
            
            resp = resp.content
            
            if resp == 'img':
                await self.ask_for_img(ctx,dino=dino)

                try:
                    resp = await self.bot.wait_for('message', check=check, timeout=400.0)
                except:
                    await ctx.send(f"{ctx.message.author.name} TIMEOUT")
                    return
                resp = resp.content
            
            if resp == 'set':
                dino.is_random = False
                dino.is_image_random = False
                continue
            
            elif resp == 'skip':
                continue
            
            elif resp == 'stop':
                Dbh.session.commit()
                break
            
            # elif resp == 'del':
            #     StaticDino.removeFromFile([dino,])
            #     e = discord.Embed(description=f"{dino.name.capitalize()} został usunięty.")
            #     e.colour = discord.Colour.from_rgb(255,0,0)
            #     await msg.edit(embed=e)
            #     Dbh.session.commit()
            #     continue
            
            else:
                stats = resp.split(',')
                mappers = [(int,(0,10)),(int,(0,10)),(int,(1,10)),(int,(1,10)),(int,(1,5))]
                for i, stat in enumerate(stats):
                    try:
                        stats[i] = mappers[i][0](stat)
                    except:
                        await ctx.send(f'Niepoprawny argument "{stat}"')
                        return
                    if not(mappers[i][1][0] <= stats[i] <= mappers[i][1][1]):
                        await ctx.send(f'Niepoprawna wartość {stats[i]}, zakres wartości dla tej statystyki to {mappers[i][1]}')
                        return
                dino.damage = stats[0]
                dino.armor  = stats[1]
                dino.health = stats[2]
                dino.speed  = stats[3]
                dino.tier   = stats[4]
                dino.is_random = False

            if breaker:
                break

            Dbh.session.commit()
            e = dino.getEmbed()
            e.color = discord.Colour.from_rgb(0,255,0)
            e.set_footer(text="Edycja Pomyślna")
            await msg.edit(embed=e)
  
            
            
            
    async def find_channels(self):
        self.channels = {}
        for guild in self.bot.guilds:
            self.channels[guild.id] = []
            for channel in guild.voice_channels:
                static_dino = StaticDino.getDinoFromChannelName(channel.name)
                if static_dino:
                    self.channels[guild.id].append(channel)
        
    async def shuffle_channels(self,bot,g,gs):
        
        time = str((datetime.now()+timedelta(hours=1)).time())[:5]
        category = None
        self.visitors[g.id] = {}
        for vc in g.voice_channels:
            if not vc.category:
                continue
            
            if vc.category.id == gs.voice_cat:
                dino = StaticDino.getRandomDinoTierWise()
                category = vc.category
                
                if dino.isDiscovered(g.id):
                    emoji = StaticDino.emoji
                    tier = f" ᴛ{dino.tier}"
                else:
                    emoji = '❓'
                    tier = ''
                    
                    tier = f" ᴛ{dino.tier}" ##############
                await vc.edit(name=f"{emoji} {dino.name.capitalize()}"+tier)

        if category:
            await category.edit(name=f"Jurassic Park @{time}")
        
        
    @commands.command(name='shuffle',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def shuffle_command(self,ctx):
        gs = JGuildSettings.get(ctx.message.guild.id)
    
        await self.shuffle_channels(self,ctx.message.guild,gs)
        
        
        
    @commands.command(name='cadd',hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def cadd(self,ctx,name=None):
        await self.core(limit=False,dino_name=name)

    
    async def core(self,limit=True,dino_name=None):
        for g in self.bot.guilds:
            gs = JGuildSettings.get(g.id)
            if not gs.voiceReady:
                continue
            category = gs.category
            dino = random.choice(StaticDino.get(is_random=False,tier=round(random.triangular(1, 5, 5)))) if not dino_name else StaticDino.get(is_random=False,as_list=False,name=dino_name)
            if not dino:
                print("NO DINO")
                return
            if dino.isDiscovered(g.id):
                emoji = StaticDino.EMOJI
                tier = f" ᴛ{dino.tier}"
            else:
                emoji = '❓'
                tier = ''
            
            
            channel = None
            if len(self.channels[g.id]) >= 4 and limit:
                channel = random.choice(self.channels[g.id])
                await channel.edit(name=f"{emoji} {dino.name.capitalize()}"+tier)
            else:
                channel = await category.create_voice_channel(f"{emoji} {dino.name.capitalize()}"+tier)
                
            r = random.randint(0,len(category.voice_channels))
            if r != len(category.voice_channels):
                await channel.edit(position=r)
                
    async def simpleChannelDropLoop(self):
        while True:
            await self.find_channels()
            await self.core()
            await asyncio.sleep(1600)

    async def loop(self):
        while True:
            shuffled = False
            rewarded = False
            
            for g in self.bot.guilds:
            
                # if time.time() - self.last_shuffle > self.shuffle_interval:
                #     gs = JGuildSettings.get(g.id)
                #     if not gs.voiceReady:
                #         continue
                #     await self.shuffle_channels(self,g,gs)
                #     shuffled = True

                    
                if time.time() - Resources.last_update > Resources.update_interval:
                    for profile in JP.get(as_list=True,guild_id=g.id):
                        member = g.get_member(profile.member_id)
                        rewards = Rewards.getMemberReward(member)
                        profile.resources.addResources(rewards)
                        
                    rewarded = True

            # if shuffled:
            #     self.last_shuffle = time.time()
            if rewarded:
                Resources.last_update = time.time()
                Dbh.session.commit()
            await asyncio.sleep(50)

    def setupDB(self):
        Dbh.init()

        # Dbh.session.execute('DROP TABLE discovery;')
        # Dbh.session.execute('DROP TABLE resources;')
        # Dbh.session.execute('DROP TABLE jurassicprofile;')
        # Dbh.session.execute('DROP TABLE part;')
        # Dbh.session.execute('DROP TABLE profile_dino;')
        # Dbh.session.execute('DROP TABLE profile_dino_part;')
        # Dbh.session.execute('DROP TABLE profile_entity;')



        Dbh.createTables()
        #StaticDino.updateDinos()
        dinos = StaticDino.get()
        DinoPart.update(dinos)
        JP.updateProfiles()
        Resources.updateResources(JP.get(as_list=True))
        
        
        for dino in dinos:
            dino.map_image_url = ""
        print(f"{len(JP.get(as_list=True))} Profiles IN TOTAL")
        print(f"{len(Resources.getAll())} Resources IN TOTAL")
        print(f"{len(StaticDino.get())} Dinos IN TOTAL")
       
       

            
        Dbh.session.commit()
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            gs = JGuildSettings.get(guild.id)
            if not gs:
                o = JGuildSettings(guild.id)
                Dbh.session.add(o)
                Dbh.session.commit()
            for member in guild.members:
                if member.bot:
                    JP.get(member)
        
        
        self.bot.loop.create_task(self.loop())
        self.bot.loop.create_task(self.simpleChannelDropLoop())
        
    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        v = veh(member,before,after,self)
        await v.handle()

def setup(_bot):
    bot = _bot
    cog = JurrasicPark(_bot)
    cog.setupDB()
    bot.add_cog(cog)
    
