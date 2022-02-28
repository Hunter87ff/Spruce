import discord
import  os
import aiohttp
import datetime
import warnings
from keep_alive import keep_alive
from discord.ext import commands



intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or('&'),
                   intents=intents, help_command=None)
client = discord.Client


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, name='&help'))
    print('im online')

#custom help
class Nhelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emb = discord.Embed(title="Commands",
                                description=page,
                                color=3 * 679319)
            await destination.send(embed=emb)


bot.help_command = Nhelp(no_category='Moderation')


#prefix command
@bot.command()
async def prefix(ctx):
    await ctx.send(' **<:vf:947194381172084767>My prefix is `&` ** ')

    
@bot.command()
async def info(ctx, *, member: discord.Member):
    """Tells you some info about the member."""
    fmt = '{0} joined on {0.joined_at} and has {1} roles.'
    await ctx.send(fmt.format(member, len(member.roles)))

@info.error
async def info_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('I could not find that member...')


  
#welcome message
@bot.event
async def on_member_join(member):
  guild = member.guild
  
  channel = bot.get_channel(943095689834029086)
  embed = discord.Embed(title="", description=f"**<a:namaste:947518755016159253> WELCOME TO {guild.name} <a:namaste:947518755016159253>\n━━━━━━━━━━━━━━━━━━━━━━\n<a:hg_heart:947518930916876288>Don't forget to read <#943091951119507466> \n<a:hg_heart:947518930916876288>Take self roles from <#943091952692387840> \n<a:hg_heart:947518930916876288>Talk with friends <#943091939186712606>\n━━━━━━━━━━━━━━━━━━━━━━\n<a:atom:947518612195934248> STAY WITH US | DON'T LEAVE <a:atom:947518612195934248> **", color=5*52342)
  embed.set_image(url="https://images-ext-2.discordapp.net/external/cGrcX-q2Fwotcb1ora1IcMHabHEXo-XEU-bQ2jqbTJ8/https/raw.githubusercontent.com/Hunter87ff/hgo/main/assets/images/discord/HG%2520OFFICIAL.gif")
  await channel.send(member.mention , embed=embed)
  await member.send(embed=embed)
    

#say command
@bot.command()
async def say(ctx, messages):
    await ctx.send(messages)

#role give
@bot.command(pass_context=True)
async def role(ctx, role: discord.Role , user: discord.Member):
    await user.add_roles(role)
    await ctx.send(f"<:vf:947194381172084767> {role.mention} has been given to {user.mention}")


#role remove
@bot.command(pass_context=True)
async def rrole(ctx, role: discord.Role , user: discord.Member):
    await user.remove_roles(role)
    await ctx.send(f"<:vf:947194381172084767> {role.mention} has been removed from {user.mention}")

  
#lock command
@bot.command()
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,
                                      send_messages=False)
    await ctx.send('**<:vf:947194381172084767> Channel has beenlocked'**')


#Unlock command
@bot.command()
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,
                                      send_messages=True)
    await ctx.send('**<:vf:947194381172084767>Channel has been Unlocked**')


#hide channel
@bot.command()
async def hide(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,
                                      view_channel=False)
    await ctx.send('**<:vf:947194381172084767>This channel is hidden from everyone**')


#unhide channel
@bot.command()
async def unhide(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,
                                      view_channel=True)
    await ctx.send('**<:vf:947194381172084767>This channel is visible to everyone**')

  
#kick command
@bot.command()
async def kick(ctx, member: discord.Member,*, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'**<:vf:947194381172084767>User {member} has kicked . reason of**')


#ban command
@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'<:vf:947194381172084767>User {member} has banned')


#create role
@bot.command()
async def crole(ctx, *, name):
    guild = ctx.guild
    await guild.create_role(name=name)
    await ctx.send(f'**<:vf:947194381172084767>Role `{name}` has been created**')


#message clear
@bot.command()
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'**<:vf:947194381172084767>Succesfully cleared  `{amount}` message**')

my_secret = os.environ['TOKEN']
keep_alive()
bot.run(my_secret)
