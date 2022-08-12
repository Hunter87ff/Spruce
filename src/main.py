import os 
import discord
from discord.ext import commands
from asyncio import sleep
import datetime
from datetime import datetime, timedelta
from data import *
import requests
import pymongo
import json
from pymongo import MongoClient
from modules import (message_handel, channel_handel, checker, config, color)
onm = message_handel
ochd = channel_handel
from discord.ui import Button, View




intents = discord.Intents.default()
intents.message_content = True
pref = os.environ["prefix"]


#Configuring db
dburl = os.environ["mongo_url"]
maindb = MongoClient(dburl)






bot = commands.Bot(command_prefix= commands.when_mentioned_or("&"), intents=intents ) 
#allowed_mentions = discord.AllowedMentions(roles=True, users=True, everyone=True),


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f'{pref}help'))
    await load_extensions()
    print(f'{bot.user} is ready')



nitrodbc = maindb["nitrodb"]["nitrodbc"]
async def nitrof(message):
    if message.author.bot:
        return
    try:
        gnitro = nitrodbc.find_one({"guild" : message.guild.id})
    except:
        return

    if gnitro != None and gnitro["nitro"] == "enabled":
        try:
            webhook = discord.utils.get(await message.channel.webhooks(), name="Spruce")

        except:
            message.reply("Missing Permissions - `manage_messages` , `manage_webhooks`")

        if webhook == None:
            try:
                webhook = await message.channel.create_webhook(name="Spruce")

            except:
                await message.reply("Missing Permissions - `manage_messages` , `manage_webhooks`")
       
                
        words = message.content.split()
        for word in words:
            if word[0] == ":" and word[-1] == ":":
                emjn = word.replace(":", "")
                emoji = discord.utils.get(bot.emojis, name=emjn)
                if emoji != None:
                    if emoji.name in message.content:
                        msg = message.content.replace(":","").replace(f"{emoji.name}" , f"{emoji}")
                        allowed_mentions = discord.AllowedMentions(everyone = False, roles=False, users=True)
                        nick = message.author.nick
                        if message.author.nick == None:
                            nick = message.author.name
                        await webhook.send(avatar_url=message.author.display_avatar, content=msg, username=nick, allowed_mentions= allowed_mentions)
                        await message.delete()
                        




    

@bot.event
async def on_message(message):
    await onm.tourney(message)
    await nitrof(message)
    await bot.process_commands(message)
   
   
	
@bot.event
async def on_guild_channel_delete(channel):
    await ochd.ch_handel(channel)
	
	
	
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
        err = discord.Embed(color=0xff0000, description="Missing Required Arguments")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.MissingPermissions):
        err = discord.Embed(color=0xff0000, description="You don't have Permissions To Use This Command")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.DisabledCommand):
        err = discord.Embed(color=0xff0000, description="This Command Is Currently Disabled! You Can Try Again Later")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.CommandNotFound):
        err = discord.Embed(color=0xff0000, description="Command Not Found! Please Check Spelling Carefully.")
        return await ctx.send(embed=err)


    elif isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
        err = discord.Embed(color=0xff0000, description="You Do Not Have The Exact Role To Use This Command")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.UserInputError):
        err = discord.Embed(color=0xff0000, description="Please Enter Valid Arguments")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.EmojiNotFound):
        err = discord.Embed(color=0xff0000, description="Emoji Not Found")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.NotOwner):
        err = discord.Embed(color=0xff0000, description="This Is A Owner Only Command You Cant Use It")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.MessageNotFound):
        err = discord.Embed(color=0xff0000, description="Message Not Found Or Deleted")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.MemberNotFound):
        err = discord.Embed(color=0xff0000, description="Member Not Found")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.ChannelNotFound):
        err = discord.Embed(color=0xff0000, description="Channel Not Found")
        return await ctx.send(embed=err)

    elif isinstance(error, commands.ChannelNotReadable):
        err = discord.Embed(color=0xff0000, description="Can Not Read Messages Of The Channel")
        return await ctx.send(embed=err)


    else:
        e = str(error)
        await ctx.send(f"```py\n{e}```")





@bot.command()
@commands.dm_only()
async def cdm(ctx,amount:int):
  dmchannel = await ctx.author.create_dm()
  async for message in dmchannel.history(limit=amount):
    if message.author == bot.user:
      await message.delete()






############################################################################################
#                                       INFO
############################################################################################
  

@bot.command()
@commands.cooldown(2, 20, commands.BucketType.user)
@commands.bot_has_permissions(manage_messages=True, send_messages=True)
async def ping(ctx):
    await ctx.send(f'**Current ping is {round(bot.latency*1000)} ms**')





@bot.command()
@commands.bot_has_permissions(manage_messages=True, send_messages=True, embed_links=True)
async def botinfo(ctx):
  emb = discord.Embed(title="Spruce Bot", description="Welcome To Spruce", color=discord.Color.blurple())
  emb.add_field(name="<:server:968372588533383178> __Servers Info__", value=f"Total server : {len(bot.guilds)}\nTotal Members : 29721", inline=False)
  emb.add_field(name="<:owner:968371297744744448> __Owner__", value="[Hunter#6967](https://discord.com/users/885193210455011369)", inline=False)
  emb.add_field(name="<:g_latency:968371843335610408> __Current Ping__", value=f"{round(bot.latency*1000)} ms", inline=False)
  emb.add_field(name="<:setting:968374105961300008> __Command Prefix__", value="prefix: & , command: &help", inline=False)
  emb.set_footer(text=f"Made with ❤️ | By hunter#6967")
  return await ctx.send(embed=emb)






@bot.command()
@commands.guild_only()
@commands.bot_has_permissions(manage_emojis=True)
async def addemoji(ctx, emoji: discord.PartialEmoji):
    if ctx.author.guild_permissions.manage_emojis:
        for g in bot.guilds:
            if g.id != ctx.guild.id:
                #emoji = discord.utils.get(g.emojis, name=name)
                await ctx.send(f"{emoji} added", delete_after=10)
                emoji_bytes = await emoji.read()
                await ctx.guild.create_custom_emoji( name=emoji.name, image=emoji_bytes, reason=f'Emoji Added By {ctx.author}')
    else:
        return await ctx.send("You Should Check Your Permission")




@bot.command(hidden=True)
async def sdm(ctx, member: discord.User, *, message):
    if ctx.author.id == 885193210455011369:
        await member.send(message)
    if ctx.author.id != 885193210455011369:
        return await ctx.send("Command not found! please check the spelling carefully")





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



if os.environ["status"] == "On":
	bot.run(os.environ['TOKEN'])
