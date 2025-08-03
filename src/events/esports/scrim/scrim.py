from __future__ import annotations
import discord
from models import ScrimModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cogs.esports import ScrimCog


async def handle_scrim_registration(self : ScrimCog, message:discord.Message):
    """Listener for when a message is sent in a scrim registration channel."""
    if not message.guild:
        return 
    
    if not all([
        not message.author.bot,
        isinstance(message.channel, discord.TextChannel),
        isinstance(message.author, discord.Member),
        message.guild,
        message.guild.me.guild_permissions.manage_messages,
        message.guild.me.guild_permissions.add_reactions,
        message.guild.me.guild_permissions.manage_roles,
    ]):
        return
    self.debug("✅ Check 1 passed for scrim registration. bot having all the permsissions.")

    if discord.utils.get(message.author.roles, name=self.bot.config.TAG_IGNORE_ROLE):
        return  # Ignore messages from users with the scrim-ignore-tag role

    _scrim = await ScrimModel.find_by_reg_channel(message.channel.id)

    if not _scrim:
        return

    #  if no scrim is found or not active, return
    if not _scrim.status:
        return
    
    self.debug(f"✅ Check 1.1 passed for scrim registration. Scrim found: {_scrim.name} with status: {_scrim.status}")


    #  Check if the member is already registered for the scrim (having idp role)
    if not _scrim.multi_register and message.author.id in _scrim.teams:
        await message.delete(delay=1)
        await message.channel.send( f"**{message.author.mention}**: You are already registered. Please wait for the next one.",  delete_after=10 )
        await self.log(message.guild, f"{message.author.mention} tried to register a team but is already registered.", self.bot.color.red)
        return
    
    self.debug("✅ Check 1.6 passed for scrim registration. Member is not already registered.")

    available_slots = _scrim.total_slots - (len(_scrim.reserved) + len(_scrim.teams))
    confirm_role = message.guild.get_role(_scrim.idp_role)
    self.debug(f"✅ Check 2 passed for scrim registration. Available slots: {available_slots}, IDP Role: {confirm_role}")

    #  check if there is any available slot for registration
    if available_slots <= 0:
        await message.channel.send( f"**{message.author.mention}**: All slots are full for this scrim. Please wait for the next one.", delete_after=10 )
        
        #  log action info
        await self.log(message.guild, f"All slots are full for scrim <#{_scrim.reg_channel}>. {message.author.mention} tried to register a team.", self.bot.color.red)
        return
    
    self.debug("✅ Check 3 passed for scrim registration.")

    # check if idp role exists or not, if  not, then close the scrim and inform the scrim mod role if exists
    if not confirm_role:
        await self.log(message.guild, self.DEFAULT_NO_IDP_ROLE, color=self.bot.color.red)
        return

    #  check if the idp role is higher than the bot's top role
    if confirm_role.position >= message.guild.me.top_role.position:
        await message.channel.send(
            f"**{message.author.mention}**: I cannot add the IDP role `{confirm_role.name}` to you because it is higher than my top role. Please contact a server admin to resolve this issue.",
            delete_after=10
        )
        await self.log(message.guild, f"{message.author.mention} tried to register a team but I cannot add the IDP role `{confirm_role.name}` because it is higher than my top role.", color=self.bot.color.red)
        return

    #  Check if the team name is valid
    _team_name = self.bot.helper.parse_team_name(message, _scrim.team_compulsion)
    if not _team_name:
        await message.channel.send( f"**{message.author.mention}**: You must provide a team name. something like `TEAM NAME : XPERIENCED`", delete_after=10 )
        return
    

    #  check if the required mentions are met
    if len(message.mentions) < _scrim.mentions:
        await message.channel.send( f"**{message.author.mention}**: You must mention at least {_scrim.mentions} members to register a team.", delete_after=10 )
        await message.delete()
        await self.log(message.guild, f"{message.author.mention} tried to register a team but did not mention enough members. Required: {_scrim.mentions}, Mentioned: {len(message.mentions)}", color=self.bot.color.red)
        return

    #  checking for duplicate tag invalidation if duplicate tag is enabled
    if not _scrim.duplicate_tag: #if duplicate tag is not allowed
        is_duplicate_tag = await self.bot.helper.duplicate_tag(self.bot, confirm_role, message)
            
        if is_duplicate_tag:
            await message.delete(delay=1)
            await message.channel.send(
                embed=discord.Embed(
                    title="Duplicate Tag Detected",
                    description=f"{is_duplicate_tag.mention} you've mentioned is registered to a different [team]({is_duplicate_tag.message.jump_url}). Please check your mentions and try again.", color=self.bot.color.red
                ), delete_after=10
            )
            await self.log(message.guild, f"{message.author.mention} tried to register a team with a duplicate tag: {is_duplicate_tag.mention}.", color=self.bot.color.red)
            return
        
    self.debug("✅ Check 4 passed for scrim registration. Team name and mentions are valid.")
    try:
        await message.author.add_roles(confirm_role, reason="Scrim registration")
        await message.add_reaction(self.bot.emoji.tick)

    except Exception as e:
        await self.log(
            message.guild,
            "Registration message deleted suddenly, unable to add tick reaction"
        )
        self.debug(f"❌ Check 5 failed for scrim registration. Error: {str(e)}")
        
    self.debug("✅ Check 5 passed for scrim registration. IDP role added to the author.")

    #  add the team to the scrim
    _scrim.add_team(captain=message.author.id, name=_team_name)
    await _scrim.save()
    self.debug("✅ Check 6 passed for scrim registration. Team added to the scrim.")

    team_count = len(_scrim.teams) + len(_scrim.reserved)

    if team_count >= _scrim.total_slots:
        self.bot.dispatch("scrim_close_time_hit", _scrim)

    await self.log(message.guild, f"{message.author.mention} has registered for scrim {_scrim.name}.", color=self.bot.color.green)


