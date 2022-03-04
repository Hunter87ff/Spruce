import discord
import os
import asyncio
from discord.ui import Button, View
from keep_alive import keep_alive
from discord.ext import commands
from asyncio import sleep
import json
#import asyncio
#from discord import RawReactionActionEvent
from discord.utils import get

bot = commands.Bot(command_prefix=commands.when_mentioned_or('&'),intents=discord.Intents.all())
client= discord.Client(command_prefix=commands.when_mentioned_or('&'),intents=discord.Intents.all())
#intents = discord.Intents.default()
#intents.members = True

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, name='&help'))
    print('bot is ready')



#prefix command
@bot.command()
async def prefix(ctx):
    await ctx.send(' **<:vf:947194381172084767>My prefix is  `&` ** ')


############################################################################################
#                                          JOIN/LEFT EVENTS
############################################################################################













############################################################################################
#                                          TEXT COMMANDS
############################################################################################


#say command
@bot.command()
async def say(ctx, *, msg):
    await ctx.channel.purge(limit=1)
    await ctx.send(msg)


#embed command
@bot.command()
async def emb(ctx, *, msg):
    embed = discord.Embed(description=msg, color=4 * 5555)
    await ctx.channel.purge(limit=1)
    await ctx.send(embed=embed)

#dm command
@bot.command()
@commands.has_permissions(administrator=True)
async def dm(ctx, users: commands.Greedy[discord.User], *, message):
    for user in users:
        await user.send(message,f'\nSent from{guild.name}')
@dm.error
async def info_error(ctx, error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send('**Please enter  Arguments \nExample :  `&dm @hunter hello bro` **')
  

#clear command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(
        f'**<:vf:947194381172084767> Successfully cleared {amount} messages**',
        delete_after=5)
  
@clear.error
async def info_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('**Please enter amount \nExample :  `&clear 10` **')



@bot.command()
@commands.has_permissions(manage_messages=True)
async def poll(ctx,emoji1,emoji2,emoji3=None,*,message):
    emb=discord.Embed(description=f"{message}", color = discord.Color.red)
    msg=await ctx.channel.send(embed=emb)
    await msg.add_reaction(emoji1,emoji2,emoji3=None)

#react command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def react(ctx,emoji,message_id):
  channel = ctx.channel
  msg = await channel.fetch_message(message_id)
  await msg.add_reaction(emoji)

############################################################################################
#                                          ROLE COMMANDS
############################################################################################


#create role
@bot.command(help="**Use this command to crate roles\nExample: &crole Family**"
             )
@commands.has_permissions(
    manage_roles=True
)  # Check if the user executing the command can manage roles
async def crole(ctx, *names):
    for name in names:
        guild = ctx.guild
        await guild.create_role(name=name)
        await ctx.send(
            f"**<:vf:947194381172084767> Role `{name}` has been created**")


#delet role
@bot.command()
@commands.has_permissions(manage_roles=True)
async def drole(ctx, *roles: discord.Role):
    for role in roles:
        await ctx.send(
            f'**<:vf:947194381172084767> Role {role.name} has been deleted**')
        await role.delete()
        await ctx.channel.purge(limit=2)


#role give
@bot.command(
    pass_context=True,
    help=
    "Use this command to give role to someone \n \n Example : &role @hunter @family "
)
@commands.has_permissions(administrator=True)
async def role(ctx, role: discord.Role, *users: discord.Member):
    for user in users:
        await user.add_roles(role)
        await ctx.send(
            f"<:vf:947194381172084767> {role.mention} has been given to {user.mention}"
        )


#role remove
@bot.command(
    pass_context=True,
    help=
    "Use this command to remove role from someone \n \n Example : &rrole @role @hunter "
)
@commands.has_permissions(administrator=True)
async def rrole(ctx, role: discord.Role, user: discord.Member):
    await user.remove_roles(role)
    await ctx.send(
        f"<:vf:947194381172084767> {role.mention} has been removed from {user.mention}"
    )


############################################################################################
#                                      REACTION ROLE
############################################################################################


