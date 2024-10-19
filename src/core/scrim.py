from discord.ext import commands
from discord.ext import tasks
import discord, re, pytz, json
from datetime import datetime
from enum import Enum

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
    def __init__(self, bot) -> None:
        self.bot:commands.Bot = bot
        self.monitor_scrims.start()

    def create_scrim(self, total_slots:int, time:str, zone:str):
        try:
            with open("scrim.json", "r") as f:
                data:list = json.load(f)
                data.append({
                    "total_slots": total_slots,
                    "time": time,
                    "zone": zone
                })
        except FileNotFoundError:
            data = [{
                "total_slots": total_slots,
                "time": time,
                "zone": zone
            }]
        with open("scrim.json", "w") as f:
            json.dump(data, f, indent=4)
        return data


    @discord.app_commands.command()
    async def scrim(self, interaction:discord.Interaction, total_slots:int, time:str, time_zone:TimeZone):
        self.create_scrim(total_slots, self.convert_time(self.to24h(time)), time_zone.value)
        await interaction.response.send_message("Scrim created successfully")


    def to24h(time:str) -> str:
        if time[-2:] == "AM":return time[:-2]
        else:
            time = time[:-2]
            time = time.split(":")
            if int(time[0]) >= 11: return ":".join(time)
            else: return str(int(time[0]) + 12) + ":" + time[1]


    def convert_time(time: str, fr: str = "Asia/Tokyo", to: str = "Asia/Kolkata"):
        from_zone = pytz.timezone(fr)
        naive_time = datetime.strptime(time, "%H:%M").time() 
        combined_time = datetime.combine(datetime.now(from_zone).date(), naive_time)
        localized_time = from_zone.localize(combined_time)
        to_zone = pytz.timezone(to)
        converted_time = localized_time.astimezone(to_zone)
        return converted_time


    def time_format(self, delta):
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


    async def ft_ch(self, message:discord.Message):
        ctx = message
        messages = [message async for message in ctx.channel.history(limit=123)]  
        for fmsg in messages:
            if fmsg.author.id != ctx.author.id:
                for mnt in fmsg.mentions:
                    if mnt not in message.mentions:
                        return None
                    if mnt in message.mentions:
                        return mnt
                    

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
        em.set_footer(text=f"Time Taken : {self.time_format(time_taken)}")
        mes = await msg.channel.send(embed=em)
        await mes.add_reaction("✅")

 
    async def team_reg(self, message:discord.Message):
        msg = message
        tmrole = discord.utils.get(msg.guild.roles, name="scrim-mod") 
        if tmrole in msg.author.roles:
            return
        elif message.author.bot or message.author == self.bot.user:
            return
        elif message.channel.id != 1167331222494646302:  
            return
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
    

    @commands.command()
    async def slotlist(self, ctx:commands.Context, channel:discord.TextChannel):
        message = [ms async for ms in channel.history(limit=2)][0]
        crole = message.guild.get_role(1167424093574930432)
        tmrole = discord.utils.get(channel.guild.roles, name="scrim-mod")
        ms = await ctx.send("Processing")
        await self.team_struct(message, crole, tmrole)
        await ms.edit(content="Done")



    @tasks.loop(seconds=60)
    async def monitor_scrims(self):
        pass


async def setup(bot:commands.Bot):
    await bot.add_cog(Scrim(bot))