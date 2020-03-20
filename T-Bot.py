import discord
from discord.ext import commands
import sys, traceback
from datetime import datetime
import platform
from cogs import botinstance as bi


initial_extensions = ['cogs.jurassicpark']
bot = commands.Bot(command_prefix="!", description=f'Nazywam się Arkowiec, jestem najlepszym botem na świecie.\n\nOS: {platform.system()}\nPlatform: {platform.platform()}\nVersion: {platform.version()}\nCPU: {platform.processor()}')
bi.bot = bot

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

bot.run("NjYzMTk5MzQ1OTE0NTQ0MTM4.XnOQ-Q._mDaza2i1KKqUUpOLFEBtpxGg2U",reconnect=True)