@bot.event
async def on_raw_reaction_add(payload):

    if payload.member.bot:
        pass

    else:
        with open('reactrole.json') as react_file:
            data = json.load(react_file)
            for x in data:
                if x['emoji'] == payload.emoji.name:
                    role = discord.utils.get(bot.get_guild(
                        payload.guild_id).roles, id=x['role_id'])

                    await payload.member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):

    with open('reactrole.json') as react_file:
        data = json.load(react_file)
        for x in data:
            if x['emoji'] == payload.emoji.name:
                role = discord.utils.get(bot.get_guild(
                    payload.guild_id).roles, id=x['role_id'])

                
                await bot.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(role)
                    


@bot.command()
@commands.has_permissions(administrator=True, manage_roles=True)
async def rrc(ctx, emoji, role: discord.Role, *, message):

    emb = discord.Embed(description=message)
    msg = await ctx.channel.send(embed=emb)
    await msg.add_reaction(emoji)

    with open('reactrole.json') as json_file:
        data = json.load(json_file)

        new_react_role = {'role_name': role.name, 
        'role_id': role.id,
        'emoji': emoji,
        'message_id': msg.id}

        data.append(new_react_role)

    with open('reactrole.json', 'w') as f:
        json.dump(data, f, indent=4)




############################################################################################
#                                      CHANNEL COMMANDS
############################################################################################


#lock command
@bot.command(help=" Use this command to lock a channel")
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,
                                      send_messages=False)
    await ctx.send('**<:vf:947194381172084767> Channel has been locked**')
    await ctx.channel.purge(limit=2)


#unlock command
@bot.command(help=" Use this command to lock a channel")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,
                                      send_messages=True)
    await ctx.send('**<:vf:947194381172084767> Channel has been unlocked**')
    await ctx.channel.purge(limit=2)


#hide channel
@bot.command(help=" Use this command to hide a channel")
@commands.has_permissions(manage_channels=True)
async def hide(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,
                                      view_channel=False)
    await ctx.send(
        '**<:vf:947194381172084767>This channel is hidden from everyone**')
    await ctx.channel.purge(limit=2)


#unhide channel
@bot.command(help=" Use this command to unhide a channel")
@commands.has_permissions(manage_channels=True)
async def unhide(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,
                                      view_channel=True)
    await ctx.send(
        '**<:vf:947194381172084767>This channel is visible to everyone**')
    await ctx.channel.purge(limit=2)


#channel create
@bot.command(aliases=['chm'])
@commands.has_permissions(manage_channels=True)
async def chmake(ctx, *names):
    for name in names:
        await ctx.guild.create_text_channel(name)
        await ctx.send(f'**<:vf:947194381172084767>`{name}` has been created**'
                       )
        await sleep(1)


#channel delete
@bot.command(aliases=['chd'])
@commands.has_permissions(manage_channels=True)
async def chdel(ctx, *channels: discord.TextChannel):
    for ch in channels:
        await ch.delete()
        await ctx.send(
            f'**<:vf:947194381172084767>`{ch.name}` has been deleted**')
        await sleep(1)


############################################################################################
#                                       KICK / BAN / MUTE
############################################################################################


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
    await ctx.send(f'User {member.mention} has been kicked for {reason}')


########################################################################################
#                                       INFO
############################################################################################


#bot info
@bot.command(help="print the detsil of the bot")
async def about(ctx):
    button = Button(label="Support Server", url="https://discord.gg/aqGTGKVTfQ" ,style=discord.ButtonStyle.link)
    view = View()
    embed = discord.Embed(
        title=ctx.guild.name,
        description=
        "**My name is Hunter 87\nI was built by Hunter.\nNow I have limited features\nfind out more by typing `&help` **",
        color=discord.Color.blue())
    view.add_item(button)
    await ctx.send(embed=embed,view=view)

@bot.command()
async def ping(ctx):
    await ctx.send(f'**Current ping is {round(bot.latency*1000)} ms**')



#RUN BOT


  
keep_alive()
bot.run(os.environ['TOKEN'])
