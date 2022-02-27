import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
client = discord.Client



@bot.command()
async def hlo(ctx):
    await ctx.send("hello")