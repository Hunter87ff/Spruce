from discord.ext import commands
from discord.ext import tasks
import discord, re, pytz, json
from datetime import datetime
from modules import config
from modules.bot import Spruce
from enum import Enum
import numpy as np


class TimeZone(Enum):
    Asia_Kolkata = "Asia/Kolkata"
    Asia_Tokyo = "Asia/Tokyo"
    Asia_Shanghai = "Asia/Shanghai"
    Asia_Singapore = "Asia/Singapore"
    Asia_Dubai = "Asia/Dubai"
    Asia_Bangkok = "Asia/Bangkok"
    Asia_Hong_Kong = "Asia/Hong_Kong"
    Asia_Bangladesh = "Asia/Dhaka"
    Asia_Nepal = "Asia/Kathmandu"



class Scrim(commands.Cog):
    """Currently in development mode!!"""
    def __init__(self, bot) -> None:
        self.bot:Spruce = bot
        self.monitor_scrims.start()


    @discord.app_commands.command()
    async def scrim(
        self, 
        interaction:discord.Interaction, 
        total_slots:int, 
        time_zone:TimeZone, time:str,
        registration_channel:discord.TextChannel, 
        idp_role:discord.Role
    ):
        if await config.is_dev(interaction) == False: return

        if self.bot.db.scrims.find_one({"channel_id": registration_channel.id}):
            return await interaction.response.send_message("Scrim already exists", ephemeral=True)
        try:
            _time = re.match(r"([0-9]{1,2}):([0-9]{1,2}) ([AP]M)", time)
            if not _time:
                return await interaction.response.send_message(
                    "Invalid time format!! Follow something like this : 10:00 AM", 
                    ephemeral=True
                )
            _time = datetime.strptime(time, "%I:%M %p").time().strftime("%H:%M")
        except Exception:
            return await interaction.response.send_message(
                "Invalid time format!! Follow something like this : 10:00 AM", 
                ephemeral=True
            )
        self.create_scrim(
            total_slots, 
            Scrim.convert_time(
                time=str(_time), 
                fr=time_zone.value, 
                to=TimeZone.Asia_Kolkata.value
            ), 
            time_zone.value,
            registration_channel,
            idp_role
        )
        await interaction.response.send_message("Scrim created successfully")


    @commands.hybrid_command()
    async def slotlist(self, ctx:commands.Context, channel:discord.TextChannel):
        if await config.is_dev(ctx) == False: return
        message = [ms async for ms in channel.history(limit=2)][0]
        crole = message.guild.get_role(1167424093574930432)
        tmrole = discord.utils.get(channel.guild.roles, name="scrim-mod")
        ms = await ctx.send("Processing")
        await self.team_struct(message, crole, tmrole)
        await ms.edit(content="Done")


    def create_scrim(
            self, 
            total_slots:int, 
            time:str, zone:str, 
            channel:discord.TextChannel,
            idp_role:discord.Role
        ):
        """Creates a scrim in the database"""
        _data = {
                "slot": total_slots,
                "time": time,
                "zone": zone,
                "channel_id": channel.id,
                "role_id": idp_role.id,
                "status": "active",
                "started" : False,
                "reged" : 0 # Number of registered teams
            }
        self.bot.db.scrims.insert_one(_data)


    @staticmethod
    def convert_time(time: str, fr: str = TimeZone.Asia_Kolkata.value, to: str = TimeZone.Asia_Kolkata.value):
        from_zone = pytz.timezone(fr)
        naive_time = datetime.strptime(time, "%H:%M").time() 
        combined_time = datetime.combine(datetime.now(from_zone).date(), naive_time)
        localized_time = from_zone.localize(combined_time)
        to_zone = pytz.timezone(to)
        converted_time = localized_time.astimezone(to_zone).time()
        return str(converted_time)


    @staticmethod
    def time_format(delta):
        delta = str(delta)
        time = ""
        lst = delta.split(".")[0].split(":")
        if(len(lst)<=3):
            h,m,s = delta.split(".")[0].split(":")
            time = f"{h}hr, {m}min, {s}sec"
        elif(len(lst)>3):
            d,h,m,s = delta.split(".")[0].split(":")
            time = f"{d}day, {h}hr, {m}min, {s}sec"
        return time


    def find_team(self, message:discord.Message):
        content = message.content.lower()
        teamname = re.search(r"team.*", content)
        if teamname is None:
            return f"{message.author}'s team"
        teamname = re.sub(r"<@*#*!*&*\d+>|team|name|[^\w\s]", "", teamname.group()).strip()
        teamname = f"{teamname.title()}" if teamname else f"{message.author}'s team"
        return teamname


    async def ft_ch(self, message:discord.Message) -> discord.Member|None:
        ctx = message
        current_mentions = np.array(ctx.mentions)
        messages = [message async for message in ctx.channel.history(limit=123)]  
        for fmsg in messages:
            previous_mentions = set(fmsg.mentions)
            if len(np.intersect1d(current_mentions, previous_mentions)) > 0:
                return fmsg.author
        return None
                    

    async def team_struct(self, msg:discord.Message, crole:discord.Role, tmrole):
        msgs = [ms async for ms in msg.channel.history(limit=200)][::-1]
        teams = "```"
        tms = 1
        for ms in msgs:
            if tmrole not in ms.author.roles or not ms.author.bot:
                tm = self.find_team(ms)
                teams += f"{tms}) {tm} : {ms.author}\n"
                tms += 1
        teams += "```"
        time_taken = msgs[-1].created_at - msgs[0].created_at
        em = discord.Embed(title="Team List", description=teams, color=0x00ff00)
        em.set_footer(text=f"Time Taken : {Scrim.time_format(time_taken)}")
        mes = await msg.channel.send(embed=em)
        await mes.add_reaction("✅")

 
    async def team_reg(self, message:discord.Message):
        msg = message
        tmrole = discord.utils.get(msg.guild.roles, name="scrim-mod") 
        if message.author.bot or message.author == self.bot.user or tmrole in msg.author.roles or message.channel.id != 1167331222494646302:
            return None
        req_men = 2
        tslot = 12
        crole = message.guild.get_role(1167424093574930432) 
        ment = message.mentions
        if not ment or len(ment) < req_men:
            await message.reply(f"You must mention `{req_men}` or more members to register a team.", delete_after=5)
            return await msg.delete()
            
        ft = await self.ft_ch(message) 
        if ft != None:
            return await message.reply(f"You've mentioned `{ft}` who is already in a team.")
        else:
            await message.author.add_roles(crole)
            await message.add_reaction("✅")
            if len(crole.members) == tslot:
                await msg.channel.send("Registration closed")
                return await self.team_struct(message, crole, tmrole)
    

    @tasks.loop(seconds=30)
    async def monitor_scrims(self):
        _time = datetime.now(pytz.timezone(TimeZone.Asia_Kolkata.value)).strftime("%H:%M:00")
        _test = self.bot.db.scrims.find_one({"status": "active", "started": False, "time" : _time})
        if _test:
            print(_test)
        self.bot.db.scrims.update_many({"status": "active", "started":False, "time" : _time}, {"$set": {"started": True}})



async def setup(bot:commands.Bot):
 await bot.add_cog(Scrim(bot))