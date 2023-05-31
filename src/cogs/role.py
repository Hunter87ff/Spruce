import discord
from discord.ext import commands
import asyncio
from modules import config


cmd = commands
blurple = 0x7289da
greyple = 0x99aab5
d_grey = 0x546e7a
d_theme = 0x36393F
l_grey = 0x979c9f
d_red = 0x992d22
red = 0xe74c3c
d_orange = 0xa84300
orange= 0xe67e22
d_gold = 0xc27c0e
gold = 0xf1c40f
magenta = 0xe91e63
purple = 0x9b59b6
d_blue = 0x206694 
blue = 0x3498db
green = 0x2ecc71
d_green = 0x1f8b4c
cyan = 0x1abc9c
d_dcyan = 0x11806a




class Roles(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	
	@cmd.command(aliases=["croles"])
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	async def create_roles(self, ctx, *Names:str):
		if ctx.author.bot:
			return
		if not await config.voted(ctx, bot=self.bot):
			return await config.vtm(ctx)
		for role in Names:
			await ctx.guild.create_role(name=role, reason=f"Created by {ctx.author}")
			await asyncio.sleep(2)
		await ctx.send(embed=discord.Embed(description=f"{config.tick} | All roles created"), delete_after=5)




	@cmd.command(aliases=["droles"])
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	async def del_roles(self, ctx, *roles : discord.Role):
		if ctx.author.bot:
			return
		if not await config.voted(ctx, bot=self.bot):
			return await config.vtm(ctx)
			
		bt = ctx.guild.get_member(self.bot.user.id)
		msg = await ctx.send(f"{config.loading} Processing...")
		for role in roles:
			if ctx.author.top_role.position < role.position:
				return await ctx.send("Role Is Higher Than Your Top Role", delete_after=5)

			elif bt.top_role.position < role.position:
				return await ctx.send("Role Is Higher Than My Top Role", delete_after=5)

			else:
				await role.delete(reason=f"Role {role.name} has been deleted by {ctx.author}")
				await asyncio.sleep(2)
		await msg.edit(content=None, embed=discord.Embed(color=config.cyan, description=f"{config.tick} | Roles Successfully Deleted", delete_after=30))





	@cmd.command(aliases=["role"])
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	async def give_role(self, ctx, role: discord.Role, *users: discord.Member):
		if ctx.author.bot:
			return
		if not await config.voted(ctx, bot=self.bot):
			return await config.vtm(ctx)
			
		ms = await ctx.send("Processing...")
		bt = ctx.guild.get_member(self.bot.user.id)
		given = []
		if bt.top_role.position <= role.position:
			if ms:
				await ms.edit(content="My Top Role position Is not higher enough")
		if not ctx.author.top_role.position >= role.position:
			if ms:
				return await ms.edit(content="You can Not manage that role")

		if users:
			if len(users) >=1 and role.permission.administrator:
				return await ms.edit(content="**I can't give admin role to more than 1 person. at a time**")
			for user in users:
				if user.top_role.position >= ctx.author.top_role.position:
					try:
						await ms.edit(content=f"{user}'s Role Is Higher Than __Your Top Role__! I can not manage him")
					except:
						return

				if bt.top_role.position < user.top_role.position:
					try:
						await ms.edit(content=f"{user}'s Role Is Higher Than __My Top Role__! I can not manage him")
					except:
						return

				else:
					await user.add_roles(role)
					given.append(user)
					await asyncio.sleep(2)

			if ms:
				await ms.edit(content=f"{role.mention} given To {len(given)} Members")

		if not users and ctx.message.reference:
			message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
			for user in ctx.guild.members:
				if user.mention in message.content.split():
					if user.top_role.position >= ctx.author.top_role.position:
						try:
							await ms.edit(content=f"{user}'s Role Is Equal Or Higher Than __Your Top Role__! I can not manage him")
						except:
							return


					if bt.top_role.position <= user.top_role.position:
						try:
							await ms.edit(content=f"{user}'s Role Is Equal Or Higher Than __My Top Role__! I can not manage him")
						except:
							return



					else:
						await user.add_roles(role)
						given.append(user)
						await asyncio.sleep(2)

			if ms:
				await ms.edit(content=f"Role Added To - {len(given)} Members")





	@cmd.command(aliases=["ra_role"])
	@commands.has_permissions(administrator=True)
	@commands.guild_only()
	@commands.bot_has_permissions(manage_roles=True)
	async def remove_role_members(self, ctx, role: discord.Role, reason=None):
		if ctx.author.bot:
			return
		prs = await ctx.send("<a:loading:969894982024568856> Processing...")
		if reason == None:
			reason = f"{role} removed by {ctx.author}"
			
		for member in role.members:
			await member.remove_roles(role, reason=reason)
			await asyncio.sleep(2)
			
		return await prs.edit(content="**:white_check_mark: | Role Removed from everyone**", delete_after=30)



	@cmd.hybrid_command(with_app_command = True)
	@commands.guild_only()
	@commands.bot_has_permissions(manage_roles=True)
	async def inrole(self, ctx, role: discord.Role):
		await ctx.defer()
		if ctx.author.bot:
			return
		if not await config.voted(ctx, bot=self.bot):
			return await config.vtm(ctx)
			
		msg = ""
		if len(role.members) < 15:
			for i in role.members:
				msg = msg + f"\n{i} : {i.id}"
			try:
				await ctx.send(msg)
			except:
				return

		if len(role.members) > 15 and len(role.members) <= 1000000:
			for i in role.members:
				msg = msg + f"\n{i} : {i.id}"
			file = open("members.txt", "w", encoding="utf-8")
			file.write(msg)
			file.close()
			await ctx.send(f"total members : `{len(role.members)}`",file=discord.File("members.txt"))
		if len(role.members) > 1000000:
			try:
				return await ctx.send("Too Many Members To Show!")
			except:
				return


	@cmd.hybrid_command(with_app_command = True)
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	@commands.guild_only()
	async def port(self, ctx, role1: discord.Role, role2: discord.Role, reason=None):
		await ctx.defer()
		if ctx.author.bot:
			return
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
			
		msg = await ctx.send(f"**{config.loading} Processing...**")

		for m in role1.members:
			if m.top_role.position < bt.top_role.position:
				await m.add_roles(role2, reason=reason)
				await asyncio.sleep(1)

		await msg.edit(content=f"{config.vf} **Role Added Successfully.**", delete_after=30)



	@cmd.command()
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	@commands.guild_only()
	async def remove_role(self, ctx, role:discord.Role, *users: discord.Member):
		if ctx.author.bot:
			return
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
	@commands.bot_has_permissions(manage_roles=True)
	async def add_roles(self, ctx, user:discord.Member, * roles:discord.Role):
		if ctx.author.bot:
			return
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

			else:
				await user.add_roles(role)

		return await ctx.message.add_reaction("✅")






	@cmd.hybrid_command(with_app_command = True)
	@commands.guild_only()
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	async def role_all_human(self, ctx, role: discord.Role):
		if ctx.author.bot:
			return
		await ctx.defer()
		if ctx.author.bot:
			return
		prs = await ctx.send("Processing...")
		if role.permissions.administrator:
			return await prs.edit(content="**Sorry but i can not do this with a role with admin perms.**")
		if ctx.author.top_role.position <= role.position:
			return await prs.edit(content=f"**{config.cross}You Can't Manage This Role | The role should be higher than your top role.**")
	
		if discord.utils.get(ctx.guild.members, id=self.bot.user.id).top_role.position < role.position:
			return await prs.edit(content="I can't manage This role")
		if len(ctx.guild.members) != ctx.guild.member_count:
			return await prs.edit(content="**I'm unable to see anyone! i don't know why. please contact support team!**")
		for member in ctx.guild.members:
			if not member.bot:
				await member.add_roles(role, reason=f"role all command used by {ctx.author}")
				await asyncio.sleep(3)
		await prs.edit(content=None, embed=discord.Embed(color=0x00ff00, description=f"**{config.tick} | {role.mention} Given To All These Humans**"))





	@cmd.hybrid_command(with_app_command = True)
	@commands.guild_only()
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	async def role_all_bot(self, ctx, role: discord.Role):
		await ctx.defer()
		if ctx.author.bot:
			return
		prs = await ctx.send("Processing...")
		if role.permissions.administrator:
			return await prs.edit(content="**Sorry but i can not do this with a role with admin perms.**")
		if ctx.author.top_role.position <= role.position:
			return await prs.edit(content="You Can't Manage This Role")
	
		if discord.utils.get(ctx.guild.members, id=self.bot.user.id).top_role.position < role.position:
			return await prs.edit(content="I can't manage This role")

		if len(ctx.guild.members) != ctx.guild.member_count:
			return await prs.edit(content="**I'm unable to see anyone! i don't know why. please contact support team!**")

		for member in ctx.guild.members:
			if member.bot:
				await member.add_roles(role, reason=f"role all command used by {ctx.author}")
				await asyncio.sleep(3)
		await prs.edit(content=None, embed=discord.Embed(color=0x000fff, description=f"**{config.tick} | {role.mention} Given To All Bots**"))





	@cmd.hybrid_command(with_app_command = True)
	@commands.guild_only()
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	async def hide_roles(self, ctx):
		await ctx.defer()
		if ctx.author.bot:
			return
		msg = await ctx.send(f'{config.loading}** Processing..**')
		roles = ctx.guild.roles
		for role in roles:
		    if role.position < ctx.author.top_role.position:
		            try:
		                await role.edit(hoist=False)
		            except:
		                pass
		await msg.edit(content=f"{config.vf} Done", delete_after=10)




	@cmd.command()
	@commands.guild_only()
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	async def unhide_roles(self, ctx, *roles : discord.Role):
		if ctx.author.bot:
			return
		msg = await ctx.send(f'{config.loading}** Processing..**')
		for role in roles:
		    if role.position < ctx.author.top_role.position:
		        try:
		            await role.edit(hoist=True)
		        except:
		            pass
		await msg.edit(content=f"{config.vf} Done", delete_after=10)











async def setup(bot):
    await bot.add_cog(Roles(bot))
