"""
A module for managing roles in a Discord server.
    :author: hunter87
    :copyright: (c) 2022-present hunter87.dev@gmail.com
    :license: GPL-3, see LICENSE for more details.
"""
import os
import aiofiles
from asyncio import sleep
from discord.ext import commands
from ext import constants,  color
from discord.ui import View, Button
from discord import  Embed, Role, File, Member, Message, app_commands, Interaction, ButtonStyle
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from modules.bot import Spruce


class RoleCogException(Exception):
    """
    Custom exception for RoleCog.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message




class RoleCog(commands.Cog):
    """
    ## RoleCog Class
    This class contains commands for managing roles in a Discord server.
    """
    def __init__(self, bot:"Spruce"):
        self.bot = bot
        self.DEFAULT_SLEEP = 1
        self.ROLE_HIGHER_THAN_YOU = "{role.mention} Is Higher or Equal To Your Top Role. So I Can't Manage It"
        self.ROLE_HIGHER_THAN_ME = "{role.mention} Is Higher or Equal To My Top Role. So I Can't Manage It"


    def check_access(self, user:Member, role:Role):
        """
        Raise an exception if the user does not have permission to manage the role.
        """

        # if suddenly someone remove manage_roles permission from the bot, this will be helpful
        if not user.guild.me.guild_permissions.manage_roles:
            raise RoleCogException(
                "**I don't have permission to manage roles in this server**"
            )
        
        if role.is_default():
            raise RoleCogException(
                "**This is a default role and cannot be managed**"
            )

        if user.id != user.guild.owner.id and user.top_role.position < role.position:
            raise RoleCogException(
                self.ROLE_HIGHER_THAN_YOU.format(role=role)
            )

        if user.guild.me.top_role.position < role.position:
            raise RoleCogException(
                self.ROLE_HIGHER_THAN_ME.format(role=role)
            )
        

    @commands.command(aliases=["croles"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def create_roles(self, ctx:commands.Context, *names:str):
        if ctx.author.bot:
            return
        
        await ctx.send(f"{self.bot.emoji.loading} {constants.PROCESSING}", delete_after=len(names) * self.DEFAULT_SLEEP)

        for role in names:
            await ctx.guild.create_role(name=role, reason=f"Created by {ctx.author}", color=self.bot.color.random())
            await sleep(self.DEFAULT_SLEEP)

        await ctx.send(embed=Embed(description=f"{self.bot.emoji.tick} | All roles created", color=self.bot.color.green))


    @commands.command(aliases=["droles"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def del_roles(self, ctx:commands.Context, *roles : Role):
        if ctx.author.bot:return
        
        msg = await ctx.send(f"{self.bot.emoji.loading} {constants.PROCESSING}")

        for role in roles:
            try:
                self.check_access(ctx.author, role)
            except Exception as e:
                await ctx.send(embed=Embed(
                    description=str(e),
                    color=self.bot.color.red
                ), delete_after=10)
                continue


            await role.delete(reason=f"Role {role.name} has been deleted by {ctx.author}")
            await sleep(self.DEFAULT_SLEEP* 2)  # sleep a bit more to avoid rate limits

        await msg.edit(content=None, embed=Embed(color=self.bot.color.green, description=f"{self.bot.emoji.tick} | Roles Successfully Deleted")) if msg else None



    @commands.command(aliases=["role"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True, send_messages=True)
    async def give_role(self, ctx:commands.Context, role: Role, *members: Member):
        if ctx.author.bot:
            return
        given = []
        try:
            self.check_access(ctx.author, role)

        except Exception as e:
            return await ctx.send(embed=Embed(
                description=str(e),
                color=self.bot.color.red
            ))
        
        if role.permissions.administrator and not ctx.author.guild_permissions.administrator:
            return await ctx.send(embed=Embed(
                description="**Non admin users cannot give admin roles**",
                color=self.bot.color.red
            ))

        if not members and not ctx.message.reference:
            return await ctx.send(embed=Embed(
                description="**Please mention users or reply to a message with users to give them a role**",
                color=self.bot.color.red
            ))
        
        if not members and ctx.message.reference:
            members = ctx.message.reference.resolved.mentions

        if len(members) > 1 and role.permissions.administrator:
            return await ctx.send(embed=Embed(
                description="**I can't give admin role to more than 1 person. at a time**",
                color=self.bot.color.red
            ))

        for user in members:
            if not isinstance(user, Member):
                continue

            await user.add_roles(role)
            given.append(user)
            await sleep(self.DEFAULT_SLEEP)

        base_message:Message

        async def take_back_roles(int_ctx:Interaction):
            try:
                self.check_access(int_ctx.user, role)

            except Exception as e:
                return await int_ctx.response.send_message(
                    embed=Embed(
                        description=str(e),
                        color=self.bot.color.red
                    ),
                    ephemeral=True
                )
            
            if not members:
                return await int_ctx.response.send_message(
                    embed=Embed(
                        description="No members to remove role from.",
                        color=self.bot.color.red
                    )
                )
            
            for member in members:
                await member.remove_roles(role, reason=f"Role reversed by {int_ctx.user}")
                await sleep(1)

            if base_message:
                await base_message.delete()

            await int_ctx.response.send_message(
                embed=Embed(
                    description=f"Role {role.mention} removed from {len(members)} members.",
                    color=self.bot.base_color
                )
            )
        
        view = View(timeout=20)
        reverse_btn = Button(
            emoji=self.bot.emoji.remove,
            label="Reverse Role",
            style=ButtonStyle.green,
            custom_id="reverse_role"
        )
        reverse_btn.callback = take_back_roles
        view.add_item(reverse_btn)

        embed = Embed(
            title="Role Given",
            description=f"Role {role.mention} given to {len(given)} members.",
            color=self.bot.base_color
        )

        # async def timeout_callback():
        #     reverse_btn.disabled = True
        #     await ctx.send(embed=embed, view=view)

        # view.on_timeout = timeout_callback
        base_message = await ctx.send(embed=embed, view=view, delete_after=20)


    @app_commands.command(description="Remove members from a role")
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_roles=True, send_messages=True)
    @app_commands.describe(role="The role to remove from all members fom", reason="The reason for removing the role")
    async def remove_members(self, interaction: Interaction, role: Role, reason: str = None):
        if interaction.user.bot:
            return
        
        try:
            self.check_access(interaction.user, role)

        except Exception as e:
            return await interaction.response.send_message(
                embed=Embed(
                    description=str(e),
                    color=self.bot.color.red
                ),
                ephemeral=True
            )


        await interaction.response.send_message(f"{self.bot.emoji.loading} | {constants.PROCESSING}", ephemeral=True)

        if reason is None:
            reason = f"{role} removed from everyone by {interaction.user}"

        for member in role.members:
            await member.remove_roles(role, reason=reason)
            await sleep(self.DEFAULT_SLEEP)

        await interaction.followup.send(embed=Embed(
            description=f"**{self.bot.emoji.tick} | {role} Removed from everyone**",
            color=self.bot.color.green
        ), ephemeral=True)



    @app_commands.command(name="inrole", description="Get the list of members in a role ")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(send_messages=True, manage_roles=True)
    @app_commands.describe(role="Mention the role to get member list")
    async def inrole(self, interaction:Interaction, role:Role):
        if interaction.user.bot:return

        elif (len(role.members) == 0):
            return await interaction.response.send_message("No members in this role", ephemeral=True)
        
        msg=""
        for i in role.members:
            msg = msg + f"\n{i.display_name} : <@{i.id}>"
        if len(msg) < 2000:
            emb = Embed(title=f"{role.name}", description=msg, color=color.random(color.cyan))
            await interaction.response.send_message(embed=emb)
        else:
            async with aiofiles.open(file=f"{role.name}-{role.id}-members.txt", mode="w", encoding="utf-8") as f:
                await f.write(msg)
            await interaction.response.send_message(file=File(f"{role.name}-{role.id}-members.txt"))
            os.remove(f"{role.name}-{role.id}-members.txt")
        



    @commands.hybrid_command(with_app_command = True)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def port(self, ctx:commands.Context, role1: Role, role2: Role, reason=None):
        await ctx.defer()
        if ctx.author.bot:return

        try:
            self.check_access(ctx.author, role2)

        except Exception as e:
            return await ctx.send(embed=Embed(
                description=str(e),
                color=self.bot.color.red
            ), delete_after=10)
        
        await ctx.reply("If You're Running this command by mistake! You Can Run `&help ra_role`")

        if reason == None:
            reason = f"{role2.name} added by {ctx.author}"

        msg = await ctx.send(f"**{self.bot.emoji.loading} {constants.PROCESSING}**")

        for member in role1.members:
            await member.add_roles(role2, reason=reason)
            await sleep(self.DEFAULT_SLEEP)

        await msg.edit(content=f"{self.bot.emoji.tick} **Role Added Successfully.**", delete_after=30)



    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def remove_role(self, ctx:commands.Context, role:Role, *users: Member):
        if ctx.author.bot:return

        try:
            self.check_access(ctx.author, role)
        except Exception as e:
            return await ctx.send(embed=Embed(
                description=str(e),
                color=self.bot.color.red
            ), delete_after=10)


        for user in users:
            await user.remove_roles(role, reason=f"Role removed by {ctx.author}")
            await sleep(self.DEFAULT_SLEEP)

        return await ctx.send(f"**{role.name} removed from these members**")



    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def add_roles(self, ctx:commands.Context, user:Member, *roles:Role):
        if ctx.author.bot:return


        for role in roles:
            try:
                self.check_access(ctx.author, role)
            except Exception as e:
                await ctx.send(embed=Embed(
                    description=str(e),
                    color=self.bot.color.red
                ), delete_after=10)
                continue

            await user.add_roles(role)

        return await ctx.message.add_reaction("✅")


    @commands.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @app_commands.describe(role="The role to give to all humans")
    async def role_all_human(self, ctx:commands.Context, role: Role):
        if ctx.author.bot:return
        await ctx.defer()

        if role.permissions.administrator:
            return await ctx.send(embed=Embed(description="**This role has admin permissions and not secure to add to all members !!**"))
        
        try:
            self.check_access(ctx.author, role)
        except Exception as e:
            return await ctx.send(embed=Embed(
                description=str(e),
                color=self.bot.color.red
            ))

        for member in ctx.guild.members:
            if not member.bot:
                await member.add_roles(role, reason=f"role all command used by {ctx.author}")
                await sleep(self.DEFAULT_SLEEP)

        await ctx.send(content=None, embed=Embed(color=self.bot.color.green, description=f"**{self.bot.emoji.tick} | {role.mention} Given To All These Humans**"))


    @commands.hybrid_command(description="Give a role to all bots in the server")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(role="The role to give to all bots")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def role_all_bot(self, ctx:commands.Context, role: Role):
        if ctx.author.bot:return
        await ctx.defer()

        if role.permissions.administrator:
            return await ctx.send(embed=Embed(description="**This role has admin permissions and not secure to add to all bots !!**"))
        
        try:
            self.check_access(ctx.author, role)

        except Exception as e:
            return await ctx.send(embed=Embed(
                description=str(e),
                color=self.bot.color.red
            ))

        for member in ctx.guild.members:
            if not member.bot:
                continue

            await member.add_roles(role, reason=f"role all command used by {ctx.author}")
            await sleep(self.DEFAULT_SLEEP)

        await ctx.send(content=None, embed=Embed(color=self.bot.color.green, description=f"**{self.bot.emoji.tick} | {role.mention} Added To All The Bots**"))


    @commands.hybrid_command(description="Hide all roles from the member list")
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def hide_roles(self, ctx:commands.Context):
        await ctx.defer()
        if ctx.author.bot:return
        msg = await ctx.send(f'{self.bot.emoji.loading}** {constants.PROCESSING}**')

        for role in ctx.guild.roles:
            try:
                self.check_access(ctx.author, role)
                if role.is_default():
                    continue
                await role.edit(hoist=False)

            except Exception as e:
                await ctx.send(embed=Embed(
                    description=str(e),
                    color=self.bot.color.red
                ), delete_after=10)
                continue

            await sleep(self.DEFAULT_SLEEP)


        await msg.edit(content=f"{self.bot.emoji.tick} Done", delete_after=10)


    @commands.command(aliases=["hoist"])
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True, send_messages=True)
    async def unhide_roles(self, ctx:commands.Context, *roles : Role):
        if ctx.author.bot:
            return
        
        msg = await ctx.channel.send(f'{self.bot.emoji.loading}** {constants.PROCESSING}**') if ctx.channel.permissions_for(ctx.me).send_messages else None

        for role in roles:
            try:
                self.check_access(ctx.author, role)
                await role.edit(hoist=True)
                await sleep(self.DEFAULT_SLEEP)

            except Exception as e:
                await ctx.send(embed=Embed(
                    description=str(e),
                    color=self.bot.color.red
                ), delete_after=10)
                continue


        await msg.edit(content=f"{self.bot.emoji.tick} Done", delete_after=10) if msg else None