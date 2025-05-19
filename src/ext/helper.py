from discord import Message, Color, Embed, Interaction
from discord.ui import Button, View
from ext import Database
from discord.ext import commands



def get_db():
    """
    Returns a Database Object
    """
    return Database()


votes = []
async def vote_add(bot:commands.Bot):
    global votes
    vtl = bot.get_channel(votel)
    votes = [message async for message in vtl.history(limit=500)]


async def voted(ctx:commands.Context, bot:commands.Bot):
	return True


async def vote_check(message:Message):
    global votes
    if message.channel.id == message.guild.me:
        votes.append(message)


async def vtm(ctx:commands.Context):
	btn = Button(label="Vote Now", url=f"https://top.gg/bot/{ctx.me.id}/vote")
	await ctx.send(embed=Embed(color=Color.cyan, description="Vote Now To Unlock This Command"),view=View().add_item(btn))


async def is_dev(ctx: commands.Context | Interaction):
    """
    Checks if the user is a developer
    """
    user_id = ctx.user.id if isinstance(ctx, Interaction) else ctx.author.id
    if user_id not in get_db().cfdata["devs"]:
        response = ctx.response.send_message if isinstance(ctx, Interaction) else ctx.send
        await response("Command is under development", ephemeral=True if isinstance(ctx, Interaction) else False)
        return False
    return True
    