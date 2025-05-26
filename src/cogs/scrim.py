import re, pytz
from datetime import datetime
from typing import TYPE_CHECKING
from ext import permissions, constants
from discord.ext import commands, tasks
from ext.models.scrim import ScrimModel
from discord import Embed, Message, Member, Interaction,  app_commands as app




if TYPE_CHECKING:
    from modules.bot import Spruce    



class ScrimCog(commands.GroupCog, name="scrim", group_name="scrim", command_attrs={"help": "Manage scrims for the server."}):
    """Currently in development mode!!"""
    def __init__(self, bot:"Spruce") -> None:
        self.bot = bot
        self.monitor_scrims.start()
        self.DEFAULT_START_TIME = "10:00 AM"
        self.DEFAULT_END_TIME = "4:00 PM"
        self.DEFAULT_TIMEZONE = constants.TimeZone.Asia_Kolkata.value
        self.DEFAULT_START_MESSAGE = "Scrim has started! Please register your team in this channel."
        self.DEFAULT_END_MESSAGE = "Scrim has ended! Thank you for participating."


    @app.command(name="create", description="Create a scrim for the server.")
    @app.guild_only()
    @app.describe(
        scrim_name="Name of the scrim",
        total_slots="Total number of slots for the scrim (default: 12)",
        scrim_start_time="scrim start time in HH:MM AM/PM format (default: 10:00 AM)",
        scrim_end_time="scrim end time in HH:MM AM/PM format (default: 4:00 PM)",
        timezone="Timezone of the scrim (default: Asia/Kolkata)",
    )
    @permissions.tourney_mod()
    @commands.bot_has_guild_permissions(embed_links=True, manage_messages=True, read_message_history=True)
    async def create_scrim(
        self, 
        ctx:Interaction, 
        scrim_name:str, 
        timezone:constants.TimeZone=constants.TimeZone.Asia_Kolkata,
        total_slots:int=12, 
        scrim_start_time:str="10:00 AM",
        scrim_end_time:str="4:00 PM",
        ):
        """Create a new scrim"""
        _parsed_start_time = self.bot.helper.time_parser(
            time=scrim_start_time,
            from_tz=timezone.value, 
            to_tz=constants.TimeZone.Asia_Kolkata.value
        )
        _parsed_end_time = self.bot.helper.time_parser(
            time=scrim_end_time, 
            from_tz=timezone.value, 
            to_tz=constants.TimeZone.Asia_Kolkata.value
        )
        print(f"TimeZone: {timezone.value}\nTime: Start: {scrim_start_time}, End: {scrim_end_time}\nParsed: {_parsed_start_time} to {_parsed_end_time} in {timezone}")
        if _parsed_start_time is None or _parsed_end_time is None:
            return await ctx.response.send_message("Invalid time format. Please use HH:MM AM/PM format.", ephemeral=True)

        _event_prefix = self.bot.helper.get_event_channel_prefix(scrim_name)
        _scrim_category = await ctx.guild.create_category(name=str(scrim_name))
        _self_override = _scrim_category.overwrites_for(ctx.guild.me)
        _self_override.update(
            send_messages=True, 
            manage_messages=True, 
            read_message_history=True, 
            add_reactions=True, 
            manage_channels=True, 
            external_emojis=True, 
            view_channel=True
        )
        await _scrim_category.set_permissions(ctx.guild.me, overwrite=_self_override)
        _registration_channel = await ctx.guild.create_text_channel(f"{_event_prefix}register-here", category=_scrim_category)

        try:
            _scrim_obj = ScrimModel(
                status=False,
                guild_id=ctx.guild.id,
                registration_channel=_registration_channel.id,
                start_time=_parsed_start_time,
                end_time=_parsed_end_time,
                total_slots=total_slots,
                time_zone=timezone,
                start_message=self.DEFAULT_START_MESSAGE,
                end_message=self.DEFAULT_END_MESSAGE,
            )
            _scrim_obj.save()
            _embed = Embed(
                title=f"Scrim Created: {scrim_name}",
                description=f"Scrim has been created successfully! \n\n**Start Time:** {_parsed_start_time.strftime('%I:%M %p')} \n**End Time:** {_parsed_end_time.strftime('%I:%M %p')} \n**Total Slots:** {total_slots} \n**Timezone:** {timezone}",
                color=self.bot.color.green
            )
            _embed.set_footer(text=f"Scrim ID: {_scrim_obj.registration_channel}")
            await ctx.response.send_message(embed=_embed, ephemeral=True)

            await _registration_channel.send(embed=Embed(
                description=f"Scrim will start at {scrim_start_time}",
                color=self.bot.color.random()
            ))
        except ValueError as e:
            return await ctx.response.send_message(f"Error creating scrim: {str(e)}", ephemeral=True)



    def find_team(self, message:Message):
        content = message.content.lower()
        teamname = re.search(r"team.*", content)
        if teamname is None:
            return f"{message.author}'s team"
        teamname = re.sub(r"<@*#*!*&*\d+>|team|name|[^\w\s]", "", teamname.group()).strip()
        teamname = f"{teamname.title()}" if teamname else f"{message.author}'s team"
        return teamname


    async def ft_ch(self, message:Message) -> Member|None:
        ctx = message
        current_mentions = set(ctx.mentions)
        messages = [message async for message in ctx.channel.history(limit=123)]  
        for fmsg in messages:
            previous_mentions = set(fmsg.mentions)
            if len(current_mentions.intersection(previous_mentions)) > 0:
                return fmsg.author
        return None
                    

    

    @tasks.loop(seconds=30)
    async def monitor_scrims(self):
        _time = datetime.now(pytz.timezone(constants.TimeZone.Asia_Kolkata.value)).strftime("%H-%M")
        print(f"Checking scrims at {_time}")
