from datetime import datetime
import random
from .dino_info import StaticDino
from ..utils.dbconnector import DatabaseHandler as Dbh
from ..utils.copy import Copy
import discord
from .dino_info import ProfileDino, DinoStatEmojis as DSE
from sqlalchemy import Column, ForeignKey, Float, Integer, BigInteger, String, TIMESTAMP, Boolean, orm
from .resources import ResourcesBase
from ..utils.imageutils import averageColor
from .entities.entity import EntityBase
from ..utils.general import splitList


class DataBattle(Dbh.Base, EntityBase):
    __tablename__ = "battle"

    id = Column(Integer, primary_key=True)
    attacker_profile_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    defender_profile_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    winner_profile_id = Column(Integer, ForeignKey('jurassicprofile.id'))
    destruction = Column(Boolean)

    def __init__(self,atk_prof,def_prof,winner_prof,destruction):
        self.attacker_profile_id = atk_prof.id
        self.defender_profile_id = def_prof.id
        self.winner_profile_id = winner_prof.id
        self.destruction = destruction


# class Player:
#     def __init__(self,army,buildings,)

class DinoBattle:
    MAX_TURNS = 10
    
    def __init__(self, atk_army, def_army):
        self.timestamp = datetime.now()
        
        self.atk_army = atk_army
        self.def_army = def_army
    
        self.turns = 0
    
        self.winner = None
        self.outcome = 'Battle in progress..'

        self.plunder = None
        

    def getEmbed(self):
        at_d = self.atk_army.profile.member.display_name
        df_d = self.def_army.profile.member.display_name
        title = f'Battle between {at_d} and {df_d}'
        if self.winner:
            e = '🏆'
        else:
            e = ''
        status = f"{e} {self.outcome}"
        the_title = f"{e} {self.winner.member.display_name}" if self.winner else "TIE"
        
        imgurl = self.winner.member.avatar_url_as(format='png') if self.winner else ''
        color = averageColor(imgurl)
        if color:
            color = discord.Colour.from_rgb(color[0],color[1],color[2])
            embed = discord.Embed(title=the_title,color=color)
        else:
            embed = discord.Embed(title=the_title)
        
        embed.set_author(name=title)
        embed.set_thumbnail(url=imgurl)
        
        embed.add_field(name=f'{at_d} Army {len(self.atk_army.starting_dinos)} → {len(self.atk_army.getAliveDinos())}',value=self.atk_army.getSummary() or "{DSE.emojis['blank']}",inline=False)
        embed.add_field(name=f'{df_d} Army {len(self.def_army.starting_dinos)} → {len(self.def_army.getAliveDinos())}',value=self.def_army.getSummary() or "{DSE.emojis['blank']}")
        
        if self.turns:
            embed.set_footer(text=f'Battle lasted {self.turns} turns.')
        
        if self.plunder:
            embed.add_field(name='Plunder',value=f'{self.plunder.asText()}',inline= False)
        
        return embed
    

    def modifiers(self):
        for army in (self.def_army, self.atk_army):
            for modifier in army.modifiers:
                modifier(self)
    
    def start(self):
        self.modifiers()
        self.battleLoop()
        self.healing()
        self.getSummary()
        
        if self.winner == self.atk_army.profile:
            self.plunder = self.atk_army.plunderResources(self.def_army)
    
        self.healing2()
        self.dying()
        Dbh.commit()
        
    def healing(self):
        self.def_army.heal()
    
    def healing2(self):
        for army in (self.def_army, self.atk_army):
            for dino in army.healed_dinos:
                dino.alive = True
    
    def dying(self):
        for army in (self.def_army, self.atk_army):
            for dino in army.getDeadDinos():
                dino.die()
    
    def isFinished(self):
        if not self.atk_army.isAlive() or not self.def_army.isAlive():
            return True

    def getSummary(self):
        both_alive = self.atk_army.isAlive() and self.def_army.isAlive()
        both_dead = self.atk_army.isAlive() == False and self.def_army.isAlive() == False
        if both_alive or both_dead:
            self.outcome = 'TIE'
        elif self.atk_army.isAlive():
            self.outcome = f'{self.atk_army.profile.member.display_name} WINS'
            self.winner = self.atk_army.profile
        elif self.def_army.isAlive():
            self.outcome = f'{self.def_army.profile.member.display_name} WINS'
            self.winner = self.def_army.profile
        if not self.def_army.isAlive():
            self.def_army.profile.last_destroyed = self.timestamp
            
    def battleLoop(self):
        while not self.isFinished() and self.turns < self.MAX_TURNS:
            self.turns += 1
            self.atk_army.attack(self.def_army)
            self.def_army.attack(self.atk_army)
            


    def __str__(self):
        return f"[{self.timestamp}] Battle between {self.atk_army.profile.member.display_name} and {self.def_army.profile.member.display_name}.\nWinner: {self.winner}\nSummary: {self.outcome}\nTurns: {self.turns}"



