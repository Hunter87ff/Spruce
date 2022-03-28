import discord
from discord.ext import commands


class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.counter = 0

	#start commands


	@commands.command()
	@commands.has_permissions(administrator=True)
	async def ra_role(self, ctx, role:discord.Role):
		for member in ctx.guild.members:
			if role in member.roles:
				await member.remove_roles(role)
				await ctx.send("Done")
				await member.send(f"{role.name} removed in {ctx.guild.name}")
      	  
      	  



    @commands.command(aliases=['cr, crole'],help="**Use this command to crate roles\nExample: &crole Family**")
    @commands.has_permissions(manage_roles=True)
    async def create_roles(self, ctx, *names):
    	for name in names:
    		await ctx.guild.create_role(name=name)
    		await ctx.send(f"**<:vf:947194381172084767> Role `{name}` has been created**")






def setup(bot):
    bot.add_cog(Moderation(bot))