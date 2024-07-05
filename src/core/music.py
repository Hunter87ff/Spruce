from typing import cast
from time import gmtime, strftime
from modules import config
from discord.ext import commands
from discord import ButtonStyle, Interaction, Embed
from discord.ui import Button, View
import wavelink

controlButtons = [
        Button(emoji=config.next_btn, custom_id="music_next_btn"),
        Button(emoji=config.pause_btn, custom_id="music_pause_btn"),
        Button(emoji=config.stop_btn, style=ButtonStyle.danger, custom_id="music_stop_btn"),
        Button(emoji=config.queue_btn, style=ButtonStyle.blurple, custom_id="music_queue_btn"),
        Button(emoji=config.play_btn, custom_id="music_play_btn"),
        Button(emoji=config.loop_btn, custom_id="music_loop_btn")
]

class Music(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot:commands.Bot = bot

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self):
        return config.logger.info("Node Connected")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:return
        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track
        # print(track.title, track.artwork, track.length, track.source, track.uri)
        tm = "%H:%M:%S"
        if track.length//1000 < 3599:tm = "%M:%S"
        embed = Embed(title="<a:music_disk:1020370054665207888>   Now Playing", color=0x303136, description=f'**[{track.title}](https://discord.com/oauth2/authorize?client_id=931202912888164474&permissions=8&redirect_uri=https%3A%2F%2Fdiscord.gg%2FvMnhpAyFZm&response_type=code&scope=bot%20identify)**\nDuration : {strftime(tm, gmtime(track.length//1000))}\n').set_thumbnail(url=track.artwork)
        view = View()
        for button in controlButtons:view.add_item(button)
        # if track.artwork:embed.set_image(url=track.artwork)
        # if original and original.recommended:embed.description += f"\n\n`This track was recommended via {track.source}`"
        # if track.album.name:embed.add_field(name="Album", value=track.album.name)
        await player.home.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:return
        # track: wavelink.Playable = payload.track
        if not player.queue.is_empty: await player.play(player.queue.get(), volume=30)
        else:await player.disconnect()

    @commands.Cog.listener()
    async def on_interaction(self, interaction:Interaction):
        if "custom_id" not in interaction.data:return
        elif not interaction.data["custom_id"].startswith("music_"):return
        elif not interaction.user.voice:return await interaction.response.send_message("Please Join VC", ephemeral=True)
        if interaction.message: ctx:commands.Context = await self.bot.get_context(interaction.message)
        if not ctx.voice_client: return await interaction.response.send_message("I'm Not Connected To Vc!!", ephemeral=True)
        if ctx.voice_client: vc:wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if interaction.data["custom_id"] == "music_stop_btn":
            try:
                await ctx.voice_client.disconnect()
                await interaction.response.send_message("Successfully Disconnected", ephemeral=True)
                await interaction.message.delete()
            except:pass

        elif interaction.data["custom_id"] == "music_loop_btn":
            await interaction.response.defer(ephemeral=True)
            if interaction.user.voice != None:
                if not vc.current:return await ctx.reply(embed=Embed(description="No Audio Available For Loop...", color=0xff0000))
                else:
                    vc.loop = True
                    lemb = Embed(title="Loop Music", description=f"✅ Cuttent Audio'll Play In Loop", color=config.orange)
                    await ctx.send(embed=lemb, delete_after=5)

            if interaction.user.voice == None:
                em = Embed(description="Please Join A Voice Channel To Use This Command", color=0xff0000)
                await ctx.reply(embed=em)

        elif interaction.data["custom_id"] == "music_next_btn":
            if vc.queue.is_empty:return await interaction.response.send_message(embed=Embed(description="the queue is empty"), ephemeral=True)
            else:
                await interaction.response.send_message("Skiping...", ephemeral=True)
                vc.loop = False
                await vc.skip()
                await interaction.message.delete()

        elif interaction.data["custom_id"] == "music_queue_btn":
            if vc.queue.is_empty:return await interaction.response.send_message("Queue is empty", ephemeral=True)
            em = Embed(title="Queue", color=0x303136)
            queue = vc.queue.copy()
            songCount = 0
            for song in queue:
                songCount += 1
                em.add_field(name=f"Song Position {str(songCount)}", value=f"`{song}`")
            await interaction.response.send_message(embed=em, ephemeral=True)
            
        elif interaction.data["custom_id"] == "music_pause_btn":
            if not vc.current:return await interaction.response.send_message("No audio is playing", ephemeral=True)
            if vc.current:
                await vc.pause(True)
                return await interaction.response.send_message("Paused", ephemeral=True)

        elif interaction.data["custom_id"] == "music_play_btn":
            if vc.current:return await interaction.response.send_message("Already playing", ephemeral=True)
            if vc.paused:
                await vc.pause(False)
                return await interaction.response.send_message("Resumed", ephemeral=True)

    @commands.hybrid_command(with_app_command=True, alliases=["p"])
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        if not ctx.guild:return
        player: wavelink.Player
        player:wavelink.Player = cast(wavelink.Player, ctx.voice_client)  # type: ignore
        if not player:
            try: player = await ctx.author.voice.channel.connect(cls=wavelink.Player)  
            except:return await ctx.send("Something went wrong. Please try again.")
        player.autoplay = wavelink.AutoPlayMode.disabled

        tracks: wavelink.Search = await wavelink.Playable.search(query)
        if not tracks: return await ctx.send(f"{ctx.author.mention} - Could not find any tracks with that query. Please try again.")
        player.home = ctx.channel
        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            await ctx.send(f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue.")
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            if player.current:await ctx.send(f"Added **`{track}`** to the queue.")
        if not player.playing:await player.play(player.queue.get(), volume=30)

    @commands.hybrid_command(with_app_command=True)
    async def skip(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:return
        await player.skip(force=True)
        await ctx.message.add_reaction("\u2705")

    @commands.hybrid_command(with_app_command=True, disabled=True)
    async def nightcore(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:return
        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=1.2, speed=1.2, rate=1)
        await player.set_filters(filters)
        await ctx.message.add_reaction("\u2705")

    @commands.hybrid_command(with_app_command=True, name="toggle", aliases=["pause", "resume"])
    async def pause_resume(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:return
        await player.pause(not player.paused)
        await ctx.message.add_reaction("\u2705")

    @commands.hybrid_command(with_app_command=True)
    async def volume(self, ctx: commands.Context, value: int) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player: return
        await player.set_volume(value)
        await ctx.message.add_reaction("\u2705")

    @commands.hybrid_command(with_app_command=True, aliases=["stop"])
    async def disconnect(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:return
        await player.disconnect()
        await ctx.message.add_reaction("\u2705")

    @commands.hybrid_command(with_app_command=True)
    async def queue(self, ctx:commands.Context):
        await ctx.defer()
        if not ctx.voice_client:return await ctx.send("Not Connected to any VC!!")
        elif not ctx.author.voice:return await ctx.send("join a voice channel first!!")
        vc:wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if vc.queue.is_empty:return await ctx.reply("Queue is empty")
        em = Embed(title="Queue", color=config.blurple)
        queue = vc.queue.copy()
        songCount = 0
        for song in queue:
            songCount += 1
            em.add_field(name=f"Song Position {str(songCount)}", value=f"`{song}`")
        await ctx.send(embed=em)

    @commands.hybrid_command(with_app_command=True)
    async def spotify(self, ctx:commands.Context, playlist_url:str):
        if not ctx.guild:return
        player:wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            try: player = await ctx.author.voice.channel.connect(cls=wavelink.Player)  
            except AttributeError:return await ctx.send("Please join a voice channel first before using this command.")
        playlist :wavelink.Playlist = playlist_url
        if playlist:
            await player.queue.put_wait(playlist)
            await ctx.send(f"Added the playlist **`{playlist.name}`** to the queue.")
            if not player.playing:await player.play(player.queue.get(), volume=30)
        

    @commands.hybrid_command(with_app_command=True, aliases= ['connect'])
    async def join(self, ctx:commands.Context):
        await ctx.defer()
        if ctx.author.voice == None:return await ctx.reply("Please Join VC", delete_after=10)
        if ctx.voice_client: return await ctx.reply("I'm Already Connected To VC", delete_after=10)
        else:
            try:
                await ctx.author.voice.channel.connect(cls=wavelink.Player)
                await ctx.reply("Connected To VC", delete_after=10)
            except:await ctx.reply("I'm Unable To Join VC", delete_after=10)
        
async def setup(bot:commands.Bot):
    await bot.add_cog(Music(bot))