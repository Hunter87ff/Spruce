import os
import discord
from discord.ext import commands
#from discord.ui import Button, View
from keep_alive import keep_alive
from asyncio import sleep




bot = commands.Bot(command_prefix=commands.when_mentioned_or('&'),intents=discord.Intents.all())


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='&help'))
  
    print('bot is ready')

	

  
#prefix command
@bot.command()
async def prefix(ctx):
    await ctx.send(' **<:vf:947194381172084767>My prefix is  `&` ** ')


@bot.command()
async def sav(ctx):
	guild = ctx.guild
	await ctx.send(guild.icon_url)

  
##########################################################################################
#                                          USER AND SERVER COMMANDS
############################################################################################
@bot.command()
async def av(ctx, member: discord.Member=None):
    await ctx.send(member.avatar_url)


	
	
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
  
  
  
##########################################################################################
#                                          TEXT COMMANDS
############################################################################################

class Nhelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page, color = discord.Color.red())
#           emby.add_field(name='Support Server', value='[join](https://discord.gg/FXbRZHz3cG)', inline = False)
            await destination.send(embed=emby)
bot.help_command = Nhelp()

'''
#say command
@bot.command()
@commands.has_permissions(manage_channels=True)
async def say(ctx, *, msg):
    await ctx.channel.purge(limit=1)
    await ctx.send(msg)
'''



  
#embed command
@bot.command()
async def emb(ctx, *, msg):
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

'''
#clear command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'**<:vf:947194381172084767> Successfully cleared {amount} messages**',delete_after=5)


"""@bot.command()
@commands.has_permissions(manage_messages=True)
async def poll(ctx, emojis, *, message):
  for emoji in emojis:
    emb = discord.Embed(description=f"{message}", color= 4*5565)
    msg = await ctx.channel.send(embed=emb)
    await msg.add_reaction(emoji)
"""



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
#                                          ROLE COMMANDS
############################################################################################



'''
@bot.command()
@commands.has_permissions(administrator=True)
async def delroles(ctx):
  for role in ctx.guild.roles:
    try:
      await role.delete()
    except:
      await ctx.send(f"I can't delete {role.name}")
'''


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
@bot.command(help="**Use this command to crate roles\nExample: &crole Family**")
@commands.has_permissions(manage_roles=True)
async def crole(ctx, *names):
    for name in names:
        guild = ctx.guild
        await guild.create_role(name=name)
        await ctx.send(f"**<:vf:947194381172084767> Role `{name}` has been created**")


#delet role
@bot.command()
@commands.has_permissions(manage_roles=True)
async def drole(ctx, *roles: discord.Role):
    for role in roles:
        await ctx.send(f'**<:vf:947194381172084767> Role {role.name} has been deleted**')
        await role.delete()
        await ctx.channel.purge(limit=2)


#role give
@bot.command(pass_context=True,help="Use this command to give role to someone \nExample : &role @hunter @family ")
@commands.has_permissions(administrator=True)
async def role(ctx, role: discord.Role, *users: discord.Member):
    for user in users:
        await user.add_roles(role)
        await ctx.send(f"<:vf:947194381172084767> {role.mention} has been given to {user.mention}")


#role remove
@bot.command(pass_context=True,help="Use this command to remove role from someone \n \n Example : &rrole @role @hunter ")
@commands.has_permissions(administrator=True)
async def rrole(ctx, role: discord.Role, user: discord.Member):
    await user.remove_roles(role)
    await ctx.send(f"<:vf:947194381172084767> {role.mention} has been removed from {user.mention}")


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
async def chmake(ctx, *names):
    for name in names:
        await ctx.guild.create_text_channel(name)
        await ctx.send(f'**<:vf:947194381172084767>`{name}` has been created**',delete_after=5)
        await sleep(1)


#channel delete
@bot.command(aliases=['chd'])
@commands.has_permissions(manage_channels=True)
async def chdel(ctx, *channels: discord.TextChannel):
    for ch in channels:
        await ch.delete()
        await ctx.send(f'**<:vf:947194381172084767>`{ch.name}` has been deleted**',delete_after=5)
        await sleep(1)


############################################################################################
#                                       KICK / BAN / MUTE
############################################################################################


#kick command
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if reason == None:
        reason = " no reason provided"
    await ctx.guild.kick(member)
    await ctx.send(f'User {member.mention} has been kicked for {reason}')


#ban command
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if reason == None:
        reason = " no reason provided"
    await ctx.guild.ban(member)
    await ctx.send(f'User {member.mention} has been baned for {reason}')


########################################################################################
#                                       INFO
############################################################################################



  
#bot info
@bot.command(help="print the detsil of the bot")
async def about(ctx):

    embed = discord.Embed(
        title=ctx.guild.name,
        description="**My name is Hunter 87\nI was built by Hunter.\nNow I have limited features\nfind out more by typing `&help` **",color=discord.Color.blue())
    await ctx.send(embed=embed)


  
#check latency
@bot.command()
async def ping(ctx):
    await ctx.send(f'**Current ping is {round(bot.latency*1000)} ms**')




keep_alive()
bot.run(os.environ['TOKEN'])
