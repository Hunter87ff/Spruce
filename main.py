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
import datetime
from datetime import datetime, timedelta
import json
from data import *
import requests
import pymongo
from pymongo import MongoClient
#import mysql.connector
#import humanfriendly
#from data.badwords import bws
#from discord.ui import Button, View




pref = '&'
intents= discord.Intents.default()
intents.members = True

#Configuring db
dburl = os.environ["monog_url"]
maindb = MongoClient(dburl)
userdb = maindb["userdb"]
userdbc = userdb["userdbc"]


def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or("&")(bot, message)

    with open("data/prefixes.json", "r") as f:
        prefixes = json.load(f)

    if str(message.guild.id) not in prefixes:
        return commands.when_mentioned_or("&")(bot, message)

    prefix = prefixes[str(message.guild.id)]
    return commands.when_mentioned_or(prefix)(bot, message)


bot = commands.Bot(command_prefix= get_prefix, allowed_mentions = discord.AllowedMentions(roles=True, users=True, everyone=True), intents=intents )



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
	
	
	
@bot.command()
async def store(ctx):
    crd = ctx.author.created_at.strftime("%a, %#d %B %Y, %I:%M %p")
    data = {"id" : int(ctx.author.id),"name" : ctx.author.name,"created_at" : crd}
    usrd = userdbc.find_one({"id" : ctx.author.id})
    usrid = usrd["id"]
    if usrid == ctx.author.id:
        return await ctx.send("already stored")

    elif usrid != ctx.author.id:
        userdbc.insert_one(data)
        return await ctx.send("Your data stored")
   
     
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
@commands.bot_has_permissions(manage_channels=True, manage_messages=True, send_messages=True)
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
@commands.bot_has_permissions(manage_messages=True, send_messages=True)
async def ping(ctx):
    await ctx.send(f'**Current ping is {round(bot.latency*1000)} ms**')

@bot.command()
@commands.bot_has_permissions(manage_messages=True, send_messages=True, embed_links=True)
async def botinfo(ctx):
  emb = discord.Embed(title="Spruce Bot", description="Welcome To Spruce", color=discord.Color.blurple())
  emb.add_field(name="<:server:968372588533383178> __Servers Info__", value=f"Total server : {len(bot.guilds)}\nTotal Members : 17593", inline=False)
  emb.add_field(name="<:owner:968371297744744448> __Owner__", value="[Hunter#6967](https://discord.com/users/885193210455011369)", inline=False)
  emb.add_field(name="<:g_latency:968371843335610408> __Current Ping__", value=f"{round(bot.latency*1000)} ms", inline=False)
  emb.add_field(name="<:setting:968374105961300008> __Command Prefix__", value="prefix: & , command: &help", inline=False)
  emb.set_footer(text=f"Made with ❤️ | By hunter#6967")
  return await ctx.send(embed=emb)


@bot.command()
@commands.guild_only()
@commands.bot_has_permissions(manage_webhooks=True)
async def say(ctx, *, message):      
    for w in await ctx.channel.webhooks():
        wurl = w.url
       
    data = {
    "content" : "",
    "avatar_url" : f"{ctx.author.avatar_url}",
    "username" : f"{ctx.author.name}"
}
    data["embeds"] = [
    {
        "description" : f"{message}",
        "title" : "",
        "color" : 0xffff00
    }]    
    try:
        #await ctx.channel.purge(limit=1)
        requests.post(wurl, json = data)

        
    except:
        await ctx.channel.send("**I think this channel has no any webhooks, don't worry i've created one! now you can try**")
        await ctx.channel.create_webhook(name="Spruce")




bot.run(os.environ['TOKEN'])
