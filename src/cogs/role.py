"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
"""
import os
from typing import TYPE_CHECKING
from asyncio import sleep
from modules import config
from discord.ext import commands
from discord import  Embed, Role, File, Member, utils, Guild, Message, app_commands, Interaction
from ext import constants,  color
cmd = commands

if TYPE_CHECKING:
    from modules.bot import Spruce


class RoleCog(commands.Cog):
    """
    ## RoleCog Class
    This class contains commands for managing roles in a Discord server.
    """
    def __init__(self, bot:"Spruce"):
        self.bot = bot

    @cmd.command(aliases=["croles"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def create_roles(self, ctx:commands.Context, *names:str):
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):return await config.vtm(ctx)
        for role in names:
            await ctx.guild.create_role(name=role, reason=f"Created by {ctx.author}")
            await sleep(1)
        await ctx.send(embed=Embed(description=f"{config.tick} | All roles created"), delete_after=5)


    @cmd.command(aliases=["droles"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def del_roles(self, ctx:commands.Context, *roles : Role):
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
            
        msg = await ctx.send(f"{config.loading} {constants.PROCESSING}")
        for role in roles:
            if ctx.author.top_role.position < role.position:
                return await ctx.send("Role Is Higher Than Your Top Role", delete_after=5)

            elif ctx.me.top_role.position < role.position:
                return await ctx.send("Role Is Higher Than My Top Role", delete_after=5)

            else:
                await role.delete(reason=f"Role {role.name} has been deleted by {ctx.author}")
                await sleep(2)
        await msg.edit(content=None, embed=Embed(color=self.bot.color.cyan, description=f"{config.tick} | Roles Successfully Deleted", delete_after=30))


    async def message_role(self, ctx:commands.Context, role:Role, ms:Message, bt:Member):
        if not ctx.message.reference:return await ms.edit(content="**Please reply to a message or mention users to give them a role**")
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        given = []
        for user in message.mentions:
            if len(message.mentions)<1: return await ms.edit(content="**No User Mentioned In The Message**")
            if user.top_role.position >= ctx.author.top_role.position:
                await ms.edit(content=f"{user}'s Role Is Equal Or Higher Than __Your Top Role__! I can not manage him")
                await sleep(3)
            elif bt.top_role.position <= user.top_role.position:
                await ms.edit(content=f"{user}'s Role Is Equal Or Higher Than __My Top Role__! I can not manage him")
                await sleep(3)

            elif isinstance(user, Member):
                await user.add_roles(role)
                given.append(user)
                await sleep(1)
        if ms:await ms.edit(content=f"Role Added To - {len(given)} Members")



    @cmd.command(aliases=["role"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True, send_messages=True)
    async def give_role(self, ctx:commands.Context, role: Role, *users: Member):
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):return await config.vtm(ctx)
        ms:Message = await ctx.send(f"{constants.PROCESSING}")
        given = []
        if ctx.me.top_role.position <= role.position and ms:return await ms.edit(content="```\nMy Top Role position Is not higher enough\n```")
        if ctx.author.top_role.position < role.position and ms:return await ms.edit(content="You can Not manage that role")
        if not users:return await self.message_role(ctx, role, ms, ctx.me)

        if len(users) > 1 and role.permissions.administrator:
            return await ms.edit(content="**I can't give admin role to more than 1 person. at a time**")

        for user in users:
            if user.top_role.position >= ctx.author.top_role.position:
                await ms.edit(content=f"{user}'s Role Is Higher Than __Your Top Role__! I can not manage him")
                await sleep(4)

            elif ctx.me.top_role.position < user.top_role.position:
                await ms.edit(content=f"{user}'s Role Is Higher Than __My Top Role__! I can not manage him")
                await sleep(4)
            else:
                await user.add_roles(role)
                given.append(user)
                await sleep(1)
        if ms:return await ms.edit(content=f"{role.mention} given To {len(given)} Members")




    @app_commands.command(description="Remove a role from all members")
    @app_commands.describe(role="The role to remove from all members", reason="The reason for removing the role")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True, send_messages=True)
    async def remove_members(self, interaction: Interaction, role: Role, reason: str = None):
        if interaction.user.bot:return
        await interaction.response.send_message(f"{config.loading} | {constants.PROCESSING}", ephemeral=True)
        if reason is None:
            reason = f"{role} removed from everyone by {interaction.user}"
        for member in role.members:
            await member.remove_roles(role, reason=reason)
            await sleep(2)
        await interaction.followup.send(content=f"**{config.tick} | {role} Removed from everyone**", ephemeral=True)



    @app_commands.command(description="Get the list of members in a role ")
    @app_commands.describe(role="Mention the role to get member list")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(send_messages=True, manage_roles=True)
    async def inrole(self, interaction:Interaction, role:Role):
        if interaction.user.bot:return
        elif not await config.voted(interaction, bot=self.bot):
            return await interaction.response.send_message("You need to vote to use this command", ephemeral=True)
        elif len(role.members) > 400:
            return await interaction.response.send_message("Too many members to show!!", ephemeral=True)
        elif (len(role.members) == 0):
            return await interaction.response.send_message("No members in this role", ephemeral=True)
        msg=""
        for i in role.members:
            msg = msg + f"\n{i.display_name} : <@{i.id}>"
        if len(msg) < 2000:
            emb = Embed(title=f"{role.name}", description=msg, color=color.random(color.cyan))
            await interaction.response.send_message(embed=emb)
        else:
            with open(file=f"{role.name}-{role.id}-members.txt", mode="w", encoding="utf-8") as f:
                f.write(msg)
            await interaction.response.send_message(file=File(f"{role.name}-{role.id}-members.txt"))
            os.remove(f"{role.name}-{role.id}-members.txt")
        



    @cmd.hybrid_command(with_app_command = True)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def port(self, ctx:commands.Context, role1: Role, role2: Role, reason=None):
        await ctx.defer()
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
        bt = ctx.guild.get_member(self.bot.user.id)
        if role2.position > bt.top_role.position:
            return await ctx.send("I Can't Manage This Role, It is Higher Than My Top Role")
        if role2.position > ctx.author.top_role.position:
            return await ctx.send("You Can't Manage This Role")
        await ctx.reply("If You're Running this command by mistake! You Can Run `&help ra_role`")
        if reason == None:
            reason = f"{role2.name} added by {ctx.author}"
        msg = await ctx.send(f"**{config.loading} {constants.PROCESSING}**")
        for m in role1.members:
            if m.top_role.position < bt.top_role.position:
                await m.add_roles(role2, reason=reason)
                await sleep(1)

        await msg.edit(content=f"{config.tick} **Role Added Successfully.**", delete_after=30)



    @cmd.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def remove_role(self, ctx:commands.Context, role:Role, *users: Member):
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
        bt = ctx.guild.get_member(self.bot.user.id)
        for user in users:
            if ctx.author.top_role.position < user.top_role.position:
                return await ctx.send(f"**You don't have enough permission to manage {user}'s role'**", delete_after=15)
            if bt.top_role.position < user.top_role.position:
                return await ctx.send(f"**I can't manage {user}'r role'**", delete_after=15)
            if bt.top_role.position < role.position:
                return await ctx.send("**I don't have enough permission to manage this role**", delete_after=15)
            else:
                await user.remove_roles(role, reason=f"Role removed by {ctx.author}")
        return await ctx.send(f"**{role.name} removed from these members**")



    @cmd.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def add_roles(self, ctx:commands.Context, user:Member, *roles:Role):
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
        bt = ctx.guild.get_member(self.bot.user.id)
        for role in roles:
            if bt.top_role.position > role.position:
                return await ctx.send("**My top role is not higher enough**", delete_after=20)
            if ctx.author.top_role.position < role.position:
                return await ctx.send("you don't have enough permission", delete_after=5)
            if user.top_role.position > ctx.author.top_role.position:
                return await  ctx.send("Your can not manage him")
            else:await user.add_roles(role)
        return await ctx.message.add_reaction("✅")


    @cmd.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def role_all_human(self, ctx:commands.Context, role: Role):
        if ctx.author.bot:return
        await ctx.defer()
        prs = await ctx.send(f"{constants.PROCESSING}")
        if role.permissions.administrator:
            return await prs.edit(content="**Sorry but i can not do this with a role with admin perms.**")
        if ctx.author.top_role.position <= role.position:
            return await prs.edit(content=f"**{config.cross}You Can't Manage This Role | The role should be higher than your top role.**")

        if utils.get(ctx.guild.members, id=self.bot.user.id).top_role.position < role.position:
            return await prs.edit(content="I can't manage This role")
        if len(ctx.guild.members) != ctx.guild.member_count:
            return await prs.edit(content="**I'm unable to see anyone! i don't know why. please contact support team!**")
        for member in ctx.guild.members:
            if not member.bot:
                await member.add_roles(role, reason=f"role all command used by {ctx.author}")
                await sleep(3)
        await prs.edit(content=None, embed=Embed(color=0x00ff00, description=f"**{config.tick} | {role.mention} Given To All These Humans**"))


    @cmd.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def role_all_bot(self, ctx:commands.Context, role: Role):
        await ctx.defer()
        if ctx.author.bot:return
        prs = await ctx.send(f"{constants.PROCESSING}")
        if role.permissions.administrator:
            return await prs.edit(content="**Sorry but i can not do this with a role with admin perms.**")
        if ctx.author.top_role.position <= role.position:
            return await prs.edit(content="You Can't Manage This Role")

        if utils.get(ctx.guild.members, id=self.bot.user.id).top_role.position < role.position:
            return await prs.edit(content="I can't manage This role")

        if len(ctx.guild.members) != ctx.guild.member_count:
            return await prs.edit(content="**I'm unable to see anyone! i don't know why. please contact support team!**")

        for member in ctx.guild.members:
            if member.bot:
                await member.add_roles(role, reason=f"role all command used by {ctx.author}")
                await sleep(2)
        await prs.edit(content=None, embed=Embed(color=0x000fff, description=f"**{config.tick} | {role.mention} Given To All Bots**"))


    @cmd.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def hide_roles(self, ctx:commands.Context):
        await ctx.defer()
        if ctx.author.bot:return
        msg = await ctx.send(f'{config.loading}** {constants.PROCESSING}**')
        roles = ctx.guild.roles
        for role in roles:
            if role.position < ctx.author.top_role.position:
                    try:await role.edit(hoist=False)
                    except Exception:pass
        await msg.edit(content=f"{config.tick} Done", delete_after=10)


    @cmd.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def unhide_roles(self, ctx:commands.Context, *roles : Role):
        if ctx.author.bot:return
        msg = await ctx.send(f'{config.loading}** {constants.PROCESSING}**')
        for role in roles:
            if role.position < ctx.author.top_role.position:
                try:await role.edit(hoist=True)
                except Exception:pass
        await msg.edit(content=f"{config.tick} Done", delete_after=10)