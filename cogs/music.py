import discord
import wavelink
from wavelink.ext import spotify
from time import gmtime
from time import strftime
from discord.ui import Button, View
from discord import ButtonStyle
from discord.ext import commands


cmd = commands
class Music(commands.Cog):
	def __init__(self, bot):
		self.bot = bot





	@commands.Cog.listener()
	async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.YouTubeTrack, reason):
	    try:
	        ctx = player.ctx
	        vc: player = ctx.voice_client
	        
	    except discord.HTTPException:
	        interaction = player.interaction
	        vc: player = interaction.guild.voice_client
	    
	    if vc.loop:
	        return await vc.play(track)
	    
	    if vc.queue.is_empty:
	        return
	        #return await vc.disconnect()

	    next_song = vc.queue.get()
	    await vc.play(next_song)
	    tm = "%H:%M:%S"
	    if next_song.duration < 3599:
	        tm = "%M:%S"
	    next_song_emb = discord.Embed(title=next_song.title, url=next_song.uri, color=0x303136, description=f'Duration : {strftime(tm, gmtime(next_song.duration))}\n').set_thumbnail(url=next_song.thumbnail)
	    try:
	        await ctx.send(embed=next_song_emb)

	    except discord.HTTPException:
	        await interaction.send(embed=next_song_emb)








	@cmd.command(aliases=["p", "P"])
	async def play(self, ctx: commands.Context, *, search: wavelink.YouTubeTrack):

	    next_btn = Button(emoji="<:Skip:1019218793597243462>", custom_id="next_btn")
	    pause_btn = Button(emoji="<:Pause:1019217055712559195>", custom_id="pause_btn")
	    stop_btn = Button(emoji="<:WhiteButton:1019218566475681863>", style=ButtonStyle.danger, custom_id="stop_btn")
	    queue_btn = Button(emoji="<:_playlist:1019219174070951967>", style=ButtonStyle.blurple, custom_id="queue_btn")
	    play_btn = Button(emoji="<:play_btn:1019504469299441674>", custom_id="play_btn")

	    btns = [next_btn, pause_btn, play_btn, stop_btn, queue_btn]
	    view = View()
	    for btn in btns:
	        view.add_item(btn)

		if not ctx.voice_client:
			try:
				vc: wavelink.Player = await ctx.author.voice.channel.connect(self_deaf=True, reconnect=True, cls=wavelink.Player)#reconnect=True, self_deaf=True,
			except:
				return await ctx.send("Please Join a vc")


		if ctx.voice_client is not None:
			if ctx.author.voice is not None:
				if ctx.voice_client.channel != ctx.author.voice.channel:
					vc : wavelink.Player = await ctx.voice_client.move_to(ctx.author.voice.channel)

	    else:
	        vc: wavelink.Player = ctx.voice_client
	        

	    if vc.queue.is_empty and not vc.is_playing():
	        await vc.play(search)
	        tm = "%H:%M:%S"
	        if search.duration < 3599:
	            tm = "%M:%S"
	        em = discord.Embed(title=search.title, url=search.uri, color=0x303136, description=f'Duration : {strftime(tm, gmtime(search.duration))}\n').set_thumbnail(url=search.thumbnail)
	        await ctx.send(embed=em, view=view)
	                
	    else:
	        await vc.queue.put_wait(search)
	        await ctx.send(f'Added to the queue...', delete_after=5)
	    vc.ctx = ctx

	    try:
	        if vc.loop: return
	    except Exception:
	        setattr(vc, "loop", False)





	@cmd.command()
	async def skip(self, ctx):
	    if ctx.voice_client != None:
	        vc: wavelink.Player = ctx.voice_client

	    if vc.queue.is_empty:
	        return await ctx.send("the queue is empty", ephemeral=True)

	    else:
	        await vc.stop()






	@cmd.command()
	async def pause(self, ctx):
	    if not ctx.author.voice:
	        return await ctx.reply("Please Join VC")

	    if ctx.voice_client != None:
	        vc : wavelink.Player = ctx.voice_client


	        if vc.is_playing:
	            await vc.pause()


	@cmd.command()
	async def resume(self, ctx):
	    if not ctx.author.voice:
	        return await ctx.reply("Please Join VC")

	    if ctx.voice_client != None:
	        vc : wavelink.Player = ctx.voice_client


	        if vc.is_paused:
	            await vc.resume()


	@cmd.command()
	async def queue(self, ctx):
	    if not ctx.voice_client:
	        return await ctx.send("im not even in a vc...")

	    elif not getattr(ctx.author.voice, "channel", None):
	        return await ctx.send("join a voice channel first lol")


	    vc: wavelink.Player = ctx.voice_client
	    if vc.queue.is_empty:
	        return await ctx.send("the queue is empty")
	    em = discord.Embed(title="Queue", color=0x303136)
	    
	    queue = vc.queue.copy()
	    songCount = 0
	    for song in queue:
	        songCount += 1
	        em.add_field(name=f"Song Position {str(songCount)}", value=f"`{song}`")
	    await ctx.send(embed=em)






	@cmd.Cog.listener()
	async def on_interaction(self, interaction):
	    ctx = await self.bot.get_context(interaction.message)

	    if interaction.data["custom_id"] == "stop_btn":
	        if ctx.voice_client != None:
	            try:
	                await ctx.voice_client.disconnect()
	                await interaction.response.send_message("Successfully Disconnected", ephemeral=True)
	            except:
	                return 
	        else:
	            await interaction.response.send_message("I'm Not in a vc", ephemeral=True)


	    if interaction.data["custom_id"] == "next_btn":
	            if ctx.voice_client != None:
	                vc: wavelink.Player = ctx.voice_client
	                #player = bot.wavelink.get_player(ctx.guild.id)

	            if vc.queue.is_empty:
	                return await interaction.response.send_message("the queue is empty", ephemeral=True)

	            else:
	                await interaction.response.send_message("Skiping...")
	                await ctx.channel.purge(limit=1)
	                await vc.stop()



	    if interaction.data["custom_id"] == "queue_btn":
	        if not ctx.voice_client:
	            return await interaction.response.send_message("im not even in a vc...", ephemeral=True)

	        elif ctx.author.voice == None:
	            return await interaction.response.send_message("join a voice channel first lol", ephemeral=True)


	        vc: wavelink.Player = ctx.voice_client
	        if vc.queue.is_empty:
	            return await interaction.response.send_message("the queue is empty", ephemeral=True)
	        em = discord.Embed(title="Queue", color=0x303136)
	        
	        queue = vc.queue.copy()
	        songCount = 0
	        for song in queue:
	            songCount += 1
	            em.add_field(name=f"Song Position {str(songCount)}", value=f"`{song}`")
	        await interaction.response.send_message(embed=em, ephemeral=True)
	        
	        
	    if interaction.data["custom_id"] == "pause_btn":
	        if not ctx.author.voice:
	            return await ctx.reply("Please Join VC")
	            
	        if ctx.voice_client != None:
	            vc : wavelink.Player = ctx.voice_client

	            if vc.is_playing:
	                await vc.pause()
	                return await interaction.response.send_message("Paused", ephemeral=True)


	    if interaction.data["custom_id"] == "play_btn":
	        if not ctx.author.voice:
	            return await ctx.reply("Please Join VC")
	            
	        if ctx.voice_client != None:
	            vc : wavelink.Player = ctx.voice_client

	            if vc.is_paused:
	                await vc.resume()
	                return await interaction.response.send_message("Resumed", ephemeral=True)



	@cmd.command()
	async def join(self, ctx):
		if ctx.author.voice == None:
			return await ctx.reply("Please Join VC")

		if not ctx.voice_client:
			try:
				await ctx.author.voice.channel.connect(reconnect=True)
			except:
				return await ctx.reply("Please Join VC")



	@cmd.command()
	async def leave(self, ctx):
		if ctx.author.voice == None:
			return await ctx.reply("Please Join VC")

		if ctx.voice_client:
			return await ctx.voice_client.disconnect()

		if not ctx.voice_client:
			return await ctx.reply("I'm Not Connected To Vc")



















async def setup(bot):
    await bot.add_cog(Music(bot))