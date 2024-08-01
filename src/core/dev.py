import discord, typing, requests
from modules import config 
from discord.ext import commands
from typing import Any
# from discord import app_commands, Interaction
cmd = commands
import psutil

class dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cmd.command(hidden=True)
    @config.dev()
    async def system(self, ctx):
        if ctx.author.bot:return
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        detail = f"""Total RAM : {memory.total / (1024**3):.2f} GB\nCPU Cores : {psutil.cpu_count(logical=False)+psutil.cpu_count(logical=True)}\nCPU Usage : {cpu_usage}%\nRAM Usage : {memory.used//10**6} MB({memory.percent}%)\nTotal Disk: {disk.total//10**9} GB\nDisk Usage: {disk.used//10**9} GB({disk.percent}%)
        """
        await ctx.send(embed=discord.Embed(title="System Information", description=detail, color=0x00ff00))
        
    @cmd.command(hidden=True)
    @commands.guild_only()
    @config.dev()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def leaveg(self, ctx, member:int, guild_id:int=None):
        if ctx.author.bot:
            return
        if ctx.author.id != config.owner_id:
            return
        if not guild_id:
            for guild in self.bot.guilds:
                if guild.member_count < member:
                    gname = guild.name
                    await guild.leave()
                    await ctx.send(f"Leaved From {gname}, Members: {guild.member_count}")
        if guild_id:
            try:
                gld = self.bot.get_guild(guild_id)
            except:
                return
            if gld:
                await gld.leave()
                await ctx.send(f"Leaved From {gld.name}, Members: {gld.member_count}")

    @cmd.command(aliases=["dbu"])
    @config.dev()
    async def dbupdate(self, ctx, key:str, *, value:Any):
        if ctx.author.bot:return
        try:
            config.cfdbc.update_one({"config_id": 87}, {"$set":{key:value}})
            await ctx.send(f"Updated {key} to {value}")
        except Exception as e:
            await ctx.reply(e)
        

    @cmd.command()
    @config.dev()
    async def get_guild(self, ctx:commands.Context, id:discord.Guild):
        if ctx.author.bot: return
        await ctx.defer()
        guild = id #self.bot.get_guild(id)
        if  guild:
            try:
                invites = await [channel for channel in guild.channels][0].create_invite(reason=None, max_age=360, max_uses=2, temporary=True, unique=False, target_type=None, target_user=None, target_application_id=None)
                return await ctx.send(invites)
            except: return await ctx.send(f"i dont have permission to get links in {guild.name}")
        else: return await ctx.send("guild not found")						  


    @cmd.hybrid_command(with_app_command=True)
    @commands.guild_only()
    @config.dev()
    async def dlm(self, ctx, msg:discord.Message):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        try:
            await msg.delete()
            return await ctx.send("deleted", delete_after=2)
        except:return await ctx.send("Not Possible")

    @cmd.hybrid_command(with_app_command = True, hidden=True)
    @config.dev()
    @commands.dm_only()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def cdm(self, ctx,amount:int):
        await ctx.defer(ephemeral=True)
        dmchannel = await ctx.author.create_dm()
        async for message in dmchannel.history(limit=amount):
            if message.author == self.bot.user:
                await message.delete()
        return await ctx.send("deleted", delete_after=3)


    @cmd.hybrid_command(with_app_command = True, hidden=True)
    @commands.is_owner()
    @config.dev()
    async def edm(self, ctx, msg:discord.Message, *, content):
        if ctx.author.bot: return
        await ctx.defer(ephemeral=True)
        if msg.author.id == self.bot.user.id:
            await msg.edit(content=content)
            await ctx.send('done')
        else:return await ctx.send("i didn't sent")
        

    @cmd.command(hidden=True)
    @cmd.guild_only()
    @config.dev()
    @cmd.cooldown(2, 20, commands.BucketType.user)
    async def sdm(self, ctx, member: discord.User, *, message):
        if ctx.author.id == config.owner_id:
            erl  = self.bot.get_channel(config.erl)
            try:
                await member.send(message)
                return await ctx.reply("Done")
            except Exception as e:
                return await erl.send(e)
        if ctx.author.id != config.owner_id:
            return await ctx.send(embed=discord.Embed(description="Command not found! please check the spelling carefully", color=0xff0000))

    @cmd.command()
    @commands.guild_only()
    @config.dev()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def owners(self, ctx):
        ms = await ctx.send(f"{config.loading} Processing...")
        ofcg = self.bot.get_guild(config.support_server_id)
        owner_role = ofcg.get_role(1043134410029019176)
        
        for i in self.bot.guilds:
            if i.owner in ofcg.members:
                if i.member_count > 1000:
                    onr = ofcg.get_member(i.owner.id)
                    await onr.add_roles(owner_role)
        return await ms.edit(content="Done")






async def setup(bot):
	await bot.add_cog(dev(bot))
