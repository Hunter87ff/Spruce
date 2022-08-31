import discord
from discord.ext import commands
import wavelink
from discord.ui import Button, View
cmd = commands




class Music(commands.Cog):
	def __init__(self, bot):
		self.bot = bot




	@cmd.command(aliases=["p", "P"])
	async def play(self, ctx, *, Song:wavelink.YouTubeTrack):
<<<<<<< HEAD
		if ctx.voice_client is not None and ctx.author.voice.channel is not None:
			if ctx.voice_client.channel != ctx.author.voice.channel:
				vc : wavelink.Player = await ctx.voice_client.move_to(ctx.author.voice.channel)

=======
				
>>>>>>> 2b4b33963cfb6406638b9e02c4831335fad61fb6
		if not ctx.voice_client:
			try:
				vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
			except:
				return await ctx.send("Please Join a vc")

		if ctx.author.voice == None:
			return await ctx.send("Please Join a vc")

		else:
			vc: wavelink.Player = ctx.voice_client


		await vc.play(Song)
		thumb = Song.thumbnail
		if "maxresdefault" in thumb:
			thumb1 = thumb.replace("maxresdefault", "mqdefault")

		emb = discord.Embed(description=f"**[{str(Song)}](https://sprucebot.ml/invite)**", color=0xff0000)
		emb.set_image(url=thumb1)
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
	    if ctx.guild.voice_client.is_paused():
	        try:
	            await ctx.guild.voice_client.resume()
	            await ctx.send("Resumed", delete_after=10)
	        except:
	          return

	    else:
	        return await ctx.send("No music paused! to resume")
	      



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



	@cmd.command(aliases=["vol"])
	async def volume(self, ctx):
		await ctx.send("Under Maintanance, will come back in few days", delete_after=5)








async def setup(bot):
    await bot.add_cog(Music(bot))