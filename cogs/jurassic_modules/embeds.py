import discord
from discord import Embed
from datetime import datetime, timedelta

no_storage_warning = 'Your lab is full! Clean up some space by building currently unfinished dinos.\n❗ Storing more parts than your lab can contain can lead to explosion 💥 which will destroy everything inside it.'

def dropEmbed(member,static_part,nostorage=False):
    e = Embed(title=member.display_name,description=f'{static_part.getEmoji()} **{static_part.dino_name.capitalize()}** {static_part.type}')
    footer = str((datetime.now()+timedelta(hours=1)).time())[:5]
    if nostorage:
        footer += f"\n{no_storage_warning}"
    e.set_footer( text= footer)
    return e

def itemDropEmbed(member, items, nostorage=False):
    
    if isinstance(items,list):
        text = "\n".join([item.dropText for item in items])
    else:
        text = items.dropText
        
    footer = str((datetime.now()+timedelta(hours=1)).time())[:5]
    if nostorage:
        footer += f"\n{no_storage_warning}"
        
    e = Embed(title=member.display_name,description=text)
    e.set_footer( text= footer)
    return e

def discoveryEmbed(member,static_dino):
    de = static_dino.getEmbed()
    de.set_footer(text=f'New discovery by {member.display_name}')
    return de

def noStorageEmbed(member):
    return Embed(description=f"{member.mention} {no_storage_warning}")

def destructionEmbed(member):
    return Embed(description=f"❗ {member.mention} Your lab has exploded 💥 due to overload, you lost everything.")

def greenEmbed(descr):
    return Embed(description=descr,colour=discord.Colour.from_rgb(25,255,0))
def redEmbed(descr):
    return Embed(description=descr,colour=discord.Colour.from_rgb(255,25,25))