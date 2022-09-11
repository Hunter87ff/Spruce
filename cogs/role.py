import discord
from discord.ext import commands
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
		self.counter = 0








	@cmd.command(aliases=['croles'])
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	async def create_roles(self, ctx, *Names):
		for role in Names:
			await ctx.guild.create_role(name=role, reason=f"Created by {ctx.author}")
			await ctx.channel.purge(limit=1)
			await ctx.send(f'**<:vf:947194381172084767> {role} Created by {ctx.author}**', delete_after=5)




	@cmd.command()
	@commands.cooldown(2, 20, commands.BucketType.user)
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True, send_messages=True)
	async def del_roles(self, ctx, *roles : discord.Role):
		for role in roles:
			if ctx.author.top_role < role:
				return await ctx.send("This Role Is Higher Than Your Top Role", delete_after=5)
#			elif self.bot.top_role < role:
#				return await ctx.send("This Role Is Higher Than My Top Role", delete_after=5)
			else:
				await role.delete(reason=f"Role {role.name} has been deleted by {ctx.author}")
				await ctx.send(f"Role {role.name} has been deleted by {ctx.author}", delete_after=5)





	@commands.command(aliases=["role"] help="Use this command to give/remove role for someone \nExample : &role  @Male @hunter")
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True, manage_permissions=True, send_messages=True)
	async def give_role(self, ctx, role: discord.Role, *users: discord.Member):
		bt = ctx.guild.get_member(self.bot.user.id)
		if bt.top_role.position < role.position:
			return await ctx.send("My Top Role position Is not higher enough")
		if not ctx.author.top_role.position > role.position:
			return await ctx.send("You can Not manage that role")


		if users != None:
			for user in users:
				if user.top_role.position > ctx.author.position:
					pass

				if bt.top_role.position < user.top_role.position:
					return await ctx.send(f"{user}'s Role Is Higher Than My Top Role! I can not manage him")	

				else:
					await user.add_roles(role)
					await ctx.message.add_reaction("✅")



	@cmd.command()
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(manage_roles=True, manage_permissions=True, send_messages=True)
	async def ra_role(self, ctx, role: discord.Role, reason=None):
		if reason == None:
			reason = f"{role} removed by {ctx.author}"
			
		for member in ctx.guild.members:
			if ctx.author.top_role < member.top_role:
				return await ctx.send("**You don't have enough permission**", delete_after=5)
			if role in member.roles:
				await member.remove_roles(role, reason=reason)
				return await ctx.send("**:white_checck_mark: Role Removed from everyone**")








	@cmd.command()
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True, send_messages=True)
	async def remove_role(self, ctx, role:discord.Role, *user: discord.Member):
		bt = ctx.guild.get_member(self.bot.user.id)
		for user in users:
			if ctx.author.top_role < user.top_role:
				return await ctx.channel.purge(limit=1)
				return await ctx.send("**You don't have enough permission**", delete_after=5)


			if bt.top_role.position < user.top_role.position:
				return await ctx.channel.purge(limit=1)
				return await ctx.send("**I don't have enough permission**", delete_after=5)

			if bt.top_role.position < role.position:
				return await ctx.channel.purge(limit=1)
				return await ctx.send("**I don't have enough permission**", delete_after=5)

			else:
				await user.remove_roles(role, reason=f"Role removed by {ctx.author}")
				return await ctx.send(f"**{role.name} removed from {user}**")



	@commands.command(aliases=['roles'], help="Use this command to give role to multiple \nExample : &role  @Male @hunter @alex ")
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True, send_messages=True)
	async def give_roles(self, ctx, user: discord.Member, *roles: discord.Role):
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


















async def setup(bot):
    await bot.add_cog(Roles(bot))
