@commands.command()
@commands.has_permissions(administrator=True)
@commands.cooldown(2, 43200, commands.BucketType.guild)
async def rdm(ctx, role: discord.Role,*, msg):
  for member in ctx.guild.members:
    if role in member.roles:
      await ctx.channel.purge(limit=1)
      await member.send(msg)
      await ctx.send('**Sent**')




@commands.command()
@commands.has_permissions(administrator=True)
async def remove_role(self, ctx, role:discord.Role):
  for member in ctx.guild.members:
    if role in member.roles:
      await member.remove_roles(role)
      await ctx.send("Done")
      await member.send(f"{role.name} removed in {ctx.guild.name}")