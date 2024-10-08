"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 souravyt87@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
 """

import discord
from modules import config, payment
from discord.ext import commands
from typing import Any
import psutil, enum

class Plans(enum.Enum):
    Monthly = 49
    Quarterly = 139
    HalfYearly = 229
    Yearly = 429
    Lifetime = 4444
    Custom = 0
    

class dev(commands.Cog):
    def __init__(self, bot):
        self.bot:commands.Bot = bot


    @discord.app_commands.command(description="Use coupon code SP10 to get 10% Discount.")
    @config.dev()
    async def getprime(self, interaction:discord.Interaction, plan:Plans):
        ctx = interaction
        if ctx.user.bot:return
        amount = plan.value if (interaction.user.id != config.owner_id) else 1
        url:str = f"{config.BASE_URL}/payment/prime?session="
        if plan != Plans.Custom:
            url += payment.create_order(customer_id=ctx.guild.id, customer_name=str(ctx.user.display_name.replace("_", "").replace(".","")), amount=amount).payment_session_id
        if plan == Plans.Custom:
            url = config.support_server
        button:discord.ui.Button = discord.ui.Button(label="Get Prime", url=url)
        await interaction.response.send_message(embed=discord.Embed(title="Get Prime", description="Click the button to get prime", color=0x00ff00),view=discord.ui.View().add_item(button))

    @commands.command(hidden=True)
    @config.dev()
    async def system(self, ctx:commands.Context):
        if ctx.author.bot:return
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        detail = f"""Total RAM : {memory.total / (1024**3):.2f} GB\nCPU Cores : {psutil.cpu_count(logical=False)+psutil.cpu_count(logical=True)}\nCPU Usage : {cpu_usage}%\nRAM Usage : {memory.used//10**6} MB({memory.percent}%)\nTotal Disk: {disk.total//10**9} GB\nDisk Usage: {disk.used//10**9} GB({disk.percent}%)
        """
        await ctx.send(embed=discord.Embed(title="System Information", description=detail, color=0x00ff00))
        
    @commands.command(hidden=True)
    @commands.guild_only()
    @config.dev()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def leaveg(self, ctx:commands.Context, member:int, guild_id:int=None):
        if ctx.author.bot:return
        if ctx.author.id != config.owner_id:return
        if not guild_id:
            for guild in self.bot.guilds:
                if guild.member_count < member:
                    gname = guild.name
                    await guild.leave()
                    await ctx.send(f"Leaved From {gname}, Members: {guild.member_count}")
        if guild_id:
            try:gld = self.bot.get_guild(guild_id)
            except Exception:return None
            if gld:
                await gld.leave()
                await ctx.send(f"Leaved From {gld.name}, Members: {gld.member_count}")

    @commands.command(aliases=["dbu"])
    @config.dev()
    async def dbupdate(self, ctx:commands.Context, key:str, *, value:Any):
        if ctx.author.bot:return
        try:
            config.cfdbc.update_one({"config_id": 87}, {"$set":{key:value}})
            await ctx.send(f"Updated {key} to {value}")
        except Exception as e:await ctx.reply(e)
        

    @commands.command()
    @config.dev()
    async def get_guild(self, ctx:commands.Context, guild:discord.Guild):
        if ctx.author.bot: return
        await ctx.defer()
        if  guild:
            try:
                invites = await [channel for channel in guild.channels][0].create_invite(reason=None, max_age=360, max_uses=2, temporary=True, unique=False, target_type=None, target_user=None, target_application_id=None)
                return await ctx.send(invites)
            except Exception: return await ctx.send(f"i dont have permission to get links in {guild.name}")
        else: return await ctx.send("guild not found")						  


    @commands.hybrid_command(with_app_command=True)
    @commands.guild_only()
    @config.dev()
    async def dlm(self, ctx:commands.Context, msg:discord.Message):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        try:
            await msg.delete()
            return await ctx.send("deleted", delete_after=2)
        except Exception:return await ctx.send("Not Possible")

    @commands.hybrid_command(with_app_command = True, hidden=True)
    @config.dev()
    @commands.dm_only()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def cdm(self, ctx:commands.Context,amount:int):
        await ctx.defer(ephemeral=True)
        dmchannel = await ctx.author.create_dm()
        async for message in dmchannel.history(limit=amount):
            if message.author == self.bot.user:await message.delete()
        return await ctx.send("deleted", delete_after=3)


    @commands.hybrid_command(with_app_command = True, hidden=True)
    @commands.is_owner()
    @config.dev()
    async def edm(self, ctx:commands.Context, msg:discord.Message, *, content):
        if ctx.author.bot: return
        await ctx.defer(ephemeral=True)
        if msg.author.id == self.bot.user.id:
            await msg.edit(content=content)
            await ctx.send('done')
        else:return await ctx.send("i didn't sent")
        

    @commands.command(hidden=True)
    @commands.guild_only()
    @config.dev()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def sdm(self, ctx:commands.Context, member: discord.User, *, message):
        if ctx.author.id == config.owner_id:
            erl  = self.bot.get_channel(config.erl)
            try:
                await member.send(message)
                return await ctx.reply("Done")
            except Exception as e:return await erl.send(e)
        if ctx.author.id != config.owner_id:
            return await ctx.send(embed=discord.Embed(description="Command not found! please check the spelling carefully", color=0xff0000))

    @commands.command()
    @commands.guild_only()
    @config.dev()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def owners(self, ctx:commands.Context):
        ms = await ctx.send(f"{config.loading} Processing...")
        ofcg = self.bot.get_guild(config.support_server_id)
        owner_role = ofcg.get_role(1043134410029019176)
        
        for i in self.bot.guilds:
            if i.owner in ofcg.members and i.member_count > 1000:
                    onr = ofcg.get_member(i.owner.id)
                    await onr.add_roles(owner_role)
        return await ms.edit(content="Done")
    

    @commands.command()
    @commands.guild_only()
    async def add_dev(self, ctx:commands.Context, member:discord.Member):
        if ctx.author.bot or ctx.author.id != config.owner_id:return await ctx.send("You are not allowed to use this command")
        if member.id not in config.devs:
            config.devs.add(member.id)
            await ctx.send(f"Added {member.name} to devs")
        else:
            config.devs.remove(member.id)
            await ctx.send(f"Removed {member.name} from devs")






async def setup(bot):
	await bot.add_cog(dev(bot))
