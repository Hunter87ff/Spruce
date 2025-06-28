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
import wavelink.websocket
from ext.error import update_error_log
from discord import utils, ButtonStyle, Interaction, Embed, Message, TextChannel, Member
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
        self.players : dict[int, wavelink.Player] = {}
        wavelink.websocket.logger.setLevel(100)  # Disable Wavelink's internal logging

        self.controlButtons = [
            Button(emoji=self.bot.emoji.next_btn, custom_id="music_next_btn"),
            Button(emoji=self.bot.emoji.play_btn, custom_id="music_play_btn"),
            Button(emoji=self.bot.emoji.pause_btn, custom_id="music_pause_btn"),
            Button(emoji=self.bot.emoji.stop_btn, style=ButtonStyle.danger, custom_id="music_stop_btn"),
            Button(emoji=self.bot.emoji.queue_btn, style=ButtonStyle.blurple, custom_id="music_queue_btn"),
            # Button(emoji=self.bot.emoji.loop_btn, custom_id="music_loop_btn")
    ]

    async def have_access_to_play(self, user: Member):
        if not user.voice:
            raise Exception("You must be in a voice channel to use this command.")
        
        if not user.voice.channel.permissions_for(user.guild.me).connect:
            raise Exception("I do not have permission to connect to your voice channel.")
        
        if not user.voice.channel.permissions_for(user.guild.me).speak:
            raise Exception("I do not have permission to speak in your voice channel.")
        
        if not user.guild.me.voice or user.guild.me.voice.channel != user.voice.channel:
            await user.voice.channel.connect(cls=wavelink.Player, self_deaf=True)



    @commands.hybrid_command(name="join", aliases=["j"], description="Join a voice channel.")
    async def join(self, ctx: commands.Context) -> None:
        """Join the voice channel of the user who invoked the command."""
        await ctx.defer()
        try:
            await self.have_access_to_play(ctx.author)
            await ctx.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
            await ctx.send(f"Joined <#{ctx.author.voice.channel.id}>.")

        except Exception as e:
            await ctx.send(f"Error: {e}")


    @commands.hybrid_command(name="play", aliases=["p"], description="Play a song.")
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        """Play a song from a search query or URL."""
        await ctx.defer()

        await self.have_access_to_play(ctx.author)
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)  or await ctx.author.voice.channel.connect(self_deaf=True, cls=wavelink.Player)
        tracks: wavelink.Search = await wavelink.Playable.search(query)
        player.home = ctx.channel
        if not tracks:
            await ctx.send("No tracks found for your query.")
            return
        
        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            await ctx.send(embed=Embed(description=f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue.", color=self.bot.color.cyan))

        track: wavelink.Playable = tracks[0]
        if player.playing:
            await player.queue.put_wait(track)
            await ctx.send(f"Added **`{track.title}`** to the queue.")
            return

        if player.paused:
            await player.play(player.current or track)
            return

        await player.play(track)


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


    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        track = payload.track
        player: wavelink.Player = payload.player
        self.players[player.guild.id] = player
        home : TextChannel = player.home
        embed = Embed(
            title=f"{self.bot.emoji.music_disk} Now Playing", 
            color=self.bot.color.cyan, description=f'**[{track.title}]({self.bot.config.INVITE_URL})**\nDuration : <t:{int(utils.utcnow().timestamp() + track.length//1000)}:R>\n').set_thumbnail(url=track.artwork)
        view = View(timeout=60)

        for button in self.controlButtons:
            if button.custom_id == "music_play_btn":
                continue
            view.add_item(button)

        if isinstance(home, TextChannel):
            message = await home.send(embed=embed, view=view)
            player.message = message

        

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        if not payload.player:
            return
        previous_message: Message = payload.player.message

        if isinstance(previous_message, Message):
            try:
                await previous_message.delete()
                payload.player.message = None
                
            except Exception as e:
                self.bot.debug(str(e))

        if payload.player.queue.is_empty:
            await payload.player.disconnect()
            return
        
        next_track = payload.player.queue.get()
        if next_track:
            await payload.player.play(next_track)


    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        self.bot.logger.info(f"Node Connected {payload.node.identifier}")


# add interaction listeners for buttons
    @commands.Cog.listener()
    async def on_interaction(self, interaction: Interaction) -> None:
        if not interaction.guild:
            return
        interaction_id = interaction.data.get("custom_id", "-1")

        if not interaction_id.startswith("music_"):
            return
        
        if interaction_id == "music_next_btn":
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player or not player.connected:
                return await interaction.response.send_message("Not connected to a voice channel.", ephemeral=True)
            
            if not player.queue.is_empty:
                await player.skip(force=True)
                return await interaction.response.send_message("Skipped to the next track.", ephemeral=True)
            
            await player.skip(force=True)
            
        elif interaction_id == "music_pause_btn":
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player or not player.connected:
                return await interaction.response.send_message("Not connected to a voice channel.", ephemeral=True)
            await player.pause(not player.paused)
            # edit the message to reflect the pause/resume state
            if player.paused:
                view = View()
                for button in self.controlButtons:
                    if button.custom_id != "music_pause_btn":
                        view.add_item(button)

                await interaction.message.edit(embed=interaction.message.embeds[0], view=view)
            await interaction.response.defer()
            

        elif interaction_id == "music_play_btn":
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player or not player.connected:
                return await interaction.response.send_message("Not connected to a voice channel.", ephemeral=True)

            if player.paused:
                await player.pause(False)
                
                view = View()
                for button in self.controlButtons:
                    if button.custom_id != "music_play_btn":
                        view.add_item(button)

                await interaction.message.edit(embed=interaction.message.embeds[0], view=view, content="Resumed the playback.")
            await interaction.response.defer()


        elif interaction_id == "music_stop_btn":
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player or not player.connected:
                return await interaction.response.send_message("Not connected to a voice channel.", ephemeral=True)
            await player.stop()
            return await interaction.response.send_message("Stopped the playback.", ephemeral=True)
        

        elif interaction_id == "music_queue_btn":
            player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
            if not player or not player.connected:
                return await interaction.response.send_message("Not connected to a voice channel.", ephemeral=True)
            if player.queue.is_empty:
                return await interaction.response.send_message("Queue is empty.", ephemeral=True)
            queue = player.queue.copy()
            em = Embed(title="Queue", color=self.bot.color.blurple)
            for song in queue:
                em.add_field(name=f"Song Position {str(queue.count)}", value=f"`{song}`")
            return await interaction.response.send_message(embed=em, ephemeral=True)
        
