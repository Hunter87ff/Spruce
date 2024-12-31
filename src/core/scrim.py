from discord.ext import commands
from discord.ext import tasks
import discord, re, pytz
from datetime import datetime
from modules import config
from modules.bot import Spruce
from ext.constants import TimeZone


class ScrimData:
    def __init__(self, data:dict, _bot:Spruce) -> None:
        self._data = data
        self._bot:Spruce = _bot
        self.guild_id:int = data.get("guild_id")
        self.slot:int = data.get("slot")
        self.time:str = data.get("time")
        self.zone:str = data.get("zone")
        self.status:str = data.get("status")
        self.started:bool = data.get("started")


    @property
    def channel(self) -> discord.TextChannel:
        """Returns the registration channel for the scrim"""
        return self._bot.get_channel(self._data.get("channel_id"))
    
    @property
    def role(self) -> discord.Role:
        """Returns the confirmation role for the registered teams"""
        return discord.utils.get(self.channel.guild.roles, id=self._data.get("role_id"))
    
    @property
    def reged(self) -> int:
        """Returns the number of registered teams"""
        return self._data.get("reged")
    
    def __str__(self) -> str:
        return f"ScrimData({self.guild_id}, {self.slot}, {self.time}, {self.zone}, {self.channel.id}, {self.role.id}, {self.status}, {self.started}, {self.reged})"
    
    def to_dict(self) -> dict:
        """Returns the data in dict format"""
        return self._data
    



class Scrim(commands.Cog):
    """Currently in development mode!!"""
    def __init__(self, bot) -> None:
        self.bot:Spruce = bot
        self.monitor_scrims.start()


    @discord.app_commands.command()
    @discord.app_commands.describe(
        total_slots="Total slots for the scrim min: 2, max: 100",
        time_zone="Timezone for the scrim",
        time="12H formated Time for the scrim eg: 10:00 AM",
        registration_channel="Channel where the registration message is sent",
        idp_role="Role for the registered teams"
    )
    async def scrim(
        self, 
        interaction:discord.Interaction, 
        total_slots:int, 
        time_zone:TimeZone, time:str,
        registration_channel:discord.TextChannel, 
        idp_role:discord.Role
    ):
        if not await config.is_dev(interaction): return

        # Check if the channel is already registered
        if self.bot.db.scrims.find_one({"channel_id": registration_channel.id}):
            return await interaction.response.send_message("Scrim already exists", ephemeral=True)
        try:
            if total_slots < 2 or total_slots > 100:
                return await interaction.response.send_message(
                    "Total slots should be between 2 and 100", 
                    ephemeral=True
                )
            _time = re.match(r"([0-9]{1,2}):([0-9]{1,2}) ([AP]M)", time)
            if not _time:
                return await interaction.response.send_message(
                    "Invalid time format!! Follow something like this 12h format : 10:00 AM", 
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
        _data = self.bot.db.scrims.find_one({"channel_id": channel.id})
        if not _data:
            return await ctx.send("No scrim found for this channel")
        _scrim_data = ScrimData(_data, self.bot)
        await self.team_struct(ctx.message, _scrim_data.role, _scrim_data.role)


    def create_scrim(
            self, 
            total_slots:int, 
            time:str, zone:str, 
            channel:discord.TextChannel,
            idp_role:discord.Role
        ):
        """Creates a scrim in the database"""
        _data = {
                "guild_id": channel.guild.id,
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
        current_mentions = set(ctx.mentions)
        messages = [message async for message in ctx.channel.history(limit=123)]  
        for fmsg in messages:
            previous_mentions = set(fmsg.mentions)
            if len(current_mentions.intersection(previous_mentions)) > 0:
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

    

    @tasks.loop(seconds=30)
    async def monitor_scrims(self):
        _time = datetime.now(pytz.timezone(TimeZone.Asia_Kolkata.value)).strftime("%H:%M:00")
        _test = self.bot.db.scrims.find_one({"status": "active", "started": False, "time" : _time})
        if _test:
            _scrim_data = ScrimData(_test, self.bot)
            _register_message = discord.Embed(
                title="Scrim Registration",
                description=f"React to this message to register your team for the scrim",
                color=0x00ff00
            )
            _register_message.set_thumbnail(url=_scrim_data.channel.guild.icon.url or self.bot.user.avatar.url)
            _registration_view = discord.ui.View()
            _registration_view.add_item(
                discord.ui.Button(
                    custom_id=f"{self.bot.user.id}-scrim-registration-button",
                    label="Register", 
                    style=discord.ButtonStyle.green
                )
            )
            await _scrim_data.channel.send(embed=_register_message, view=_registration_view)

        self.bot.db.scrims.update_many({"status": "active", "started":False, "time" : _time}, {"$set": {"started": True}})



async def setup(bot:commands.Bot):
 await bot.add_cog(Scrim(bot))