class ArmyPreview:
    CONTROLS = {
        'prev' : u'◀',
        'next' : u'▶',
        'reload': u'🔃',
        'stop' : u'⏹'
    }
    
    def __init__(self,cog,profile,profile_dinos):
        self.cog = cog
        self.profile = profile
        self.dinos = list(sorted(profile_dinos,key = lambda x: (x.count,5-x.entity.tier),reverse=True))
        self.page_idx = 0
        self.dino_split_list = splitList(self.dinos,10)
        self.total_pages = len(self.dino_split_list)
        
        self.tiers = {1:0, 2:0, 3:0, 4:0, 5:0}
        for dino in self.dinos:
            tier = dino.entity.tier
            self.tiers[tier] += dino.count
    def getList(self):
        return self.dino_split_list[self.page_idx] if self.total_pages else self.dino_split_list
    
    
    async def start(self,ctx):
        embed = self.getEmbed(self.getList())
        msg = await ctx.send(embed=embed)
        if len(self.dino_split_list) > 1:
            await msg.add_reaction(ArmyPreview.CONTROLS['prev'])
            await msg.add_reaction(ArmyPreview.CONTROLS['next'])
        
        await msg.add_reaction(ArmyPreview.CONTROLS['reload'])
        await msg.add_reaction(ArmyPreview.CONTROLS['stop'])
        
        def check(reaction, user):
            return user.id == ctx.message.author.id and reaction.message.id == msg.id
        
        while True:
            try:
                reaction, user = await self.cog.bot.wait_for('reaction_add', check=check, timeout=50.0)
            except:
                break
            if reaction.emoji == ArmyPreview.CONTROLS['stop']:
                await msg.delete()
                return
            if reaction.emoji == ArmyPreview.CONTROLS['reload']:
                self.setup()
                pass
            
            starting_page_idx = self.page_idx
            
            if reaction.emoji == ArmyPreview.CONTROLS['next']:
                self.page_idx = self.page_idx + 1 if self.page_idx < self.total_pages - 1 else self.page_idx
            if reaction.emoji == ArmyPreview.CONTROLS['prev']:
                self.page_idx = self.page_idx - 1 if self.page_idx > 0 else self.page_idx
            
            if self.page_idx != starting_page_idx or reaction.emoji == ArmyPreview.CONTROLS['reload']:
                embed = self.getEmbed(self.getList())
                await msg.edit(embed=embed)
                await msg.remove_reaction(reaction.emoji,ctx.message.author)


    def getEmbed(self,dinos):
        
        
        total_stats = StaticDino.sumStats([dino.entity for dino in dinos],as_text=True)
        
        embed = discord.Embed(title = f"ARMY - {sum([dino.count for dino in self.dinos])} Dinosaurs",color=discord.Color.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        embed.set_author(name=self.profile.member.display_name,icon_url=self.profile.member.avatar_url_as(format='png'))
        embed.set_thumbnail(url='https://compote.slate.com/images/73f8ce3a-7952-48d5-bbf3-c4e25dc3a144.jpeg')
        
        
     
        
        c = 1
        for i,dino in enumerate(dinos):
            
            ct = f' x{dino.count}' if dino.count > 1 else ''
            embed.add_field(name=f"`{c} {DSE.emojis['dino1']} T{dino.entity.tier}{ct}` {dino.entity.name.upper()}",value=DSE.emojis['blank']+dino.entity.stats_as_string(),inline=False)
            c += dino.count
        
        if len(dinos):
            description = f"`🔥` Power: {total_stats}\n"
            ts = []
            for i in range(0,5):
                ts.append(f"`T{i+1}: {self.tiers[i+1]}`")
            tier_txt=DSE.emojis['blank'].join(ts)
            description += tier_txt
            embed.description = description
        page_txt = f'[Page: {self.page_idx+1}/{self.total_pages}]\n' if len(self.dino_split_list) > 1 else ''
        embed.set_footer(text=page_txt)
        return embed

class Army:
    
    def __init__(self, profile, profile_dinos,fleed=False,targets=[],ignores=[]):
        self.profile = profile
        self.starting_dinos = []
        self.dinos = []
        self.healed_dinos = []
        self.resources = profile.resources.copy()
        self.modifiers = []
        self.fleed = fleed
        self.targets = targets
        self.ignores = ignores
        for pd in profile_dinos:
            for _ in range(pd.count):
                d = Dino(profile_dino=pd)
                self.dinos.append(d)
                self.starting_dinos.append(d.copy())
        
        
        
    def flee(self):
        self.capacity = self.getCapacity()  
        self.starting_dinos = []
        self.dinos = []
        self.modifiers = []
        self.fleed = True
        
        
        
    def getAliveDinos(self,shuffle=False):
        dinos = [dino for dino in self.dinos if dino.alive]
        if shuffle:
            dinos = random.sample(dinos,len(dinos))
        return dinos
        
    def getDeadDinos(self):
        return [dino for dino in self.dinos if not dino.alive]
        
    def heal(self):
        for dino in self.getDeadDinos():
            if random.uniform(0,1) <= 0.25-(2*dino.tier*0.01):
                #dino.alive = True
                self.healed_dinos.append(dino)
    def attack(self, target_army):
        for dino in self.getAliveDinos(shuffle=True):
            ta = target_army.getAliveDinos()
            if not ta:
                break
            target = random.choice(ta)
            dino.attack(target)
            target.attack(dino)#########

    def isAlive(self):
        return len(self.getAliveDinos()) > 0
        
    def __str__(self):
        return f"ARMY\nProfile: {self.profile}\nDinos: {self.dinos}"
    
    def getPower(self):
        return StaticDino.sumStats(self.starting_dinos)
            
    
    def getSummary(self):
        t = []
        dinos_names = [dino.name for dino in self.getAliveDinos()]
        dead_names = [dino.name for dino in self.getDeadDinos()]
        total_stats = StaticDino.sumStats(self.starting_dinos,as_text=True)
        t.append(f"`🔥` Power: {total_stats}")
        
        checked = []
        dinos = list(set(self.starting_dinos))
        
        starting_names = [dino.name for dino in self.starting_dinos]
        
        healed_names = [dino.name for dino in self.healed_dinos]
        
        if self.fleed:
            return "Army has escaped."
        elif len(self.starting_dinos) == 0:
            return "No army encountered."
        
        for dino in list(sorted(dinos,key = lambda x: (dinos_names.count(x.name),dead_names.count(x.name),healed_names.count(x.name)),reverse=True)):
            if dino.name in checked:
                continue
            checked.append(dino.name)
            n_healed = healed_names.count(dino.name)
            healed_text =  f' ({n_healed} healed)' if n_healed else ''
            text = f'`{DSE.emojis["dino1"]} T{dino.tier}` **{dino.name.capitalize()}** `{starting_names.count(dino.name)}` → `{dinos_names.count(dino.name)}{healed_text}`'
            t.append(text)
        total_stats = StaticDino.sumStats([dino.static_dino for dino in self.getAliveDinos()],as_text=True)
        
        if len(self.starting_dinos):
            t.append(f"`💀` Survived: {total_stats}")
        
 
        while len("\n".join(t)) > 1024:
            t.pop(-2)
        return "\n".join(t)

    def getCapacity(self):
        capacity = ResourcesBase()
        for dino in self.getAliveDinos():
            base_cap = int(50*dino.health/dino.tier)
            capacity.shit += base_cap
            capacity.wood += int(base_cap*0.75)
            capacity.gold += int(base_cap*0.25)
        return capacity

    def plunderResources(self,target_army):
        temp_res = target_army.profile.resources.copy()
        temp_res = temp_res*0.5
        
        capacity = self.getCapacity()
        
        target_army.profile.resources.steal(capacity)
        self.profile.resources.addResources(capacity.resources)

        return capacity

class Damage:
    
    def __init__(self,value,source,target=None):
        self.value = value
        self.source = source
        self.target = target


class Dino(Copy):
    
    def __init__(self,static_dino=None,profile_dino=None,count=1,modifiers=[]):
        if static_dino or profile_dino:
            self.pd = profile_dino
            self.static_dino = self.pd.entity if self.pd else static_dino
            self.count = count
            self.name = self.static_dino.name
            self.tier = self.static_dino.tier
            self.damage = self.static_dino.damage
            self.armor = self.static_dino.armor
            self._health = self.static_dino.health
            self.speed = self.static_dino.speed
            self.modifiers = modifiers
            self.alive = True

    @property
    def health(self):
        return self._health
    
    @health.setter
    def health(self, value):
        self._health = value
        if self._health <= 0 and self.alive:
            self.alive = False
            #self.die()
            
    def die(self):
        if self.pd:
            self.pd.count -= 1
    
    def getDamage(self):
        return Damage(self.damage,self)
    
    def attack(self,dino):
        print(f'{self.name}#{self.static_dino.entity_id}{self.statsBrief()} attacks {dino.name}#{dino.static_dino.entity_id}{dino.statsBrief()}')
        i = 1
        while i == 1 or (random.uniform(0,1) < (self.getSpeedRatio(dino)*0.1)/i and dino.alive):
            damage = self.getDamage()
            damage.target = dino
            dino.getHit(damage,consecutive=i)
            i += 1
            
    def getSpeedRatio(self,source):
        try:
            speed_ratio = self.speed/source.speed
        except:
            speed_ratio = (self.speed-1)*0.25
        return speed_ratio
    
    def canDodge(self,damage,kwargs):
        consecutive = kwargs.get('consecutive',1)
        speed_ratio = self.getSpeedRatio(damage.source)
        if speed_ratio > 7.5:
            speed_ratio = 7.5
        if random.uniform(0,10) < speed_ratio/consecutive:
            return True     
        return False
    
    def statsBrief(self):
        return f"[{self.damage}DMG|{self.health}HP|{self.armor}ARMOR]"
    
    def damageArmorReduce(self,damage):
        if self.armor <= 0:
            return

        start_armor = self.armor
        
        new_armor = start_armor - damage.value
        self.armor = new_armor if new_armor >= 0 else 0
        
        damage.value -= start_armor
        if damage.value < 0:
            damage.value = 0
    
    def reduceDamage(self,damage):
        self.damageArmorReduce(damage)
    
    
    def takeDamage(self,damage):

        self.health -= damage.value
        print(f'    {self.health} after attack')
    
    def getHit(self,damage,**kwargs):
        print(f' INCOMING {damage.value} DAMAGE')
        if self.canDodge(damage,kwargs):
            return
        
        self.reduceDamage(damage)
        self.takeDamage(damage)
    
