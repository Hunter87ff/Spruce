"""
A collection of command to manage the autorole all the features
    :author: hunter87
    :Copyright: (C) 2022-present hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""


from discord.ext import commands
from typing import TYPE_CHECKING
from ext.models import GuildAutoRoleModel
from discord import app_commands, Role, Member, Embed, Interaction

if TYPE_CHECKING:
    from core.bot import Spruce


class AutoRoleCog(commands.GroupCog, name="autorole", description="Auto role management commands"):
    def __init__(self, bot:'Spruce') -> None:
        self.bot = bot

    autorole_add = app_commands.Group(
        name="add",
        description="Add auto roles for the guild",
        guild_only=True
    )

    def is_role_accessible(self, role: Role) -> bool:
        """Check if the role is accessible by the bot"""
        if role.is_default():
            return False
        if role.managed:
            return False
        if role.position >= role.guild.me.top_role.position:
            return False
        return True


    @commands.hybrid_command(name="list", description="List auto roles for the guild")
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def autorole_list(self, ctx: commands.Context) -> None:

        _autoroles = await GuildAutoRoleModel.find_one(ctx.guild.id)
        if not _autoroles:
            return await ctx.send("No auto roles found for this guild")

        _message = f"""
        **Human Members**: {"<@&" + str(_autoroles.auto_role_human) + ">" if _autoroles.auto_role_human else "`not-set`"}
        **Bot Members**: {"<@&" + str(_autoroles.auto_role_bot) + ">" if _autoroles.auto_role_bot else "`not-set`"}
        **All Members**: {"<@&" + str(_autoroles.auto_role_all) + ">" if _autoroles.auto_role_all else "`not-set`"}
        """

        _embed = Embed(
            title="Auto Roles",
            description=_message,
            color=self.bot.color.random()
        )
        await ctx.send(embed=_embed)



    @autorole_add.command(name="human", description="Add auto roles to human members")
    @app_commands.describe(role="The role to add")
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def autorole_add_human(self, ctx: Interaction, role: Role) -> None:
        """Add auto roles to human members
        
        Arguments:
            role (Role): The role to add as auto role for human members
        """
        await ctx.response.defer(ephemeral=True)


        if not self.is_role_accessible(role):
            return await ctx.followup.send("Seems like the role is higher than mine or not accessible !!", ephemeral=True)
        

        _autoroles = await GuildAutoRoleModel.find_one(ctx.guild.id)
        if not _autoroles:
            _autoroles = await GuildAutoRoleModel.create(
                guild_id=ctx.guild.id,
                auto_role_human=role.id
            )
            if not _autoroles:
                await ctx.followup.send("Failed to create auto role model")
                return
            
            await ctx.followup.send(f"Added {role.mention} to auto roles for human members")
            return


        if role.id == _autoroles.auto_role_human:
            await ctx.followup.send(f"{role.mention} is already set as auto role for human members")
            return
        
        _autoroles.auto_role_human=role.id
        await _autoroles.save()
        await ctx.followup.send(f"Added {role.mention} to auto roles for human members")



    @autorole_add.command(name="bot", description="Add auto roles to bot members")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(role="The role to add")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def autorole_add_bot(self, ctx: Interaction, role: Role) -> None:
        """Add auto roles to bot members"""

        if not self.is_role_accessible(role):
            await ctx.followup.send("Seems like the role is higher than mine or not accessible !!", ephemeral=True)
            return

        _autoroles = await GuildAutoRoleModel.find_one(ctx.guild.id)

        if not _autoroles:
            _autoroles = await GuildAutoRoleModel.create(
                guild_id=ctx.guild.id,
                auto_role_bot=role.id
            )
            if not _autoroles:
                await ctx.followup.send("Failed to create auto role model")
                return
            await ctx.followup.send(f"Added {role.mention} to auto roles for bot members")
            return


        if role.id == _autoroles.auto_role_bot:
            await ctx.followup.send(f"{role.mention} is already set as auto role for bot members")
            return

        _autoroles.auto_role_bot=role.id
        await _autoroles.save()
        await ctx.followup.send(f"Added {role.mention} to auto roles for bot members")


    @commands.hybrid_command(name="reset", description="Reset auto roles for the guild")
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def auto_role_reset(self, ctx: commands.Context) -> None:
        """Reset auto roles for the guild"""
        try:
            _autoroles = await GuildAutoRoleModel.find_one(ctx.guild.id)
            if not _autoroles:
               await ctx.send("No auto roles found for this guild")
               return

            _autoroles.reset()
            await ctx.send("Auto roles reset successfully")

        except Exception as e:
            self.bot.logger.error(f"Failed to reset auto roles for {ctx.guild.id}: {e}")
            await ctx.send("Failed to reset auto roles")




    @commands.Cog.listener(name="on_member_join")
    async def on_member_join(self, member: Member) -> None:
        try:
            _autoroles = await GuildAutoRoleModel.find_one(member.guild.id)
            if not _autoroles:
                return
            
            if not member.bot and _autoroles.auto_role_human:
                role = member.guild.get_role(_autoroles.auto_role_human)
                if role:
                    await member.add_roles(role)

            if member.bot and _autoroles.auto_role_bot:
                role = member.guild.get_role(_autoroles.auto_role_bot)
                if role:
                    await member.add_roles(role)

            if _autoroles.auto_role_all:
                role = member.guild.get_role(_autoroles.auto_role_all)
                if role:
                    await member.add_roles(role)

        except Exception as e:
            self.bot.logger.error(f"Failed to add auto role to {member.name}: {e}")
            return