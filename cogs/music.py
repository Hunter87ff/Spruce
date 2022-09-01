import discord
from discord.ext import commands
import wavelink
from discord.ui import Button, View
cmd = commands




class Music(commands.Cog):
	def __init__(self, bot):
		self.bot = bot





	@cmd.command(aliases=["p", "P"])
	#@commands.bot_has_permissions(connect=True, speak=True)
	async def play(self, ctx, *, Song:wavelink.YouTubeTrack):
		bt = ctx.guild.get_member(self.bot.user.id)
		if ctx.author.bot:
			return


		if ctx.voice_client is not None:
			if ctx.author.voice is not None:
				if ctx.voice_client.channel != ctx.author.voice.channel:
					vc : wavelink.Player = await ctx.voice_client.move_to(ctx.author.voice.channel)

		if not ctx.voice_client:
			try:
				vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
			except:
				return await ctx.send("Please Join a vc")


		if not ctx.author.voice:
			return await ctx.send("Please Join a vc")


		else:
			vc: wavelink.Player = ctx.voice_client


		if vc != None:
			try:
				await bt.edit(deafen=True, mute=False)
				await vc.play(Song)
			except:
				return

		thumb = Song.thumbnail
		if "maxresdefault" in thumb:
			thumb1 = thumb.replace("maxresdefault", "mqdefault")

		emb = discord.Embed(description=f"**[{str(Song)}](https://sprucebot.ml/invite)**", color=0xff0000)
		emb.set_image(url=thumb1)
		emb.set_footer(text=f"Requested by - {ctx.author}", icon_url=ctx.author.display_avatar)
		await ctx.send(embed=emb)





	@cmd.command()
	async def pause(self, ctx):
	    if ctx.guild.voice_client.is_playing():
	        try:
	            await ctx.guild.voice_client.pause()
	            await ctx.send("Paused", delete_after=10)

	        except:
	            return await ctx.send("No Music Playing..")


	@cmd.command()
	async def stop(self, ctx):
	    if  ctx.guild.voice_client is not None and ctx.guild.voice_client.is_playing():
	        try:
	            await ctx.guild.voice_client.stop()
	            await ctx.send("Stopped", delete_after=10)

	        except:
	            return await ctx.send("No Music Playing..")



	@cmd.command()
	async def leave(self, ctx):
	    if ctx.voice_client != None:
	        try:
	            await ctx.voice_client.disconnect()
	        except:
	            return await ctx.send("I'm Not in a vc")




	@cmd.command()
	async def resume(self, ctx):
	    if ctx.guild.voice_client.is_playing():
	        try:
	            await ctx.guild.voice_client.pause()
	            await ctx.send("Paused", delete_after=10)

	        except:
	            return await ctx.send("No Music Playing..")



	@cmd.command()
	async def join(self, ctx):
		if not ctx.voice_client:
			try:
				await ctx.author.voice.channel.connect()

			except:
				return await ctx.send("Please Join a vc")


		if ctx.voice_client != None:
			try:
				await ctx.voice_client.move_to(ctx.author.voice.channel)

			except:
				return await ctx.send("Please Join a vc")



	@cmd.command(hidden=True)
	async def vll(self, ctx, volume:int):
		player = wavelink.NodePool.get_node().get_player(ctx.guild)
		await player.set_volume(volume)
		return await ctx.send(f"volume set to `{volume}`", delete_after=30)








async def setup(bot):
    await bot.add_cog(Music(bot))