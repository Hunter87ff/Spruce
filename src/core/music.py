"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
 """

from typing import cast
from time import gmtime, strftime
from modules import config
from discord.ext import commands
from discord import ButtonStyle, Interaction, Embed, Message
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
        self.message:Message  = None
        self.loop:bool = False

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:return
        track: wavelink.Playable = payload.track
        tm = "%H:%M:%S"
        if track.length//1000 < 3599:
            tm = "%M:%S"
        embed = Embed(
            title=f"{config.music_disk} Now Playing", 
            color=0x303136, description=f'**[{track.title}]({config.invite_url2})**\nDuration : {strftime(tm, gmtime(track.length//1000))}\n').set_thumbnail(url=track.artwork)
        view = View()
        for button in controlButtons:view.add_item(button)
        
        messages:list[Message] = [message async for message in player.home.history(limit=10) if len(message.embeds)!=0 and message.author.id == self.bot.user.id]
        for i in messages:
            if i and i.author.id == self.bot.user.id and i.embeds[0].title == f"{config.music_disk} Now Playing":
                await i.delete() if i else None
        self.message = await player.home.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:return
        elif self.loop:return await player.play(payload.track, volume=100)
        elif not player.queue.is_empty and self.message:return await player.play(player.queue.get(), volume=100)

    @commands.Cog.listener()
    async def on_interaction(self, interaction:Interaction):
        if "custom_id" not in interaction.data or not interaction.data.get("custom_id").startswith("music_"):return
        elif not interaction.user.voice:return await interaction.response.send_message(Embed(description="Please Join VC", color=config.blurple), ephemeral=True)
        ctx:commands.Context = await self.bot.get_context(interaction.message)
        vc:wavelink.Player = cast(wavelink.Player, ctx.voice_client or await interaction.user.voice.channel.connect(self_deaf=True, cls=wavelink.Player))

        if interaction.data["custom_id"] == "music_stop_btn":
            await ctx.voice_client.disconnect()
            await interaction.response.send_message(embed=Embed(description=f"{config.tick} | Successfully Disconnected", color=config.red), ephemeral=True)
            await interaction.message.delete()

        elif interaction.data["custom_id"] == "music_loop_btn":
            await interaction.response.defer(ephemeral=True)
            if not interaction.user.voice:return await ctx.reply(embed=Embed(description="Please Join A Voice Channel To Use This Command", color=0xff0000))
            if not vc.current:return await ctx.reply(embed=Embed(description=f"{config.cross} | No Audio Available For Loop...", color=0xff0000))
            vc.loop = True
            lemb = Embed(title="Loop Music", description=f"{config.tick} | Cuttent Audio'll Play In Loop", color=config.orange)
            await ctx.send(embed=lemb, delete_after=5)

        elif interaction.data["custom_id"] == "music_next_btn":
            if vc.queue.is_empty:return await interaction.response.send_message(embed=Embed(description="the queue is empty"), ephemeral=True)
            await interaction.response.send_message("Skiping...", ephemeral=True)
            await vc.skip(force=True)
            await interaction.delete_original_response()

        elif interaction.data["custom_id"] == "music_queue_btn":
            if vc.queue.is_empty:return await interaction.response.send_message("Queue is empty", ephemeral=True)
            em = Embed(title="Queue", color=config.cyan)
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
    @commands.hybrid_command(with_app_command=True, aliases=["p"])
    @commands.bot_has_guild_permissions(connect=True, speak=True)
    @commands.guild_only()
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        await ctx.defer()
        if not ctx.guild or ctx.author.bot:
          return
        elif "youtube" in query: 
          return await ctx.reply(embed=Embed(description="I'm sorry, but I can't play YouTube links.", color=config.blue), delete_after=10)
        player:wavelink.Player = cast(wavelink.Player, ctx.voice_client)  or await ctx.author.voice.channel.connect(self_deaf=True, cls=wavelink.Player)
        player.autoplay = wavelink.AutoPlayMode.disabled
        tracks: wavelink.Search = await wavelink.Playable.search(query)
        if not tracks: 
          return await ctx.send(embed=Embed(description="Could not find any tracks with that query. Please try again.", color=config.blurple), delete_after=10)
        player.home = ctx.channel
        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            await ctx.send(embed=Embed(description=f"{config.music_disk} Added the playlist **`{tracks.name}`** ({added} songs) to the queue.", color=config.green))
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            if player.current:
              await ctx.send(embed=Embed(description=f"{config.music_disk} Added **`{track}`** to the queue.", color=config.green))
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
        await ctx.send(embed=Embed(description=f"{config.tick} | Nightcore mode enabled.", color=config.green))


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
        await ctx.send(f"{config.tick} | Successfully Disconnected")


    @commands.hybrid_command(with_app_command=True)
    @commands.guild_only()
    @commands.bot_has_guild_permissions(send_messages=True)
    async def queue(self, ctx:commands.Context):
        await ctx.defer()
        if not ctx.voice_client:return await ctx.send("Not Connected to any VC!!")
        elif not ctx.author.voice:return await ctx.send("join a voice channel first!!")
        vc:wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if vc.queue.is_empty:return await ctx.reply("Queue is empty")
        em = Embed(title="Queue", color=config.blurple)
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
        if not tracks: return await ctx.send(embed=Embed(description="Could not find any tracks with that query. Please try again.", color=config.blurple), delete_after=10)
        player.home = ctx.channel
        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            await ctx.send(embed=Embed(description=f"{config.music_disk} Added the playlist **`{tracks.name}`** ({added} songs) to the queue.", color=config.green))
        if not player.playing:await player.play(player.queue.get(), volume=100)
        

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
        
async def setup(bot:commands.Bot):
    await bot.add_cog(Music(bot))
