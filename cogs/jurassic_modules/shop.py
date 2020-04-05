import discord
import asyncio
from ..utils.general import splitList
from .dino_info import ProfileDino, StaticDino, DinoStatEmojis as DSE
import random
from .resources import ResourcesBase
from .entities.droppable import Droppable
from ..utils.dbconnector import DatabaseHandler as Dbh

class Shop:
    numbers = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','0️⃣']
    nr_to_react = {1:'1️⃣', 2:'2️⃣', 3:'3️⃣', 4:'4️⃣', 5:'5️⃣',6:'6️⃣',7:'7️⃣',8:'8️⃣',9:'9️⃣',0:'0️⃣'}
    react_to_nr = {key:value for (value,key) in nr_to_react.items()}
    controls_names = {
        'prev' : u'◀',
        'next' : u'▶',
        'back': u'⬅',
        'confirm' : u'✅',
        'stop' : u'⏹'
    }
    controls_to_names = {key:value for (value,key) in controls_names.items()}
    controls1 = [controls_names['prev'],controls_names['next']]
    controls2 = [controls_names['confirm'],controls_names['back'],controls_names['stop']]
    reaction_bar_cls = controls1 + numbers + controls2
    
    state_to_text = {
        'selecting_dino':  'Select dinosaur you want to buy.\nConfirm to finish.',
        'selecting_count': 'Select quantity.\nConfirm to continue.',
        'finished':        'Shopping finished.\nYour goods will be delivered soon.',
        'finished_empty':  'Shopping finished.\nYou bought nothing.'
    }
    
    def __init__(self,profile,member,cog=None,naked=False):
        self.profile = profile
        self.member = member
        self.cog = cog
        self.page_idx = 0
        self.dinos = list(sorted([dino for dino in StaticDino.get(is_random=False) if dino.isDiscovered(self.profile.guild.id)],key = lambda x: (5-x.tier,x.name)))
        self.dino_split_list = splitList(self.dinos,9)
        self.total_pages = len(self.dino_split_list)
        if len(self.dinos):
            self.reaction_bar = Shop.controls1 + Shop.numbers + Shop.controls2 if self.total_pages > 1 else Shop.numbers + Shop.controls2
        else:
            self.reaction_bar = []
        self.cart = []
        self.cost = ResourcesBase()
        
    def getList(self):
        return self.dino_split_list[self.page_idx] if self.total_pages else self.dino_split_list
    
    async def addReactions(self,msg):
        for reaction in self.reaction_bar:
            await msg.add_reaction(reaction)
        
    def removeReaction(self,react):
        pass
    
    def updateCost(self):
        self.cost = ResourcesBase()
        for dino,count in self.cart:
            dc = (dino.buildCost()*5)*(count or 1)
            self.cost += dc
    
    def getAction(self,reaction):
        return self.controls_to_names.get(reaction,None) or self.react_to_nr.get(reaction,None)
    
    
    async def start(self,ctx):
        self.state = 'selecting_dino'
        embed = self.getEmbed(self.getList(),ctx)
        msg = await ctx.send(embed=embed)
        self.cog.bot.loop.create_task(self.addReactions(msg))

        def check(reaction, user):
            return user.id == self.member.id and reaction.message.id == msg.id
        
        
        self.count_buffer = ''
        while True:
            
            try:
                done, pending = await asyncio.wait([self.cog.bot.wait_for('reaction_remove', check=check, timeout=60.0),self.cog.bot.wait_for('reaction_add', check=check, timeout=60.0)], return_when=asyncio.FIRST_COMPLETED)
                for future in pending:
                    future.cancel()
                reaction, user = done.pop().result()
            except:
                break
            
            
            action = self.getAction(reaction.emoji)
      

            starting_page_idx = self.page_idx
            if action == 'next':
                self.page_idx = self.page_idx + 1 if self.page_idx < self.total_pages - 1 else self.page_idx
            if action == 'prev':
                self.page_idx = self.page_idx - 1 if self.page_idx > 0 else self.page_idx
            if action == 'back':
                if len(self.cart):
                    last_one = self.cart[-1]
                    if last_one[1] > 10:
                        self.cart[-1][1] = int(self.cart[-1][1]/10)
                    else:
                        self.cart.pop(-1)
                        self.state = 'selecting_dino'
                    self.updateCost()

           
            if action == 'stop':
                await msg.delete()
                return
            
            # STEP 1 -> SELECT DINO
            dino_picked = False
            if self.state == 'selecting_dino':
                if action == 'confirm':
                    res = self.profile.resources
                    if res > self.cost:
                        if len(self.cart):
                            self.state = 'finished'
                        else:
                            self.state = 'finished_empty'
                        break
                    else:
                        embed=self.getEmbed(self.getList(),ctx)
                        embed.description = "❗ You don't have enough resources to buy these items."
                        await msg.edit(embed=embed)
                        continue
                shop_item = [None,0]
                if isinstance(action,int):
                    if action == 0:
                        action = 1
                    dino = self.dino_split_list[self.page_idx][action-1]
                    shop_item[0] = dino
                    
                    self.cart.append(shop_item)
                    self.updateCost()
                    dino_picked = True
            # STEP 2 -> SELECT COUNT OR CONFIRM 1
            if self.state == 'selecting_count':
                if action == 'confirm':
                    self.state = 'selecting_dino'
                    await msg.edit(embed=self.getEmbed(self.getList(),ctx))
                    continue
                if isinstance(action,int):
                    self.cart[-1][1] *= 10
                    self.cart[-1][1] += action
                    self.updateCost()
                
            # STATE CHANGE
            if self.state == 'selecting_dino' and dino_picked:
                self.state = 'selecting_count'


            
            
            await msg.edit(embed=self.getEmbed(self.getList(),ctx))
                 
        await msg.edit(embed=self.getEmbed(self.getList(),ctx))       
        
        if len(self.cart):
            reward = []
            for item in self.cart:
                for _ in range(item[1] or 1):
                    reward.append(item[0])
            await Droppable.dropEvent(self.member,self.profile,items=reward,silent=True)
            res = self.profile.resources
            res -= self.cost
            Dbh.commit()
            
    def getEmbed(self,dinos,ctx):
        
        res = self.profile.resources
        #desc = f"Resources: {res.asText()}"
        desc = None
        embed = discord.Embed(title = f"{ctx.message.guild.name} Shop - {len(self.dinos)} Dinosaurs" ,description=desc,color=discord.Color.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        embed.set_author(name=self.member.display_name,icon_url=self.member.avatar_url_as(format='png'))
        #embed.set_thumbnail(url='https://i.imgur.com/s1xRSYT.png')
        
        texts = []
        
        for i,dino in enumerate(dinos):    
            emoji = DSE.emojis['dino1']
            stats_txt = f'{dino.stats_as_string()}'
            embed.add_field(name=f"`{i+1} {emoji} T{dino.tier}` {dino.name.capitalize()} {stats_txt}",value=(dino.buildCost()*5).asText(),inline=False)
        
        embed.add_field(name=f"Cost/Resources",value=res.compareAsText(self.cost,'\n',reverse_void=True))
        embed.add_field(name=f"Shopping List" if self.state != 'finished' else 'Purchased Goods',value=', '.join(f'`{DSE.emojis["dino1"]}`{i[0].name.capitalize()} x{i[1] or 1}' for i in self.cart) or DSE.emojis['blank'])
        embed.set_footer(text=f'[Page {self.page_idx+1}/{self.total_pages}] {self.state_to_text[self.state]}')
        return embed