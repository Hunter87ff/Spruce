import discord
from typing import TYPE_CHECKING
from ext import permissions, constants
from discord.ext import commands, tasks
from ext.models.scrim import ScrimModel
from discord import Embed, TextChannel,  Interaction,   app_commands as app


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
        self.TAG_IGNORE_ROLE = "scrim-ignore-tag"


    def log_embed(self, message:str):
        embed = Embed(title="Scrim Log", description=message, color=self.bot.color.random())
        return embed


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
            if self.bot.helper.get_scrim_log(ctx.guild):
                await self.bot.helper.get_scrim_log(ctx.guild).send(
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


    @app.command(name="audit", description="Audit a scrim by its ID.")
    @app.guild_only()
    @app.describe(
        reg_channel="Registration channel of the scrim to audit (required)",
    )
    async def audit_scrim(self, ctx:discord.Interaction, reg_channel:discord.TextChannel):
        """Audit a scrim by its registration channel."""
        await ctx.response.defer(ephemeral=True)

        _scrim = ScrimModel.find_one(reg_channel=reg_channel.id)

        if not _scrim:
            return await ctx.followup.send("No scrim found for the provided registration channel.", ephemeral=True)
        reg_channel: TextChannel = self.bot.get_channel(_scrim.reg_channel)
        idp_role = ctx.guild.get_role(_scrim.idp_role)
        slot_channel = self.bot.get_channel(_scrim.slot_channel)

        if not reg_channel:
            return await ctx.followup.send("Registration channel not found in the scrim. Please update it.", ephemeral=True)

        if not idp_role:
            return await ctx.followup.send("IDP role not found in the scrim. Please update it.", ephemeral=True)

        if not slot_channel:
            return await ctx.followup.send("Slot channel not found in the scrim. Please update it.", ephemeral=True)

        reg_read_perms = reg_channel.permissions_for(ctx.guild.me).read_messages
        reg_send_perms = reg_channel.permissions_for(ctx.guild.me).send_messages
        reg_manage_message_perms = reg_channel.permissions_for(ctx.guild.me).manage_messages
        reg_add_reactions_perms = reg_channel.permissions_for(ctx.guild.me).add_reactions

        slot_read_perms = slot_channel.permissions_for(ctx.guild.me).read_messages
        slot_send_perms = slot_channel.permissions_for(ctx.guild.me).send_messages
        slot_manage_message_perms = slot_channel.permissions_for(ctx.guild.me).manage_messages
        slot_add_reactions_perms = slot_channel.permissions_for(ctx.guild.me).add_reactions

        manage_role_perms = ctx.guild.me.guild_permissions.manage_roles
        manage_channel_perms = ctx.guild.me.guild_permissions.manage_channels
        read_history_perms = reg_channel.permissions_for(ctx.guild.me).read_message_history

        having_perm = all([
            reg_read_perms,
            reg_send_perms,
            reg_manage_message_perms,
            reg_add_reactions_perms,
            slot_read_perms,
            slot_send_perms,
            slot_manage_message_perms,
            slot_add_reactions_perms,
            manage_role_perms,
            manage_channel_perms,
            read_history_perms
        ])

        missing_perms = []
        if not having_perm:
            if not reg_read_perms:
                missing_perms.append("read_messages")
            if not reg_send_perms:
                missing_perms.append("send_messages")
            if not reg_manage_message_perms:
                missing_perms.append("manage_messages")
            if not reg_add_reactions_perms:
                missing_perms.append("add_reactions")
            if not manage_role_perms:
                missing_perms.append("manage_roles")
            if not manage_channel_perms:
                missing_perms.append("manage_channels")
            if not read_history_perms:
                missing_perms.append("read_message_history")

            return await ctx.followup.send(
                f"Missing permissions to manage the scrim: `{'`, '.join(missing_perms)}. Please update the permissions and try again.",
                ephemeral=True
            )


        embed = discord.Embed(
            title=f"Scrim Audit: {reg_channel.name}",
            description=self.configure_start_message(scrim=_scrim),
            color=self.bot.color.random()
        )
        embed.add_field(name="IDP Role", value=f"<@&{_scrim.idp_role}>", inline=False)
        embed.add_field(name="Ping Role", value=f"<@&{_scrim.ping_role}>" if _scrim.ping_role else "None", inline=False)
        embed.add_field(name="Total Slots", value=_scrim.total_slots, inline=False)
        embed.add_field(name="Reserved Slots", value=len(_scrim.reserved), inline=False)
        
        await ctx.followup.send(embed=embed, ephemeral=True)





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



    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        """Listener for when a message is sent in a scrim registration channel."""
        if message.author.bot or not isinstance(message.channel, discord.TextChannel):
            return
        
        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        
        if not message.channel.permissions_for(message.guild.me).manage_messages:
            return
        
        if not message.channel.permissions_for(message.guild.me).read_message_history:
            return

        if not message.channel.permissions_for(message.guild.me).add_reactions:
            return
        
        if not message.guild.me.guild_permissions.manage_roles:
            return

        if discord.utils.get(message.author.roles, name=self.TAG_IGNORE_ROLE):
            return  # Ignore messages from users with the scrim-ignore-tag role

        log_channel = self.bot.helper.get_scrim_log(message.guild)
        _scrim = ScrimModel.find_one(reg_channel=message.channel.id)
        
        #  if no scrim is found, return
        if not _scrim or not _scrim.status:
            return
        
        available_slots = _scrim.total_slots - len(_scrim.reserved) if _scrim else 0 
        scrim_mod_role = discord.utils.get(message.guild.roles, name="scrim-mod")
        confirm_role = message.guild.get_role(_scrim.idp_role)


        # check if idp role exists or not, if  not, then close the scrim and inform the scrim mod role if exists
        if not confirm_role:
            _scrim.status = False
            _scrim.save()

            await log_channel.send(
                content=scrim_mod_role.mention if scrim_mod_role else None,
                embed=self.log_embed(f"IDP role not found for scrim {_scrim.name}. Please check the scrim configuration.")
            )


        #  Check if the member is already registered for the scrim (having idp role)
        if discord.utils.get(message.author.roles, id=_scrim.idp_role):
            await message.channel.send(
                f"**{message.author.mention}**: You are already registered for this scrim.",
                delete_after=10
            )
            return

        #  check if there is any available slot for registration
        if available_slots <= 0:

            await message.channel.send(
                f"**{message.author.mention}**: All slots are full for this scrim. Please try again later.",
                delete_after=10
            )

            #  log action info
            if log_channel:
                await log_channel.send(
                    embed=self.log_embed(f"{_scrim.name} closed as all slots are full. still {message.author.mention} tried to register a team.")
                )

            return None # no available slots
        

        _team_name = self.bot.helper.parse_team_name(message)

        #  Check if the team name is provided
        if not _team_name:
            await message.channel.send(
                f"**{message.author.mention}**: Please provide a valid team name in the format `team <team_name>`\nExample `TEAM XPERIENCED`.",
                delete_after=10
            )
            await message.delete()
            return
        


        #  Check if the team name is valid
        if len(_team_name) < 3 or len(_team_name) > 20:
            await message.channel.send(
                f"**{message.author.mention}**: Team name must be between 3 and 20 characters long.",
                delete_after=10
            )
            return
        

        #  checking for duplicate tag invalidation if duplicate tag is enabled
        if _scrim.duplicate_tag_check:
            is_duplicate_tag = await self.bot.helper.duplicate_tag_check(confirm_role, message)
                
            if is_duplicate_tag:
                await message.delete()
                await message.channel.send(
                    embed=discord.Embed(
                        title="Duplicate Tag Detected",
                        description=f"{is_duplicate_tag.mention} you've mentioned is registered to a different [team]({is_duplicate_tag.message.jump_url}). Please check your mentions and try again.",
                    )
                )
                return
            
        await message.author.add_roles(confirm_role, reason="Scrim registration")
        await message.add_reaction(self.bot.emoji.tick)
        await log_channel.send(
            embed=self.log_embed(f"{message.author.mention} has registered for scrim {_scrim.name}.")
        )



        
            





    @commands.Cog.listener()
    async def on_scrim_end_time_hit(self, scrim:ScrimModel):
        """Listener for when a scrim end time is hit."""

        _channel = self.bot.get_channel(scrim.slot_channel)

        if _channel.permissions_for(_channel.guild.me).send_messages:
            end_message = await _channel.send(
                content=f"<@&{scrim.ping_role}>" if scrim.ping_role else None,
                embed=discord.Embed(
                    title=f"**{self.bot.emoji.cup} | REGISTRATION ENDED | {self.bot.emoji.cup}**",
                    description=self.DEFAULT_END_MESSAGE, color=self.bot.color.random()
                )
            )

        if end_message is not None and _channel.permissions_for(_channel.guild.me).add_reactions:
            await end_message.add_reaction(self.bot.emoji.tick)

        _team_count = 1
        _slot_message_content = ""
        slot_embed = discord.Embed(
            title=f"**{self.bot.emoji.cup} | SLOTS FOR {scrim.name.upper()} | {self.bot.emoji.cup}**",
            color=self.bot.color.random()
        )

        if len(scrim.reserved) > 0:
            for slot in scrim.reserved:
                _slot_message_content += f"**`{_team_count}`) {slot.team_name.upper()}**\n"
                _team_count += 1


        async for message in _channel.history(limit=scrim.total_slots+50, before=end_message):
            if not message.author.id == self.bot.user.id:
                continue

            team = self.bot.helper.parse_team_name(message)

            if not discord.utils.get(message.author.roles, id=scrim.idp_role):
                continue

            _slot_message_content += f"**`{_team_count}`) {team.upper()}**\n"
            _team_count += 1


        slot_embed.description = _slot_message_content
        await _channel.send(embed=slot_embed)

        scrim.status = False
        scrim.save()





    @tasks.loop(seconds=10)
    async def monitor_scrims(self):
        _time = self.bot.time.scrim_format()

        scrims = ScrimModel.find(status=False, start_time=_time) # get all the pending scrims of this time frame

        print("scrims at time:", _time, "count:", len(scrims))
        if len(scrims) > 0:
            for scrim in scrims:
                self.bot.dispatch("scrim_start_time_hit", scrim)
