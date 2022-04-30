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









	@cmd.command(aliases=['Croles'])
	@commands.has_permissions(manage_roles=True)
	async def create_roles(self, ctx, *Names):
		for role in roles:
			await ctx.guild.create_roles(role, reason=f"Created by {ctx.author}")
			await ctx.channel.purge(limit=1)
			await ctx.send(f'**<:vf:947194381172084767> {role} Created by {ctx.author}**', delete_after=5)




	@cmd.command()
	@commands.cooldown(2, 20, commands.BucketType.user)
	@commands.has_permissions(manage_roles=True)
	async def del_roles(self, ctx, role : discord.Role):
		await ctx.guild.delete_roles(role, reason=f"Role {role.name} has been deleted by {ctx.author}")
		await ctx.send(f"Role {role.name} has been deleted by {ctx.author}", delete_after=5)





	@commands.command(aliases=['role'], help="Use this command to give role to someone \nExample : &role  @Male @hunter")
	@commands.has_permissions(manage_roles=True)
	async def role_give(self, ctx, role: discord.Role, user: discord.Member):
		if ctx.author.top_role < role:
			return await ctx.send("you don't have enough permission", delete_after=5)
		if ctx.author.top_role > role:
			return await user.add_roles(role)
			await ctx.message.add_reaction("✅")
		else:
			return await ctx.send("Something went wrong", delete_after=5)





	@commands.command( help="Use to remove a role from everyone")
	@commands.has_permissions(administrator=True)
	async def ra_role(self, ctx, role:discord.Role):
		for member in ctx.guild.members:
			if role in member.roles:
				if member.top_role < ctx.author.top_role:
					return await member.remove_roles(role)
					return await member.send(f"**A role named `{role.name}` removed from you in `{ctx.guild.name}`**")
					return await ctx.send("Done", delete_after=5)

				if member.top_role > ctx.author.top_role:
					return await ctx.send("You don't have enough permission", delete_after=5)

				else:
					return await ctx.send("Something went wrong", delete_after=5)



	@cmd.command()
	@commands.has_permissions(manage_roles=True)
	async def remove_role(ctx, role:discord.Role, user: discord.Member):
		if ctx.author.top_role < user.top_role:
			return await ctx.channel.purge(limit=1)
			return await ctx.send("**You don't have enough permission**", delete_after=5)


		if self.bot.top_role < user.top_role:
			return await ctx.channel.purge(limit=1)
			return await ctx.send("**You don't have enough permission**", delete_after=5)


		else:
			return await user.remove_roles(role, reason=f"Role removed by {ctx.author}")
			return await ctx.send(f"**{role.name} removed from {user}**")



	@commands.command(aliases=['roles'], help="Use this command to give role to multiple \nExample : &role  @Male @hunter @alex ")
	@commands.has_permissions(manage_roles=True)
	async def give_roles(self, ctx, role: discord.Role, *users: discord.Member):
		for user in users:

			if ctx.author.top_role < role:
				return await ctx.send("you don't have enough permission", delete_after=5)
			if ctx.author.top_role > role:
				return await user.add_roles(role)
				await ctx.message.add_reaction("✅")
			else:
				return await ctx.send("Something went wrong", delete_after=5)

















def setup(bot):
    bot.add_cog(Roles(bot))
