import os, app,discord, random, requests, wavelink
from asyncio import sleep
from discord.ext import commands
from wavelink.ext import spotify
from modules import (message_handel, channel_handel, config)
#from discord.ext.commands.converter import (MemberConverter, RoleConverter, TextChannelConverter)
from modules.bot import bot


##########################################################################################
#                                       COMMANDS
############################################################################################

def mmbrs(ctx=None):
    i = 0
    for guild in bot.guilds:
        i = i + guild.member_count
    return i

@bot.hybrid_command(with_app_command = True, aliases=["bi","stats", "about", "info", "status", "botstats"])
@commands.cooldown(2, 60, commands.BucketType.user)
@commands.bot_has_permissions(send_messages=True, embed_links=True)
async def botinfo(ctx):
    await ctx.defer(ephemeral=True)
    emb = discord.Embed(title="Spruce Bot", description="Welcome To Spruce", color=discord.Color.blurple())
    mmbs = mmbrs()
    emb.add_field(name=f"{config.servers}__Servers Info__", value=f"Total server : {len(bot.guilds)}\nTotal Members : {mmbs}", inline=False)
    emb.add_field(name=f"{config.developer} __Developer__", value="[Hunter#6967](https://discord.com/users/885193210455011369)", inline=False)
    emb.add_field(name=f"{config.ping} __Current Ping__", value=random.choice(range(19,28)), inline=False)
    emb.add_field(name=f"{config.setting} __Command Prefix__", value=f"command: {pref}help, prefix: {pref}  ", inline=False)
    emb.set_footer(text="Made with ❤️ | By hunter#6967")
    return await ctx.send(embed=emb)

app.keep_alive()
bot.run(config.token)