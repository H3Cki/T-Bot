import discord
from discord.ext import commands
import sys, traceback
from datetime import datetime
import platform

# Below cogs represents our folder our cogs are in. Following is the file name. So 'meme.py' in cogs, would be cogs.meme
# Think of it like a dot path import
#initial_extensions = ['cogs.fight','cogs.drops','cogs.games','cogs.general','cogs.cs,r6','cogs.diary','cogs.q','cogs.markov']
initial_extensions = ['cogs.jurassicpark','cogs.slot']
bot = commands.Bot(command_prefix="!", description=f'Nazywam się Arkowiec, jestem najlepszym botem na świecie.\n\nOS: {platform.system()}\nPlatform: {platform.platform()}\nVersion: {platform.version()}\nCPU: {platform.processor()}')

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

@bot.event
async def on_ready():
    """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    print(f'[{datetime.now()}] Successfully logged in and booted...!')


bot.run("NjYzMTk5MzQ1OTE0NTQ0MTM4.XhFC3Q.p096XpB7m65BRzpVtITp9kdkSAc",reconnect=True)

