"""
A module for  managing music playback using Lavalink in Spruce.
    :author: hunter87
    :copyright: (c) 2022-present hunter87.dev@gmail.com
    :license: GPL-3, see LICENSE for more details.
"""

import asyncio
import wavelink,time, os, platform
from threading import Thread
from typing import cast, TYPE_CHECKING
from time import gmtime, strftime
from discord.ext import commands
from ext.error import update_error_log
from discord import ButtonStyle, Interaction, Embed, Message, TextChannel
from discord.ui import Button, View

if TYPE_CHECKING:
    from modules.bot import Spruce




class MusicCog(commands.Cog):
    """
    Music commands for the bot.
    
    NOTE: For some issues, we've removed this cog from the bot for a while.
    """

    def __init__(self, bot:"Spruce") -> None:
        self.bot = bot
        self.message:Message  = None
        self.loop:bool = False
        self.bot.loop.create_task(self.setup_lava_node())
        self.lava_server_configured = False

        self.controlButtons = [
            Button(emoji=self.bot.emoji.next_btn, custom_id="music_next_btn"),
            Button(emoji=self.bot.emoji.pause_btn, custom_id="music_pause_btn"),
            Button(emoji=self.bot.emoji.stop_btn, style=ButtonStyle.danger, custom_id="music_stop_btn"),
            Button(emoji=self.bot.emoji.queue_btn, style=ButtonStyle.blurple, custom_id="music_queue_btn"),
            Button(emoji=self.bot.emoji.play_btn, custom_id="music_play_btn"),
            Button(emoji=self.bot.emoji.loop_btn, custom_id="music_loop_btn")
    ]


    async def setup_lava_node(self):

        def lavalink():
            if not os.path.exists("lava"):
                os.mkdir("lava")

            if not os.path.exists("lava/application.yml"):
                self.bot.logger.error("unable to setup lavalink, application.yml not found")
                raise FileNotFoundError("application.yml not found in lava directory")
            
            if not os.path.exists("lava/Lavalink.jar"):
                downloaded = os.system("cd lava && wget {link} -O Lavalink.jar".format(link=self.bot.config.LAVALINK_JAR))
                if downloaded != 0:
                    self.bot.logger.error("Failed to download Lavalink.jar")
                return
            
            self.lava_server_configured = True
            if platform.system() == "Windows":
                os.system("cd lava && java -jar Lavalink.jar > NUL 2>&1 &")
            else:
                os.system("cd lava && java -jar Lavalink.jar > /dev/null 2>&1 &")


        async def setup_lavalink():
            """
            Sets up the Lavalink server by modifying the application.yml file with the correct credentials.
            """
            try:
                import aiofiles
                self.bot.logger.info("Setting up Lavalink server...")
                async with aiofiles.open("lava/application.yml", "r") as f1:
                    content1= await f1.read()

                content = content1.replace("spot_id", f"{self.bot.config.SPOTIFY_CLIENT_ID}").replace("spot_secret", f"{self.bot.config.SPOTIFY_CLIENT_SECRET}")
                async with aiofiles.open("lava/application.yml", "w") as f:
                    await f.write(content)

                self.bot.logger.info("Starting Lavalink server...")
                Thread(target=lavalink).start()
                await asyncio.sleep(5)

                async with aiofiles.open("lava/application.yml", "w") as f:
                    await f.write(content1.replace(self.bot.config.SPOTIFY_CLIENT_ID, "spot_id").replace(self.bot.config.SPOTIFY_CLIENT_SECRET, "spot_secret"))

                if not self.lava_server_configured:
                    raise RuntimeError("Lavalink server not configured properly, please check application.yml file")
                
                _nodes = [wavelink.Node(uri=self.bot.config.LOCAL_LAVA[0], password=self.bot.config.LOCAL_LAVA[1])]
                await wavelink.Pool.connect(nodes=_nodes, client=self.bot, cache_capacity=None)
                self.bot.logger.info("Lavalink server connected")

            except Exception as e:
                    self.bot.logger.error(f"Attempting to connect to Lavalink server failed\n {e}")


        await setup_lavalink()


    # @commands.Cog.listener()
    # async def on_ready(self):
    #     _nodes = [wavelink.Node(uri=self.bot.config.LOCAL_LAVA[0], password=self.bot.config.LOCAL_LAVA[1])]
    #     await wavelink.Pool.connect(nodes=_nodes, client=self.bot, cache_capacity=None)



    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        home: TextChannel = player.home if player else None
        if not player:return
        track: wavelink.Playable = payload.track
        tm = "%H:%M:%S"
        if track.length//1000 < 3599:
            tm = "%M:%S"
        embed = Embed(
            title=f"{self.bot.emoji.music_disk} Now Playing", 
            color=0x303136, description=f'**[{track.title}]({self.bot.config.INVITE_URL})**\nDuration : {strftime(tm, gmtime(track.length//1000))}\n').set_thumbnail(url=track.artwork)
        view = View()
        for button in self.controlButtons:view.add_item(button)
        try:
            messages:list[Message] = [message async for message in home.history(limit=10) if len(message.embeds)!=0 and message.author.id == self.bot.user.id]
            for i in messages:
                if i and i.author.id == self.bot.user.id and i.embeds[0].title == f"{self.bot.emoji.music_disk} Now Playing":
                    await i.delete() if i else None
        except Exception as e:
            update_error_log(f"{e}")
        if self.message and home:
            _home : TextChannel = home
            await _home.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:return
        elif self.loop:return await player.play(payload.track, volume=100)
        elif not player.queue.is_empty and self.message:return await player.play(player.queue.get(), volume=100)

    @commands.Cog.listener()
    async def on_interaction(self, interaction:Interaction):
        if "custom_id" not in interaction.data or not interaction.data.get("custom_id").startswith("music_"):return
        elif not interaction.user.voice:return await interaction.response.send_message(Embed(description="Please Join VC", color=self.bot.color.blurple), ephemeral=True)
        ctx:commands.Context = await self.bot.get_context(interaction.message)
        vc:wavelink.Player = cast(wavelink.Player, ctx.voice_client or await interaction.user.voice.channel.connect(self_deaf=True, cls=wavelink.Player))

        if interaction.data["custom_id"] == "music_stop_btn":
            await ctx.voice_client.disconnect()
            await interaction.response.send_message(embed=Embed(description=f"{self.bot.emoji.tick} | Successfully Disconnected", color=self.bot.color.red), ephemeral=True)
            await interaction.message.delete()

        elif interaction.data["custom_id"] == "music_loop_btn":
            await interaction.response.defer(ephemeral=True)
            if not interaction.user.voice:return await ctx.reply(embed=Embed(description="Please Join A Voice Channel To Use This Command", color=0xff0000))
            if not vc.current:return await ctx.reply(embed=Embed(description=f"{self.bot.emoji.cross} | No Audio Available For Loop...", color=0xff0000))
            vc.loop = True
            lemb = Embed(title="Loop Music", description=f"{self.bot.emoji.tick} | Cuttent Audio'll Play In Loop", color=self.bot.color.orange)
            await ctx.send(embed=lemb, delete_after=5)

        elif interaction.data["custom_id"] == "music_next_btn":
            if vc.queue.is_empty:return await interaction.response.send_message(embed=Embed(description="the queue is empty"), ephemeral=True)
            await interaction.response.send_message("Skiping...", ephemeral=True)
            await vc.skip(force=True)
            await interaction.delete_original_response()

        elif interaction.data["custom_id"] == "music_queue_btn":
            if vc.queue.is_empty:return await interaction.response.send_message("Queue is empty", ephemeral=True)
            em = Embed(title="Queue", color=self.bot.base_color)
            queue = vc.queue.copy()
            for song in queue:
                em.add_field(name=f"Song Position {str(queue.count)}", value=f"`{song}`")
            await interaction.response.send_message(embed=em, ephemeral=True)
            
        elif interaction.data["custom_id"] == "music_pause_btn":
            if vc.paused:return await interaction.response.send_message("No audio is playing", ephemeral=True)
            await interaction.response.send_message("Paused", ephemeral=True)
            await vc.pause(True)
            await interaction.delete_original_response()
                

        elif interaction.data["custom_id"] == "music_play_btn":
            if not vc.paused:return await interaction.response.send_message("Already playing", ephemeral=True)
            await interaction.response.send_message("Resumed", ephemeral=True)
            await vc.pause(False)
            await interaction.delete_original_response()

    #fixes needed -> player.channel !
    @commands.command(aliases=["p"])
    @commands.bot_has_guild_permissions(connect=True, speak=True)
    @commands.guild_only()
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        await ctx.defer()
        if not ctx.guild or ctx.author.bot:
          return
        elif "youtube" in query: 
          return await ctx.reply(embed=Embed(description="I'm sorry, but I can't play YouTube links.", color=self.bot.color.blue), delete_after=10)
        player:wavelink.Player = cast(wavelink.Player, ctx.voice_client)  or await ctx.author.voice.channel.connect(self_deaf=True, cls=wavelink.Player)
        player.autoplay = wavelink.AutoPlayMode.disabled
        tracks: wavelink.Search = await wavelink.Playable.search(query)
        if not tracks: 
          return await ctx.send(embed=Embed(description="Could not find any tracks with that query. Please try again.", color=self.bot.color.blurple), delete_after=10)
        player.home = ctx.channel
        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            await ctx.send(embed=Embed(description=f"{self.bot.emoji.music_disk} Added the playlist **`{tracks.name}`** ({added} songs) to the queue.", color=self.bot.color.green))
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            if player.current:
              await ctx.send(embed=Embed(description=f"{self.bot.emoji.music_disk} Added **`{track}`** to the queue.", color=self.bot.color.green))
        if not player.playing:
          await player.play(player.queue.get(), volume=100)



    @commands.hybrid_command(with_app_command=True)
    @commands.guild_only()
    async def skip(self, ctx: commands.Context) -> None:
        await ctx.defer()
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:return
        await player.skip(force=True)
        await ctx.message.add_reaction("\u2705")


    @commands.hybrid_command(with_app_command=True)
    @commands.guild_only()
    async def nightcore(self, ctx: commands.Context) -> None:
        await ctx.defer()
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:return
        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=1.2, speed=1.2, rate=1)
        await player.set_filters(filters)
        await ctx.message.add_reaction("\u2705")
        await ctx.send(embed=Embed(description=f"{self.bot.emoji.tick} | Nightcore mode enabled.", color=self.bot.color.green))


    @commands.hybrid_command(with_app_command=True)
    @commands.guild_only()
    async def speed(self, ctx: commands.Context, value: float) -> None:
        await ctx.defer()
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:return
        filters: wavelink.Filters = player.filters
        value = max(0.5, min(value, 2.0))
        filters.timescale.set(speed=value)
        await player.set_filters(filters)
        await ctx.message.add_reaction("\u2705")
        await ctx.send(f"Speed changed to : {value}")



    @commands.hybrid_command(with_app_command=True, description="Change the pitch of the current track. 1 is default")
    @commands.guild_only()
    async def pitch(self, ctx: commands.Context, value: float) -> None:
        await ctx.defer()
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:return
        filters: wavelink.Filters = player.filters
        value = max(0.5, min(value, 2.0))
        filters.timescale.set(pitch=value)
        await player.set_filters(filters)
        await ctx.message.add_reaction("\u2705")
        await ctx.send(f"Pitch changed to : {value}")


    @commands.hybrid_command(with_app_command=True, name="toggle", aliases=["pause", "resume"], description="Pause or resume the current track.")
    @commands.guild_only()
    async def pause_resume(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:return
        await player.pause(not player.paused)
        await ctx.message.add_reaction("\u2705")
        await ctx.send(f"{'Paused' if player.paused else 'Resumed'} the track.")


    @commands.hybrid_command(with_app_command=True, aliases=["vol"])
    @commands.guild_only()
    @commands.bot_has_guild_permissions(connect=True, speak=True)
    async def volume(self, ctx: commands.Context, value: int) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player: return
        value = max(1, min(value, 200))
        await player.set_volume(value)
        await ctx.message.add_reaction("\u2705")
        await ctx.send(f"Volume changed to : {value}")


    @commands.hybrid_command(with_app_command=True, aliases=["stop", "leave"])
    @commands.guild_only()
    async def disconnect(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:return
        await player.disconnect()
        await ctx.message.add_reaction("\u2705")
        await ctx.send(f"{self.bot.emoji.tick} | Successfully Disconnected")


    @commands.hybrid_command(with_app_command=True)
    @commands.guild_only()
    @commands.bot_has_guild_permissions(send_messages=True)
    async def queue(self, ctx:commands.Context):
        await ctx.defer()
        if not ctx.voice_client:return await ctx.send("Not Connected to any VC!!")
        elif not ctx.author.voice:return await ctx.send("join a voice channel first!!")
        vc:wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if vc.queue.is_empty:return await ctx.reply("Queue is empty")
        em = Embed(title="Queue", color=self.bot.color.blurple)
        queue = vc.queue.copy()
        for song in queue:
            em.add_field(name=f"Song Position {str(queue.count)}", value=f"`{song}`")
        await ctx.send(embed=em)


    @commands.hybrid_command(with_app_command=True)
    @commands.guild_only()
    @commands.bot_has_guild_permissions(connect=True, speak=True, send_messages=True)
    async def spotify(self, ctx:commands.Context, playlist_url:str):
        tracks: wavelink.Search = await wavelink.Playable.search(playlist_url)
        player:wavelink.Player = cast(wavelink.Player, ctx.voice_client)  or await ctx.author.voice.channel.connect(self_deaf=True, cls=wavelink.Player)
        if not tracks: return await ctx.send(embed=Embed(description="Could not find any tracks with that query. Please try again.", color=self.bot.color.blurple), delete_after=10)
        player.home = ctx.channel
        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            await ctx.send(embed=Embed(description=f"{self.bot.emoji.music_disk} Added the playlist **`{tracks.name}`** ({added} songs) to the queue.", color=self.bot.color.green))
        if not player.playing:
            await player.play(player.queue.get(), volume=100)
        

    @commands.hybrid_command(with_app_command=True, aliases= ['connect'])
    @commands.guild_only()
    @commands.bot_has_guild_permissions(connect=True, speak=True)
    async def join(self, ctx:commands.Context):
        await ctx.defer()
        if ctx.author.voice == None:return await ctx.reply("Please Join VC", delete_after=10)
        if ctx.voice_client: return await ctx.reply("I'm Already Connected To VC", delete_after=10)
        else:
            try:
                await ctx.author.voice.channel.connect(self_deaf=True, cls=wavelink.Player)
                await ctx.reply("Connected To VC", delete_after=10)
            except Exception:await ctx.reply("I'm Unable To Join VC", delete_after=10)
        

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        self.bot.logger.info(f"Node Connected {payload.node.identifier}")