async def handle_scrim_start(self : ScrimCog, scrim:ScrimModel):
    """Listener for when a scrim start time is hit."""
    _debug = False
    self.bot.debug(f"Scrim open time hit for {scrim.name} in {scrim.guild_id} at {self.time.now()}", is_debug=_debug)

    if not scrim.is_open_day():
        await scrim.skip_to_next_day()
        return await self.log(
            self.bot.get_guild(scrim.guild_id),
            f"Scrim {scrim.name} is not open today. Skipping to next open day.",
            self.bot.color.yellow
        )

    _channel = self.bot.get_channel(scrim.reg_channel)
    if not _channel or scrim.is_inactive():
        guild = self.bot.get_guild(scrim.guild_id)
        await self.log(
            guild,
            f"Scrim {scrim.name} registration channel not found, and the scrim is older than 30 days. Deleting the scrim.",
            self.bot.color.red
        )
        await scrim.delete()
        return

    # check all the perms
    if not all([
        _channel.permissions_for(_channel.guild.me).send_messages,
        _channel.permissions_for(_channel.guild.me).add_reactions,
        _channel.permissions_for(_channel.guild.me).read_message_history,
        _channel.guild.me.guild_permissions.manage_messages,
        _channel.guild.me.guild_permissions.manage_roles,
    ]):
        return await self.log(
            _channel.guild,
            f"Scrim {_channel.mention} could not be started as I don't have the required permissions : `manage_messages`, `add_reactions`, `manage_roles`, `read_message_history`, in the registration channel.",
            self.bot.color.red
        )

    _idp_role = _channel.guild.get_role(scrim.idp_role)
    try:
        if not _idp_role:
            return await self.log(
                _channel.guild,
                "Idp role not found to start scrim.",
                self.bot.color.red
            )
        for member in _idp_role.members if _idp_role else []:
            if _idp_role.position >= _channel.guild.me.top_role.position:
                await self.log(
                    _channel.guild,
                    f"Could not remove IDP role {scrim.idp_role} from {member.mention} in scrim {_channel.mention} as the role is higher than my top role.",
                    self.bot.color.red
                )
                continue
            await member.remove_roles(_idp_role, reason="Scrim registration started, removing IDP role.")

    except Exception:
        return await self.log(
            _channel.guild,
            f"Could not remove IDP role <@&{scrim.idp_role}> from members in scrim {_channel.mention} due to insufficient permissions. or missing role. \nPlease ensure I have the `manage_roles` permission. and the IDP role is lower than my top role.",
            self.bot.color.red
        )

    # update the scrim status and open time
    scrim.open(next=True, clear_teams=True)
    await scrim.save()

    ping_role = _channel.guild.get_role(scrim.ping_role) if scrim.ping_role else None
    mention_content = None
    
    if ping_role:
        if ping_role.is_default():
            mention_content = "@everyone"

        else:
            mention_content = ping_role.mention
        
    available_slots = scrim.total_slots - (len(scrim.reserved) + len(scrim.teams))
    start_message = await _channel.send(
        content=mention_content,
        embed = discord.Embed(
            title=f"**{self.bot.emoji.cup} | REGISTRATION STARTED | {self.bot.emoji.cup}**",
            description=f"**{self.bot.emoji.tick} | AVAILABLE SLOTS : {available_slots}/{scrim.total_slots}\n{self.bot.emoji.tick} | RESERVED SLOTS : {len(scrim.reserved)}\n{self.bot.emoji.tick} | REQUIRED MENTIONS : {scrim.mentions}\n{self.bot.emoji.tick} | CLOSE TIME : <t:{int(scrim.close_time)}:t>(<t:{int(scrim.close_time)}:R>)**",
            color=self.bot.color.green
        )
    )

    if _channel.permissions_for(_channel.guild.me).add_reactions:
        await start_message.add_reaction(self.bot.emoji.tick)

    def purge_filter(message: discord.Message):
        return not self.bot.is_ws_ratelimited()

    await _channel.purge(limit=scrim.total_slots+10, check=purge_filter, before=start_message)
    await self.bot.helper.unlock_channel(_channel)


    await self.log(
        _channel.guild,
        f"Scrim <#{_channel.id}> has been opened for registration. Available slots: {available_slots}/{scrim.total_slots}.",
        self.bot.color.green
    )



async def handle_scrim_end(self, scrim:ScrimModel):
    """Listener for when a scrim end time is hit."""

    scrim.close_time += self.scrim_interval
    self.debug(f"Scrim close time hit for {scrim.name} in {scrim.guild_id} at {self.time.now()}")

    scrim.status = False
    await scrim.save()

    _channel = self.bot.get_channel(scrim.reg_channel)
    team_count = len(scrim.teams) + len(scrim.reserved)

    await self.log(_channel.guild, f"Scrim {_channel.mention} has ended. Team registered : {team_count}.", color=self.bot.color.green)
    self.debug(f"Setting up scrim group for {scrim.name} in {_channel.guild.name}.")
    await self.setup_group(scrim)
    self.debug(f"Scrim group setup completed for {scrim.name} in {_channel.guild.name}. locking registration channel.")
    await self.bot.helper.lock_channel(_channel)

