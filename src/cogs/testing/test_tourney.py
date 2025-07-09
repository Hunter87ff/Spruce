import asyncio
from discord.ext import commands
from ext import checks
from ext.modals import Tourney
from typing import TYPE_CHECKING
from ext import color
from discord import Embed, TextChannel, Member, Message, app_commands, Interaction, utils, Guild

if TYPE_CHECKING:
    from core.bot import Spruce

class TestTourney(commands.GroupCog, name="test_tourney", description="Test Tourney Commands"):
    bot: "Spruce" = None

    def __init__(self, bot : "Spruce"):
        self.bot = bot
        self._tnotfound = "Tournament Not Found"


    async def log(self, guild:Guild, message:str, color:int=color.cyan):
        channel = utils.get(guild.text_channels, name=self.bot.config.LOG_CHANNEL_NAME)
        if not channel:
            return 
        
        embed =  Embed(description=message, color=color)
        embed.set_author(name=guild.me.name, icon_url=guild.me.avatar)
        await channel.send(embed=embed)


    @app_commands.command(name="auto_group", description="Automatically create groups for the tournament")
    @app_commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.guild)
    @checks.tourney_mod(interaction=True)
    @app_commands.describe(reg_channel="mention the registration channel")
    async def auto_group(self, ctx:Interaction, reg_channel: TextChannel, from_group:int=1, create_channels:bool=False):
        if ctx.user.bot:
            return

        await ctx.response.defer(ephemeral=True)

        _event = Tourney.findOne(reg_channel.id)
        if not _event: 
            return await ctx.followup.send(self._tnotfound, delete_after=10)

        confirm_channel = self.bot.get_channel(_event.cch)
        group_channel = self.bot.get_channel(_event.gch)

        if not any([confirm_channel, group_channel]):
            await self.log(ctx.guild, message=f"Confirm Channel or Group Channel Not Found\nConfirm Channel: <#{_event.cch}>\nGroup Channel: <#{_event.gch}>")
            return await ctx.followup.send("Confirm Channel or Group Channel Not Found")

        slot_per_group = _event.spg # slots per group
        current_group_position = int(
            min(
                _event.reged-_event.spg, 
                max(
                    0, (from_group*_event.spg)-1
                )
            )
        ) # current group position in slots must be less than the number of registered teams

        # check permission for confirm channel for bot
        if not confirm_channel.permissions_for(ctx.guild.me).read_message_history:
            await ctx.followup.send(f"I Don't Have Permission To Read Message History In {confirm_channel.mention}")
            return
        
        teams = []
        # old confirm messages
        async for msg in confirm_channel.history(limit=_event.reged+50, oldest_first=True):
            if all([ msg.author.id == self.bot.user.id,  len(msg.embeds) > 0 ]):
                if "TEAM" in msg.embeds[0].description:
                    teams.append(msg)

        if len(teams) < 1:
            await self.log(ctx.guild, message=f"No Teams Found In Confirm Channel: <#{confirm_channel.id}>")
            return await ctx.followup.send("Minimum Number Of Teams Isn't Reached!!")

        group = int(len(teams)/slot_per_group)

        # Ensure at least one group
        if len(teams) % slot_per_group != 0:
            group += 1
        if group < 1:
            group = 1

        # Create category once if needed
        category = None
        if create_channels:
            category = await ctx.guild.create_category(name=f"{_event.prefix} Groups")
            await category.set_permissions(ctx.guild.default_role, view_channel=False)

        # private channels for each group
        for i in range(max(1, current_group_position//slot_per_group), group+1):
            ms = f"**__GROUP__ : {i:02d}\n"
            # if the current group position is greater than the number of teams, break

            if current_group_position >= len(teams):
                break

            # get the messages for each group
            self.bot.debug(f"Current Group Position: {current_group_position}, Slot Per Group: {slot_per_group}", is_debug=True)
            current_group:list[ Message] = teams[current_group_position:current_group_position+slot_per_group]

            for index, team in enumerate(current_group, start=1):
                ms = ms + f"> {index}) {team.content}" + "\n"

            # increase the starting position for the next group
            current_group_position += slot_per_group
            msg = await group_channel.send(f"{ms}**")

            if create_channels and category:
                channel = await ctx.guild.create_text_channel(name=f"{_event.prefix}-group-{i}", category=category)
                await channel.send(msg.content)
                role = await ctx.guild.create_role(name=f"{_event.prefix.upper()} G{i}", color=0x4bd6af)
                overwrite = channel.overwrites_for(role)
                overwrite.view_channel = True
                overwrite.send_messages = False
                overwrite.add_reactions = False
                overwrite.attach_files = True
                await channel.set_permissions(role, overwrite=overwrite)
                await asyncio.sleep(1)

                for member in msg.mentions:
                    if isinstance(member, Member): 
                        await asyncio.sleep(0.5)
                        await member.add_roles(role)

            await msg.add_reaction(self.bot.emoji.tick)

        await self.log(ctx.guild, message=f"Created Group Channels For Tournament: {reg_channel.mention} | Group Channel: {group_channel.mention}")
        await ctx.followup.send(f"check this channel {group_channel.mention}")

