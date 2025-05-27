import discord
from enum import Enum
from typing import TYPE_CHECKING
from ext import permissions, constants
from discord.ext import commands, tasks
from ext.models.scrim import ScrimModel
from discord import Embed, TextChannel, utils, Interaction, Guild,  app_commands as app


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
        self.DEFAULT_END_MESSAGE = "Scrim has ended! Thank you for participating."
        self.SCRIM_LOG_CHANNEL_NAME = f"{bot.user.name.strip()}-scrim-log"



    def log_embed(self, message:str):
        embed = Embed(title="Scrim Log", description=message, color=self.bot.color.random())
        return embed



    def scrim_log(self, guild:Guild) -> TextChannel | None:
        """Get the scrim log channel for the guild."""
        return utils.get(guild.text_channels, name=self.SCRIM_LOG_CHANNEL_NAME)


    @app.command(name="create", description="Create a scrim for the server.")
    @app.guild_only()
    @permissions.under_maintenance()
    @app.describe(
        scrim_name="Name of the scrim",
        mentions="Number of mentions required to register a team (default: 4)",
        total_slots="Total number of slots for the scrim (default: 12)",
        scrim_start_time="examples: 10am, 10:00, 22:00, 7:00 PM (default: 10:00 AM)",
        scrim_end_time="examples: 10am, 10:00, 22:00, 7:00 PM (default: 4:00 PM)",
        timezone="Timezone of the scrim (default: Asia/Kolkata)",
        reg_channel="Registration channel for the scrim (default: create's new channel)",
        slot_channel="Slot channel for the scrim (default: registration channel)",
        ping_role="Role to ping when the scrim starts (optional)",
    )
    @commands.bot_has_guild_permissions(embed_links=True, manage_messages=True, read_message_history=True)
    async def create_scrim(
        self, 
        ctx:Interaction, 
        scrim_name:str, 
        total_slots:int=12, 
        scrim_start_time:str="10:00 AM",
        scrim_end_time:str="4:00 PM",
        timezone:constants.TimeZone=constants.TimeZone.Asia_Kolkata,
        mentions:int=4,
        idp_role:discord.Role | None = None,
        ping_role:discord.Role | None = None,
        reg_channel:TextChannel | None = None,
        slot_channel:TextChannel | None = None
        ):
        """Create a new scrim
        """

        await ctx.response.defer(ephemeral=True)


        _is_eligible = any([
            permissions.is_dev(ctx),
            ctx.user.guild_permissions.manage_guild,
            ctx.user.guild_permissions.administrator,
            discord.utils.get(ctx.guild.roles, name="tourney-mod")
        ])

        if not _is_eligible:
            await ctx.followup.send("You do not have permission to create a scrim.", ephemeral=True)
            return
        

        if total_slots < 1 or total_slots > 100:
            return await ctx.followup.send("Total slots must be between 1 and 100.", ephemeral=True)


        _parsed_start_time = self.bot.time.scrim_time_parse(
            time=scrim_start_time,
            from_tz=timezone.value, 
            to_tz=self.DEFAULT_TIMEZONE
        )
        _parsed_end_time = self.bot.time.scrim_time_parse(
            time=scrim_end_time, 
            from_tz=timezone.value, 
            to_tz=self.DEFAULT_TIMEZONE
        )

        if _parsed_start_time is None or _parsed_end_time is None:
            return await ctx.followup.send("Invalid time format. Please use HH:MM AM/PM format.", ephemeral=True)

        _event_prefix = self.bot.helper.get_event_prefix(scrim_name)
        _scrim_category: discord.CategoryChannel
        _registration_channel: TextChannel
        
        # if registration channel is provided, use it, otherwise create a new one
        # 
        if reg_channel:
            _registration_channel = reg_channel
            if _registration_channel.category is not None:
                _scrim_category = _registration_channel.category

        else:
            _scrim_category = await ctx.guild.create_category(name=str(scrim_name))
            _registration_channel = await _scrim_category.create_text_channel(name=f"{_event_prefix}register-here")


        _slot_channel = slot_channel or _registration_channel
        await _scrim_category.set_permissions(ctx.guild.default_role, send_messages=False, add_reactions=False)

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
        idp_role = idp_role or await ctx.guild.create_role(name=f"{_event_prefix}IDP", mentionable=True, color=self.bot.color.random())

        try:
            _scrim_obj = ScrimModel(
                name=scrim_name,
                mentions=mentions,
                reg_channel=_registration_channel.id,
                slot_channel=_slot_channel.id,
                idp_role=idp_role.id,
                guild_id=ctx.guild.id,
                scrim_name=scrim_name,
                start_time=_parsed_start_time,
                end_time=_parsed_end_time,
                total_slots=total_slots,
                time_zone=timezone.value,
                ping_role=ping_role.id if ping_role else None,
            )
            _scrim_obj.save()
            _embed = Embed(
                title=f"Scrim Created: {scrim_name}",
                color=self.bot.color.random()
            )
            _embed.add_field(name="Start Time", value=scrim_start_time, inline=False)
            _embed.add_field(name="End Time", value=scrim_end_time, inline=False)
            _embed.add_field(name="Total Slots", value=_scrim_obj.total_slots, inline=False)
            _embed.add_field(name="Time Zone", value=_scrim_obj.time_zone, inline=False)
            _embed.add_field(name="Slot Channel", value=f"<#{_scrim_obj.slot_channel}>", inline=False)
            _embed.add_field(name="Registration Channel", value=f"<#{_scrim_obj.reg_channel}>", inline=False)
            _embed.add_field(name="IDP Role", value=f"<@&{_scrim_obj.idp_role}>", inline=False)
            _embed.set_footer(text=f"Scrim ID: {_scrim_obj.reg_channel}")



            await ctx.followup.send(embed=_embed, ephemeral=True)

            await _registration_channel.send(embed=Embed(
                description=f"Scrim will start at {scrim_start_time}",
                color=self.bot.color.random()
            ))
            if self.scrim_log(ctx.guild):
                await self.scrim_log(ctx.guild).send(
                    embed=self.log_embed(f"Scrim created by {ctx.user.mention} in {ctx.guild.name} with name: {scrim_name}")
                )

        except ValueError as e:
            return await ctx.followup.send(f"Unable to create scrim: {str(e)}", ephemeral=True)


    def configure_start_message(self, scrim: ScrimModel):
        return f"""**{self.bot.emoji.tick} | TOTAL SLOT : {scrim.total_slots}
{self.bot.emoji.tick} | REQUIRED MENTIONS : {scrim.mentions}
{self.bot.emoji.tick} | END TIME : {self.bot.time.scrim_time_localize(time_str=scrim.end_time, to_tz=scrim.time_zone)}
{self.bot.emoji.tick} | RESERVED SLOTS : `{len(scrim.reserved)}`
    **"""


    @commands.Cog.listener()
    async def on_scrim_start_time_hit(self, scrim:ScrimModel):
        """Listener for when a scrim start time is hit."""

        _channel = self.bot.get_channel(scrim.reg_channel)

        if _channel.permissions_for(_channel.guild.me).send_messages:
    
            start_message = await  _channel.send(
                content=f"<@&{scrim.ping_role}>" if scrim.ping_role else None,
                embed = discord.Embed(
                    title=f"**{self.bot.emoji.cup} | REGISTRATION STARTED | {self.bot.emoji.cup}**",
                    description=self.configure_start_message(scrim=scrim), color=self.bot.color.random())
                )
            

            if _channel.permissions_for(_channel.guild.me).add_reactions:
                await start_message.add_reaction(self.bot.emoji.tick)


            def purge_filter(message:discord.Message):

                if message.id == start_message.id:
                    return False

                if self.bot.is_ws_ratelimited():
                    return False

                return True


            if _channel.permissions_for(_channel.guild.me).manage_messages:
                await _channel.purge(limit=scrim.total_slots+10, check=purge_filter, before=start_message)

        scrim.status = True
        scrim.save()



    @tasks.loop(seconds=10)
    async def monitor_scrims(self):
        _time = self.bot.time.scrim_format()

        scrims = ScrimModel.find(status=False, start_time=_time) # get all the pending scrims of this time frame

        print("scrims at time:", _time, "count:", len(scrims))
        if len(scrims) > 0:
            for scrim in scrims:
                self.bot.dispatch("scrim_start_time_hit", scrim)
