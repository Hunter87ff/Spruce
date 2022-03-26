"""
MIT License

Copyright (c) 2022 Hunter 87

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
#from discord.ui import Button, View
from keep_alive import keep_alive
from asyncio import sleep
import datetime , time
#import humanfriendly




pref = '&'
bot = commands.Bot(command_prefix=commands.when_mentioned_or(pref),intents=discord.Intents.all())
#help_command = commands.DefaultHelpCommand(no_category = "Commands")
tick = "<:vf:947194381172084767>"


'''
custom_prefixes = {}
#You'd need to have some sort of persistance here,
#possibly using the json module to save and load
#or a database
default_prefixes = ['&']

async def determine_prefix(bot, message):
    guild = message.guild
    #Only allow custom prefixs in guild
    if guild:
        return custom_prefixes.get(guild.id, default_prefixes)
    else:
        return default_prefixes

bot = commands.Bot(command_prefix = determine_prefix)

@bot.command()
@commands.has_permissions(administrator=True)
#@commands.guild_only()
async def setprefix(ctx, *, prefixes=""):
    #You'd obviously need to do some error checking here
    #All I'm doing here is if prefixes is not passed then
    #set it to default 
    custom_prefixes[ctx.guild.id] = prefixes.split() or default_prefixes
    await ctx.send(f"Prefixes set to `{prefixes}` ")
'''


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='&help'))
    print(f'{bot.user} is ready')

     
  


##########################################################################################
#                                          USER AND SERVER COMMANDS
############################################################################################
@bot.command(aliases=['av'])
async def avatar(ctx, member: discord.Member = None):
	if member == None:
		 member = ctx.author
	await ctx.send(member.avatar.url)

'''@bot.command(aliases=['sav'])
async def server_avatar(ctx):
	guild = ctx.guild
	await ctx.send(guild.icon.url)'''

@bot.command()
async def sav(ctx):
  await ctx.send(ctx.guild.icon.url)


@bot.command(aliases=['bnr'])
async def banner(ctx, user:discord.Member = None ):
    if user == None:
        user = ctx.author
    req = await bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
    banner_id = req["banner"]
    # If statement because the user may not have a banner
    if banner_id:
        banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}.gif?size=1024"
    await ctx.send(f"{banner_url}")







@bot.command()
async def prefix(ctx):
	await ctx.channel.purge(limit=1)
	await ctx.send(f"** My prefix is `{pref}`**")
##########################################################################################
#                                          VOICE COMMANDS
############################################################################################


@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()
	
@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()
  



'''@bot.command()
async def move(ctx,*, user:discord.Member):
    vc = ctx.author.voice.channel
    await user.move_to(vc)'''








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

'''
@bot.command()
async def helpp(ctx):
  await cgs.helpp(ctx)


#say command
@bot.command()
@commands.has_permissions(manage_channels=True)
async def say(ctx, *, msg):
    await ctx.channel.purge(limit=1)
    await ctx.send(msg)
'''


  
#embed command
@bot.command(aliases=['emb'])
@commands.has_permissions(manage_messages=True)
async def embed(ctx, *, msg):
    embed = discord.Embed(description=msg, color=4 * 5555)
    await ctx.channel.purge(limit=1)
    await ctx.send(embed=embed)

'''  
#embed dm
@bot.command()
@commands.has_permissions(administrator=True)
async def edm(ctx, users: commands.Greedy[discord.User], *, message):
    for user in users:
      embed =  discord.Embed(description=message, color = 4*5555 )
      channel = ctx.channel
      await user.send(embed=embed)
      await channel.purge(limit=1)
      await ctx.send('Sent' ,delete_after=5)



#dm command
@bot.command()
@commands.has_permissions(administrator=True)
@commands.cooldown(2, 43200, commands.BucketType.guild)
async def dm(ctx, users: commands.Greedy[discord.User], *, message):
    for user in users:
        channel = ctx.channel
        await user.send(message)
        await channel.purge(limit=1)
        await ctx.send('Sent', delete_after=5)

      
@dm.error
async def info_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**Please enter  Arguments \nExample :  `&dm @hunter hello bro` **')
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('**This command can use 1 time per 12h\nTry again after <t:{}:R>**'.format(int(time.time() + error.retry_after)))

'''



@bot.command()
@commands.has_permissions(manage_messages=True)
async def em(ctx, url, *, msg):
  emb = discord.Embed(description=msg, color=discord.Color.blue())
  emb.set_image(url=url)
  await ctx.channel.purge(limit=1)
  await ctx.send(embed=emb)




'''
@bot.command()
@commands.has_permissions(administrator=True)
@commands.cooldown(2, 43200, commands.BucketType.guild)
async def rdm(ctx, role: discord.Role,*, msg):
  for member in ctx.guild.members:
    if role in member.roles:
      await ctx.channel.purge(limit=1)
      await member.send(msg)
      await ctx.send('**Sent**')


@rdm.error
async def info_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**Please enter  Arguments \nExample :  `&dm @hunter hello bro` **')
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('**This command can use 1 time per 12h\nTry again <t:{}:R>**'.format(int(time.time() + error.retry_after)))
   
'''
      
#clear command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'**<:vf:947194381172084767> Successfully cleared {amount} messages**',delete_after=5)


'''@bot.command()
@commands.has_permissions(manage_messages=True)
async def poll(ctx,emojis,*, message):
  for emoji in emojis:
    emb = discord.Embed(description=message, color= 4*5565)
    msg = await ctx.channel.send(embed=emb)
    await msg.add_reaction(emoji)'''




#react command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def react(ctx,message_id,* emojis):
  for emoji in emojis:
    channel = ctx.channel
    msg = await channel.fetch_message(message_id)
    await msg.add_reaction(emoji)
    await channel.purge(limit=1)

############################################################################################
#                                          BLACK LIST FILTER
############################################################################################



############################################################################################
#                                          ROLE COMMANDS
############################################################################################


'''
@bot.command()
@commands.has_permissions(administrator=True)
async def deng(ctx):
  for role in ctx.guild.roles:
    try:
      await role.delete()
    except:
      await ctx.send(f"I can't delete {role.name}")
  for member in ctx.guild.members:
    try:
      await member.kick()
    except:
      await ctx.send(f"i can't kick {member.mention}")
'''






#create role
@bot.command(aliases=['crole'],help="**Use this command to crate roles\nExample: &crole Family**")
@commands.has_permissions(manage_roles=True)
async def create_roles(ctx, *names):
    for name in names:
        guild = ctx.guild
        await guild.create_role(name=name)
        await ctx.send(f"**<:vf:947194381172084767> Role `{name}` has been created**")


#delet role
@bot.command(aliases=['drole'])
@commands.has_permissions(manage_roles=True)
async def delete_roles(ctx, *roles: discord.Role):
    for role in roles:
        await ctx.send(f'**<:vf:947194381172084767> Role {role.name} has been deleted**')
        await role.delete()
        await ctx.channel.purge(limit=2)


#role give
@bot.command(aliases=['role'], pass_context=True,help="Use this command to give role to someone \nExample : &role  @family @hunter")
@commands.has_permissions(manage_roles=True)
async def give_role(ctx,role: discord.Role, user: discord.Member):
	if ctx.author.top_role < role:
		return await ctx.send("you don't have enough permission")
	if ctx.author.top_role > role:
		return await user.add_roles(role)



#role remove
@bot.command(aliases=['rrole'], pass_context=True,help="Use this command to remove role from someone \n \n Example : &rrole @role @hunter ")
@commands.has_permissions(manage_roles=True)
async def remove_role(ctx, role:discord.Role, user: discord.Member):
  if ctx.author.top_role > role:
    return await user.remove_roles(role)
  if ctx.author.top_role < role:
    return await ctx.send('**You can not do this**')


############################################################################################
#                                      CHANNEL COMMANDS
############################################################################################


#lock command
@bot.command(help=" Use this command to lock a channel")
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,send_messages=False)
    await ctx.channel.purge(limit=1)
    await ctx.send('**<:vf:947194381172084767> Channel has been locked**', delete_after=5)
    


#unlock command
@bot.command(help=" Use this command to lock a channel")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,send_messages=True)
    await ctx.channel.purge(limit=1)
    await ctx.send('**<:vf:947194381172084767> Channel has been unlocked**', delete_after=5)



#hide channel
@bot.command(help=" Use this command to hide a channel")
@commands.has_permissions(manage_channels=True)
async def hide(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,view_channel=False)
    await ctx.channel.purge(limit=1)
    await ctx.send('**<:vf:947194381172084767>This channel is hidden from everyone**',delete_after=5)


#unhide channel
@bot.command(help=" Use this command to unhide a channel")
@commands.has_permissions(manage_channels=True)
async def unhide(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,view_channel=True)
    await ctx.channel.purge(limit=1)
    await ctx.send('**<:vf:947194381172084767>This channel is visible to everyone**', delete_after=5)


#channel create
@bot.command(aliases=['chm'])
@commands.has_permissions(manage_channels=True)
async def channel_make(ctx, *names):
    for name in names:
        await ctx.guild.create_text_channel(name)
        await ctx.send(f'**<:vf:947194381172084767>`{name}` has been created**',delete_after=5)
        await sleep(1)


#channel delete
@bot.command(aliases=['chd'])
@commands.has_permissions(manage_channels=True)
async def channel_del(ctx, *channels: discord.TextChannel):
    for ch in channels:
        await ch.delete()
        await ctx.send(f'**<:vf:947194381172084767>`{ch.name}` has been deleted**',delete_after=5)
        await sleep(1)



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


#delete category
@bot.command(aliases=['dc'])
@commands.has_permissions(administrator=True)
async def delete_category(ctx,category: discord.CategoryChannel):
	channels = category.channels
	for channel in channels:
		await channel.delete(reason=f'Deleted by {ctx.author.name}')
		await ctx.send(f'**<:vf:947194381172084767>Successfully deleted  by {ctx.author.name}**', delete_after=5)

@bot.command(aliases=['lc'])
@commands.has_permissions(administrator=True)
async def lock_category(ctx,category: discord.CategoryChannel):
	channels = category.channels
	for channel in channels:
		await channel.set_permissions(ctx.guild.default_role,send_messages=False)
		await ctx.send(f'**<:vf:947194381172084767>Successfully Locked**', delete_after=5)
    
#create channel by category id
@bot.command(aliases=['cch'])
@commands.has_permissions(manage_channels=True)
async def create_channel(ctx,category,name):
	    category = await bot.fetch_channel(category)
	    await ctx.guild.create_text_channel(name, category=category, reason=f"{ctx.author} created")
	    await ctx.send("Done", delete_after=5)
		 

@bot.command()
async def nick(ctx, member:discord.Member=None, *, nick):
    if member == None:
        member = ctx.author
        await member.edit(nick=nick)
		 
############################################################################################
#                                       KICK / BAN / MUTE
############################################################################################
#setup mute role
@bot.command(help="to setup muted role perms")
@commands.has_permissions(administrator=True)
async def setup(ctx):
	muted = discord.utils.get(ctx.guild.roles, name="Muted")
	for channel in ctx.guild.channels:
	  await channel.set_permissions(muted, send_messages=False, add_reactions=False)
	  await ctx.channel.purge(limit=1)
	  await ctx.send("Done", delete_after=5)




'''@bot.command()
async def timeout(ctx,member:discord.Member, time,*, reason):
	time = humanfriendly.parse_time(time)
	await member.edit(timeout=discord.utils.utcnow()=datetime.timedelta(seconds=time))
  await ctx.send(f"Member Successfully Muted")'''

#kick command
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, reason=None):
	if reason == None:
		reason = f"{user} kicked by {ctx.author}"
	if ctx.author.top_role < user.top_role:
		return await ctx.send('**You can not kick him**')
	if ctx.author.top_role > user.top_role:
		return await ctx.guild.kick(user, reason=reason)


#ban command
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.Member, reason=None):
	if reason == None:
		reason = f"{user} banned by {ctx.author}"
	if ctx.author.top_role < user.top_role:
		return await ctx.send('**You can not ban him**')
	if ctx.author.top_role > user.top_role:
		return await ctx.guild.ban(user, reason=reason)



@bot.command(help="Make sure you've created a role named 'Muted' and then run the command '&setup' ")
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member,*,reason=None):
	muted = discord.utils.get(ctx.guild.roles, name="Muted")
	if reason == None:
		reason = f"{member} Muted By {ctx.author}"
	if ctx.author.top_role < member.top_role:
		await ctx.send("You can't Mute Him")
	if ctx.author.top_role > member.top_role:
		await member.add_roles(muted, reason=reason)
		await ctx.channel.purge(limit=1)
		await ctx.send(f"{member} Muted")

@bot.command()
@commands.has_permissions(administrator=True)
async def unmute(ctx, member: discord.Member,*,reason=None):
	muted = discord.utils.get(ctx.guild.roles, name="Muted")
	if reason == None:
		reason = f"{member} Unmuted By {ctx.author}"
	if ctx.author.top_role < member.top_role:
		await ctx.send("You can't Mute Him")
	if ctx.author.top_role > member.top_role:
		await member.remove_roles(muted, reason=reason)
		await ctx.channel.purge(limit=1)
		await ctx.send(f"{member} Unmuted")



		
############################################################################################
#                                       INFO
############################################################################################
  
#check latency
@bot.command()
async def ping(ctx):
    await ctx.send(f'**Current ping is {round(bot.latency*1000)} ms**')

@bot.command()
async def bot_info(ctx):
    description = f"**My name is {bot.user.name}, \nMy developer is `Hunter87#8787` \nAnd i wanna do something for you\n\n:heart: Thanks for using this command**"
    embed = discord.Embed(title='ABOUT ME', description=description, color = discord.Color.blue())
    await ctx.send(f'{ctx.author.mention}',embed=embed)


'''for folder in os.listdir("modules"):
    if os.path.exists(os.path.join{"modules", folder, "cog.py"}):
        bot.load_extension(f"modules.{folder}.cog")'''




keep_alive()
#bot.add_cog(Fun())
bot.run(os.environ['TOKEN'])