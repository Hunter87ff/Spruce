#react command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def react(ctx,emoji,message_id):
  channel = ctx.channel
  msg = await channel.fetch_message(message_id)
  await msg.add_reaction(emoji)
