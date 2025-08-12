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

    if message.channel.id not in ScrimModel._REGISTER_CHANNEL_CACHE:
        self.debug(f"❌ Check 1.1 failed for scrim registration. Channel {message.channel.id} is not a scrim registration channel.")
        return

    if discord.utils.get(message.author.roles, name=self.bot.config.TAG_IGNORE_ROLE):
        return  # Ignore messages from users with the scrim-ignore-tag role

    _scrim = await ScrimModel.find_by_reg_channel(message.channel.id)

    if not _scrim:
        return

    #  if no scrim is found or not active, return
    if not _scrim.status:
        return


    #  Check if the member is already registered for the scrim (having idp role)
    if not _scrim.multi_register and message.author.id in _scrim.teams:
        await message.delete(delay=1)
        await message.channel.send( f"**{message.author.mention}**: You are already registered. Please wait for the next one.",  delete_after=10 )
        await self.log(message.guild, f"{message.author.mention} tried to register a team but is already registered.", self.bot.color.red)
        return
    
    confirm_role = message.guild.get_role(_scrim.idp_role)

    #  check if there is any available slot for registration
    if _scrim.available_slots() <= 0:
        await message.channel.send( f"**{message.author.mention}**: All slots are full for this scrim. Please wait for the next one.", delete_after=10 )
        
        #  log action info
        await self.log(message.guild, f"All slots are full for scrim <#{_scrim.reg_channel}>. {message.author.mention} tried to register a team.", self.bot.color.red)
        return
    

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
        
    try:
        await message.add_reaction(self.bot.emoji.tick)
        _scrim.add_team(captain=message.author.id, name=_team_name)
        await message.author.add_roles(confirm_role, reason="Scrim registration")

    except Exception as e:
        await self.log(
            message.guild,
            "Registration message deleted suddenly, unable to add tick reaction"
        )

    await _scrim.save()

    if _scrim.available_slots() <= 0:
        self.bot.dispatch("scrim_close_time_hit", _scrim)

    await self.log(message.guild, f"{message.author.mention} has registered for scrim {_scrim.name}.", color=self.bot.color.green)


async def handle_scrim_start(self : ScrimCog, scrim:ScrimModel):
    """Listener for when a scrim start time is hit."""
    _debug = False
    _open_time_delta = self.time.now().timestamp() - scrim.open_time
    if _open_time_delta > self.scrim_interval or not scrim.is_open_day():
        scrim.next_open_time()
        return await self.log(
            self.bot.get_guild(scrim.guild_id),
            f"Scrim {scrim.name} is not open today. Skipping to next open day.",
            self.bot.color.yellow
        )
    _channel = self.bot.get_channel(scrim.reg_channel)
    if not _channel:
        guild = self.bot.get_guild(scrim.guild_id)
        await self.log(
            guild,
            f"Scrim {scrim.name} registration channel not found. Deleting the scrim.",
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

    if not _idp_role:
        return await self.log(
            _channel.guild,
            "Idp role not found to start scrim.",
            self.bot.color.red
        )
        

    # update the scrim status and open time
    scrim.start()
    await scrim.save()
    

    ping_role = _channel.guild.get_role(scrim.ping_role) if scrim.ping_role else None
    mention_content = None
    
    if ping_role:
        if ping_role.is_default():
            mention_content = "@everyone"

        else:
            mention_content = ping_role.mention

    available_slots = scrim.available_slots()
    await _channel.send(
        content=mention_content,
        embed = discord.Embed(
            title=f"**{self.bot.emoji.cup} | REGISTRATION STARTED | {self.bot.emoji.cup}**",
            description=f"**{self.bot.emoji.tick} | AVAILABLE SLOTS : {available_slots}/{scrim.total_slots}\n{self.bot.emoji.tick} | RESERVED SLOTS : {len(scrim.reserved)}\n{self.bot.emoji.tick} | REQUIRED MENTIONS : {scrim.mentions}\n{self.bot.emoji.tick} | CLOSE TIME : <t:{int(scrim.close_time)}:t>(<t:{int(scrim.close_time)}:R>)**",
            color=self.bot.color.green
        )
    )

    await self.bot.helper.unlock_channel(_channel, _channel.guild.get_role(scrim.open_role or 582005))
    
    await self.log(
        _channel.guild,
        f"Scrim <#{_channel.id}> has been opened for registration. Available slots: {available_slots}/{scrim.total_slots}.",
        self.bot.color.green
    )


async def handle_scrim_end(self : ScrimCog, scrim:ScrimModel):
    """Listener for when a scrim end time is hit."""
    
    self.debug(f"Scrim close time hit for {scrim.name} in {scrim.guild_id} at {self.time.now()}")

    _channel = self.bot.get_channel(scrim.reg_channel)
    if not _channel:
        return
    
    scrim.next_close_time()
    team_count = len(scrim.get_teams())
    scrim.status = False
    scrim.cleared = False
    await scrim.save()

    await self.log(_channel.guild, f"Scrim {_channel.mention} has ended. Team registered : {team_count}.", color=self.bot.color.green)
    self.debug(f"Setting up scrim group for {scrim.name} in {_channel.guild.name}.")
    await self.setup_group(scrim)
    self.debug(f"Scrim group setup completed for {scrim.name} in {_channel.guild.name}. locking registration channel.")
    await self.bot.helper.lock_channel(_channel, _channel.guild.get_role(scrim.open_role or 582005))


async def handle_scrim_clear(self: ScrimCog, scrim: ScrimModel):
    """Listener for when a scrim clean time is hit."""

    if scrim.cleared:
        return
    
    _reg_channel = self.bot.get_channel(scrim.reg_channel)
    if not _reg_channel:
        return

    idp_role = await _reg_channel.guild.fetch_role(scrim.idp_role)
    if not idp_role:
        return
    old_players = [await self.get_member(idp_role.guild, _id) for _id in scrim.captain_ids()]

    for member in old_players:
        await member.remove_roles(idp_role)

    await _reg_channel.purge(reason="Clearing old scrim participants")
    scrim.cleared = True
    scrim.clear_teams()
    await scrim.save()
    await self.log(idp_role.guild, f"Scrim <#{scrim.reg_channel}> has been cleaned up.", self.bot.color.yellow)
