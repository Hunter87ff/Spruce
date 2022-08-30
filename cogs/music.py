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
	    #tracks = await wavelink.get_tracks(f'ytsearch:{Song}')
	    #await ctx.channel.send(embed=discord.Embed(description=f'Now playing {tracks[0]} .', color=0xfd2121))



	@cmd.command()
	async def pause(self, ctx):
	    if ctx.voice_client != None:
	        try:
	            await ctx.voice_client.pause()
	            await ctx.message.delete()
	            await ctx.send("Paused", delete_after=10)
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
	    if ctx.voice_client != None:
	        try:
	            await ctx.voice_client.resume()
	            await ctx.message.delete()
	            await ctx.send("Resumed", delete_after=10)
	        except:
	            return await ctx.send("No Music Paused..")















async def setup(bot):
    await bot.add_cog(Music(bot))