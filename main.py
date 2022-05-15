"""
MIT License

Copyright (c) 2022 Spruce

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


import os 
import discord
from discord.ext import commands
from asyncio import sleep
import datetime , time
import json
from data import *

#import humanfriendly
#from data.badwords import bws
#from discord.ui import Button, View




pref = '&'
intents= discord.Intents.default()
intents.members = True


def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or(",")(bot, message)

    with open("data/prefixes.json", "r") as f:
        prefixes = json.load(f)

    if str(message.guild.id) not in prefixes:
        return commands.when_mentioned_or(",")(bot, message)

    prefix = prefixes[str(message.guild.id)]
    return commands.when_mentioned_or(prefix)(bot, message)


bot = commands.Bot(command_prefix=commands.when_mentioned_or(pref), allowed_mentions = discord.AllowedMentions(roles=False, users=True, everyone=False))



# Load extensions
#bot.load_extension('cogs.mod')
#bot.load_extension('cogs.utils')



for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

#help_command = commands.DefaultHelpCommand(no_category = "Commands")
#tick = "<:vf:947194381172084767>"



@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='&help'))
    print(f'{bot.user} is ready')
    

     


##########################################################################################
#                                          TEXT COMMANDS
############################################################################################

class Nhelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page, color = discord.Color.blurple())
            emby.add_field(name="Links", value="[Support Server](https://discord.gg/vMnhpAyFZm) | [Invite Link](https://discord.com/oauth2/authorize?client_id=931202912888164474&permissions=139992746070&scope=bot)")
#           emby.add_field(name='Support Server', value='[join](https://discord.gg/FXbRZHz3cG)', inline = False)
            await destination.send(embed=emby)
bot.help_command = Nhelp(no_category = 'Commands')




@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**Please enter required Arguments **') 

    elif isinstance(error, commands.MissingPermissions):
        return await ctx.send("You don't have permission to use this command")
        print(ctx.message.content)

    elif isinstance(error, commands.DisabledCommand):
        return await ctx.send("This command is currenlty disabled. Please try again later")
        print(ctx.message.content)

    elif isinstance(error, commands.CommandNotFound):
        return await ctx.send("**Command not found! please check the spelling carefully**")
        print(ctx.message.content)

    elif isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
        return await ctx.send("You dont have the exact role to use this command")
        print(ctx.message.content)

    elif isinstance(error, commands.UserInputError):
        return await ctx.send("**Invalid input**")
        print(ctx.message.content)

    else:
        e = str(error)
        await ctx.send(f"```py\n{e}```")

'''
    else:
        return await ctx.send("Something went wrong!")
        print(ctx.message.content)

'''


@bot.command()
@commands.dm_only()
async def cdm(ctx,amount:int):
  dmchannel = await ctx.author.create_dm()
  async for message in dmchannel.history(limit=amount):
    if message.author == bot.user:
      await message.delete()

"""
@bot.event
async def on_message(msg):
    if ":" == msg.content[0] and ":" == msg.content[-1]:
        emoji_name = msg.content[1:-1]
        for emoji in msg.guild.emojis:
            if emoji_name == emoji.name:
                await msg.channel.send(str(emoji))
                await msg.delete()
                break
    await bot.process_commands(msg)
"""

############################################################################################
#                                          BLACK LIST FILTER
############################################################################################

"""
@bot.event
async def on_message(message):
    for word in bws:
        if word in message.content:
            await message.channel.purge(limit=1)
            

"""

snipe_message_author = {}
snipe_message_content = {}


@bot.event
async def on_message_delete(message):
     snipe_message_author[message.channel.id] = message.author
     snipe_message_content[message.channel.id] = message.content
     await sleep(60)
     del snipe_message_author[message.channel.id]
     del snipe_message_content[message.channel.id]

@bot.command()
@commands.cooldown(2, 10, commands.BucketType.user)
async def snipe(ctx):
    channel = ctx.channel
    try:
        em = discord.Embed(color=discord.Color.blue(), description = snipe_message_content[channel.id])
        em.set_footer(text=snipe_message_author[channel.id], icon_url=snipe_message_author[channel.id].avatar_url)
        await ctx.send(embed=em)
    except KeyError: #This piece of code is run if the bot doesn't find anything in the dictionary
        await ctx.send(f"No recently deleted messages in {channel.mention}", delete_after=10)



############################################################################################
#                                      CHANNEL COMMANDS
############################################################################################

#tournament setup (category and channels)
@bot.command(aliases=['ts','tsetup'])
@commands.cooldown(2, 20, commands.BucketType.user)
@commands.has_permissions(manage_channels=True)
async def tourney_setup(ctx,front,*,category=None):
    reason= f'Created by {ctx.author.name}'
    category = await ctx.guild.create_category(category, reason=f"{ctx.author.name} created")
    await category.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.guild.create_text_channel(str(front)+"info", category=category, reason=reason)
    await ctx.guild.create_text_channel(str(front)+"updates", category=category,reason=reason)
    await ctx.guild.create_text_channel(str(front)+"roadmap", category=category,reason=reason)
    await ctx.guild.create_text_channel(str(front)+"how-to-register", category=category, reason=reason)
    await ctx.guild.create_text_channel(str(front)+"register-here", category=category, reason=reason)
    await ctx.guild.create_text_channel(str(front)+"confirmed-teams", category=category, reason=reason)
    await ctx.guild.create_text_channel(str(front)+"groups", category=category, reason=reason)
    await ctx.guild.create_text_channel(str(front)+"queries", category=category, reason=reason)
    await ctx.send(f'**<:vf:947194381172084767>Successfully Created**',delete_after=5)

		
############################################################################################
#                                       INFO
############################################################################################
  
#check latency
@bot.command()
@commands.cooldown(2, 20, commands.BucketType.user)
async def ping(ctx):
    await ctx.send(f'**Current ping is {round(bot.latency*1000)} ms**')

@bot.command()
async def botinfo(ctx):
  emb = discord.Embed(title="Spruce Bot", description="Welcome To Spruce", color=discord.Color.blurple())
  emb.add_field(name="<:server:968372588533383178> __Servers Info__", value=f"Total server : {len(bot.guilds)}\nTotal Members : 11898")
  emb.add_field(name="<:owner:968371297744744448> __Owner__", value="[Hunter#6967](https://discord.com/users/885193210455011369)")
  emb.add_field(name="<:g_latency:968371843335610408> __Current Ping__", value=f"{round(bot.latency*1000)} ms")
  emb.add_field(name="<:setting:968374105961300008> __Command Prefix__", value="prefix: & , command: &help")
  emb.add_field(name="<:python:968372024537931786> __Language__", value="Python 3.9")
  emb.set_footer(text=f"Made with ❤️ | By hunter#6967")
  return await ctx.send(embed=emb)







bot.run(os.environ['TOKEN'])
'''
try:
    bot.run(os.environ['TOKEN'])
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING...\n\n\n")
    system("python restarter.py")
    system('kill 1')
'''