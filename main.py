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

bot = commands.Bot(command_prefix=commands.when_mentioned_or(pref))



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
            emby.add_field(name="Links", value="[Support Server](https://discord.gg/vMnhpAyFZm)")
#           emby.add_field(name='Support Server', value='[join](https://discord.gg/FXbRZHz3cG)', inline = False)
            await destination.send(embed=emby)
bot.help_command = Nhelp(no_category = 'Commands')




@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**Please enter required Arguments **')
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send('**Try again <t:{}:R>**'.format(int(time.time() + error.retry_after)))
      
    elif isinstance(error, commands.MissingPermissions):
      return await ctx.send("You don't have permission to use this command")

    elif isinstance(error, commands.DisabledCommand):
      await ctx.send("This command is currenlty disabled. Please try again later")

    elif isinstance(error, commands.CommandNotFound):
      await ctx.send("**Command not found! please check the spelling carefully*")
      print(ctx.message.content)

    elif isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
      await ctx.send("You dont have the exact role to use this command")

    else:
        return await ctx.send("Something went wrong!")




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

############################################################################################
#                                      CHANNEL COMMANDS
############################################################################################

#tournament setup (category and channels)
@bot.command(aliases=['ts','tsetup'])
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
#                                      GAME ROLES 
############################################################################################
    
    
    
    
gborder = "https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/star_border.gif"

ffemb = discord.Embed(title="FREE FIRE", description="**Garena Free Fire is a battle royal game. Played by millions of people. Developed by 111 dots studio and published by Garena. React on the emoji to access this game!**", color=discord.Color.blurple())
ffemb.set_thumbnail(url="https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/freefire.png")


bgmiemb = discord.Embed(title="BGMI", description="**Battlegrounds Mobile India(BGMI), Made for players in India. It is an online multiplayer battle royale game developed and published by Krafton. React on the emoji to access this game**", color=discord.Color.blurple())
bgmiemb.set_thumbnail(url="https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/bgmi.png")


codemb = discord.Embed(title="CALL OF DUTY", description="**Call Of Duty is a multiplayer online battle royal game, developed by TiMi Studio Group and published by Activision.react on the emoji to access this game**", color=discord.Color.blurple())
codemb.set_thumbnail(url="https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/codm.png")

valoemb = discord.Embed(title="VALORANT", description="**Valorant is a multiplayer online battle royal game made for pc, developed and published by Riot Games. react on the emoji to access this game**", color=discord.Color.blurple())
valoemb.set_thumbnail(url="https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/valorant.png")






@bot.command()
@commands.has_permissions(manage_messages=True)
async def grole(ctx):
  await ctx.send(embed=valoemb)
  await ctx.send(gborder)
  await ctx.send(embed=codemb)
  await ctx.send(gborder)
  await ctx.send(embed=bgmiemb)
  await ctx.send(gborder)
  await ctx.send(embed=ffemb)

		
############################################################################################
#                                       INFO
############################################################################################
  
#check latency
@bot.command()
async def ping(ctx):
    await ctx.send(f'**Current ping is {round(bot.latency*1000)} ms**')

@bot.command()
async def bot_info(ctx):
    description = f"**My name is {bot.user.name}, \nMy developer is `hunter#6967` \nAnd i wanna do something for you\n\n:heart: Thanks for using this command**"
    embed = discord.Embed(title='ABOUT ME', description=description, color = discord.Color.blue())
    await ctx.send(f'{ctx.author.mention}',embed=embed)




bot.run(os.environ['TOKEN'])
