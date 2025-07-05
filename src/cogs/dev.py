"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022-present hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
 """

import discord, os
from modules import config, payment
from discord.ext import commands
from ext import checks
from ext.models import Tester
from typing import Any, TYPE_CHECKING
import psutil, enum


if TYPE_CHECKING:
    from modules.bot import Spruce

class Plans(enum.Enum):
    Monthly = 49
    Quarterly = 139
    HalfYearly = 229
    Yearly = 429
    Lifetime = 4444
    Custom = 0

class CogEnum(enum.Enum):
    music = "music"
    moderation = "moderation"
    utility = "utility"


class DevCog(commands.Cog):
    """
    ## DevCog Class
    This class contains commands for developers and admins to manage the bot and its features.
    It includes commands for system information, managing guilds, and handling messages.
    """

    def __init__(self, bot):
        self.bot:'Spruce' = bot


    @discord.app_commands.command(description="Use coupon code SP10 to get Discount.")
    @checks.dev_only()
    async def getprime(self, ctx:discord.Interaction, plan:Plans):
        await ctx.response.defer()
        amount = plan.value if (ctx.user.id != config.OWNER_ID) else 1
        url:str = f"{config.BASE_URL}/extras/pg.html?session="
        if plan != Plans.Custom:
            url += payment.create_order(
                customer_id=ctx.guild.id, 
                customer_name=str(ctx.user.display_name.replace("_", "").replace(".","")), 
                amount=amount
            ).payment_session_id
        if plan == Plans.Custom:
            url = config.SUPPORT_SERVER
        button:discord.ui.Button = discord.ui.Button(label="Get Prime", url=url)
        await ctx.followup.send(
            embed=discord.Embed(
                title="Get Prime", 
                description="Click the button to get prime", 
                color=0x00ff00
                ),
            view=discord.ui.View().add_item(button))
        

    @commands.command(hidden=True)
    @checks.dev_only()
    async def add_tester(self, ctx:commands.Context, member:discord.Member, guild:discord.Guild=None):
        """
        Add a user to the tester list.
        """
        if ctx.author.bot:return
        if member not in self.bot.config.TESTERS:
            _tester = Tester(id=member.id, name=str(member),  guild=guild.id if guild else None,  level=0.0,  active=True  )
            await _tester.save(self.bot)
            self.bot.config.TESTERS.append(_tester)
            
            await ctx.send(f"Added {member.name} to testers")
        else:
            await ctx.send(f"{member.name} is already a tester")


    # remove tester
    @commands.command(hidden=True)
    @checks.dev_only()
    async def remove_tester(self, ctx:commands.Context, member:discord.Member):
        """
        Remove a user from the tester list.
        """
        if ctx.author.bot:return
        if member in self.bot.config.TESTERS:
            self.bot.config.TESTERS.remove(member)
            self.bot.db.testers.delete_one({"id": member.id})
            await ctx.send(f"Removed {member.name} from testers")
        else:
            await ctx.send(f"{member.name} is not a tester")



    @commands.command(hidden=True)
    @checks.dev_only()
    async def system(self, ctx:commands.Context):
        if ctx.author.bot:return
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        detail = f"""
Total RAM : {memory.total / (1024**3):.2f} GB\n
CPU Cores : P: {psutil.cpu_count(logical=False)}, L: {psutil.cpu_count(logical=True)}\n
CPU Usage : {cpu_usage}%\n
RAM Usage : {memory.used//10**6} MB({memory.percent}%)\n
Total Disk: {disk.total//10**9} GB\n
Disk Usage: {disk.used//10**9} GB({disk.percent}%)
        """
        await ctx.send(embed=discord.Embed(title="System Information", description=detail, color=0x00ff00))
        
    @commands.command(hidden=True)
    @commands.guild_only()
    @checks.dev_only()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def leaveg(self, ctx:commands.Context, member:int, guild_id:int=None):
        if ctx.author.bot:return
        if ctx.author.id != config.OWNER_ID:return
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

    @commands.command(aliases=["dbu"], hidden=True)
    @checks.dev_only()
    async def dbupdate(self, ctx:commands.Context, key:str, *, value:Any):
        if ctx.author.bot:return
        try:
            self.bot.db.config_col.update_one({"config_id": 87}, {"$set":{key:value}})
            await ctx.send(f"Updated {key} to {value}")
        except Exception as e:
            await ctx.reply(f"Error updating {key}: {e}")


    @commands.command(hidden=True)
    @checks.dev_only()
    async def get_guild(self, ctx:commands.Context, guild:discord.Guild):
        if ctx.author.bot: return
        await ctx.defer()
        if  guild:
            try:
                invites = await guild.channels[0].create_invite(reason=None, max_age=360, max_uses=2, temporary=True, unique=False, target_type=None, target_user=None, target_application_id=None)
                return await ctx.send(invites)
            except Exception: return await ctx.send(f"i dont have permission to get links in {guild.name}")
        else: return await ctx.send("guild not found")						  


    @commands.command(hidden=True)
    @commands.guild_only()
    @checks.dev_only()
    async def dlm(self, ctx:commands.Context, msg:discord.Message):
        if ctx.author.bot:return
        try:
            await msg.delete()
            return await ctx.send("deleted", delete_after=2)
        except Exception:return await ctx.send("Not Possible")

    @commands.command(hidden=True)
    @checks.dev_only()
    @commands.dm_only()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def cdm(self, ctx:commands.Context,amount:int):
        dmchannel = await ctx.author.create_dm()
        async for message in dmchannel.history(limit=amount):
            if message.author == self.bot.user:await message.delete()
        return await ctx.send("deleted", delete_after=3)


    @commands.command(hidden=True)
    @commands.is_owner()
    @checks.dev_only()
    async def edm(self, ctx:commands.Context, msg:discord.Message, *, content):
        """
        Edit a message sent by the bot.
        """
        if ctx.author.bot: return
        if msg.author.id == self.bot.user.id:
            await msg.edit(content=content)
            await ctx.send('done')
        else:return await ctx.send("i didn't sent")
        

    @commands.command(hidden=True)
    @commands.guild_only()
    @checks.dev_only()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def sdm(self, ctx:commands.Context, member: discord.User, *, message):
        """
        Send a direct message to a user.
        This command can only be used by the bot owner.
        """
        if ctx.author.id == config.OWNER_ID:
            try:
                await member.send(message)
                return await ctx.reply("Done")
            
            except Exception as e:
                return await  self.bot.log_channel.send(e)
            
        if ctx.author.id != config.OWNER_ID:
            return await ctx.send(embed=discord.Embed(description="Command not found! please check the spelling carefully", color=0xff0000))



    @commands.command(hidden=True)
    @commands.guild_only()
    @checks.dev_only()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def owners(self, ctx:commands.Context):
        ms = await ctx.send(f"{config.loading} Processing...")
        ofcg = self.bot.get_guild(config.SUPPORT_SERVER_ID)
        owner_role = ofcg.get_role(1043134410029019176)
        
        for i in self.bot.guilds:
            if i.owner in ofcg.members and i.member_count > 1000:
                    onr = ofcg.get_member(i.owner.id)
                    await onr.add_roles(owner_role)
        return await ms.edit(content="Done")
    


    @commands.command(hidden=True)
    @commands.guild_only()
    @checks.dev_only()
    async def add_dev(self, ctx:commands.Context, member:discord.Member):
        if ctx.author.bot or ctx.author.id != config.OWNER_ID:
            return await ctx.send("You are not allowed to use this command")
        
        if member.id not in self.bot.config.DEVELOPERS:
            self.bot.config.DEVELOPERS.append(member.id)
            await ctx.send(f"Added {member.name} to devs")
            self.bot.logger.info(f"Added {member.name} to developers")

        else:
            self.bot.config.DEVELOPERS.remove(member.id)
            await ctx.send(f"Removed {member.name} from devs")



    @commands.command(hidden=True)
    @commands.guild_only()
    @checks.dev_only()
    async def get_log(self, ctx:commands.Context):
        if ctx.author.bot:return

        if not os.path.exists("error.log"):
            return await ctx.send("No error log found.")
        
        await ctx.send(file=discord.File("error.log"))


    @discord.app_commands.command(name="load_cog", description="(Dev only): Load a cog by name")
    @checks.dev_only(interaction=True)
    @discord.app_commands.describe(cog_name="Name of the cog to load")
    async def load_cog(self, ctx: discord.Interaction, cog_name: CogEnum):
        if ctx.user.bot or ctx.user.id not in self.bot.config.DEVELOPERS:
            return await ctx.response.send_message("You are not allowed to use this command.", ephemeral=True)
        
        try:
            await self.bot.load_extension(f"cogs.{cog_name.value}")
            await ctx.response.send_message(f"Cog `{cog_name.value}` loaded successfully.", ephemeral=True)

        except Exception as e:
            await ctx.response.send_message(f"Failed to load cog `{cog_name.value}`: {e}", ephemeral=True)