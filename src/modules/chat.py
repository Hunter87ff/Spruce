import traceback
from datetime import datetime
from requests import post
from typing import TYPE_CHECKING
from discord import Message, File, Interaction, Embed, ButtonStyle
from discord.ext import commands
from discord import app_commands, ui
import google.generativeai as genai
from ext import constants, db

if TYPE_CHECKING:
    from modules.bot import Spruce

# === SET YOUR LOG CHANNEL ID HERE ===
LOG_CHANNEL_ID = 123456789012345678  # Replace with your Discord log channel ID


class ChatClient:
    """
    AI Chat Client per guild with reset confirmation and logging
    """
    def __init__(self, bot: 'Spruce') -> None:
        self.bot = bot
        self.db: db.Database = bot.db
        self.sessions = {}  # {guild_id: ChatSession}

        generation_config = {
            "temperature": 1.5,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 2000
        }

        try:
            genai.configure(api_key=self.db.GEMAPI)
            self.model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                generation_config=generation_config
            )
        except Exception as e:
            post(url=self.db.cfdata["dml"], json={"content": f"```py\n{e}\n```"})

    def _get_or_create_session(self, guild_id: int):
        if guild_id not in self.sessions:
            self.sessions[guild_id] = self.model.start_chat(history=constants.history.copy())
        return self.sessions[guild_id]

    def _reset_session(self, guild_id: int):
        self.sessions[guild_id] = self.model.start_chat(history=constants.history.copy())

    def is_bws(self, query: str) -> bool:
        bw = set(query.lower().split())
        return len(set(self.db.bws or []).intersection(bw)) > 0

    def check_send(self, ctx: commands.Context, message: Message, bot: commands.Bot) -> bool | None:
        if ctx.author.bot:
            return None
        elif not message.guild:
            return True
        elif not message.reference or not message.reference.resolved:
            return False
        elif message.reference.resolved.author.id == bot.user.id:
            return True
        return None

    async def log_to_channel(self, content: str, message: Message = None):
        """Send a log embed message to a dedicated Discord log channel."""
        channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if channel is None:
            print("Log channel not found!")
            return
        
        embed = Embed(title="ChatBot Log", color=0x3498db, timestamp=datetime.utcnow())
        embed.description = content
        
        if message and message.guild:
            embed.add_field(name="Guild", value=message.guild.name, inline=True)
            embed.add_field(name="Guild ID", value=message.guild.id, inline=True)
        if message:
            embed.add_field(name="User", value=str(message.author), inline=True)
            embed.add_field(name="User ID", value=message.author.id, inline=True)
            embed.add_field(name="Message Content", value=message.content or "N/A", inline=False)
        
        await channel.send(embed=embed)

    async def chat(self, message: Message):
        try:
            ctx = await self.bot.get_context(message)
            if not self.check_send(ctx, message, self.bot):
                return

            await ctx.typing()

            session = self._get_or_create_session(message.guild.id if message.guild else message.author.id)
            session.history = constants.history.copy()

            messages = [msg async for msg in ctx.channel.history(limit=16)][::-1]

            for msg in messages:
                role = "user" if not msg.author.bot else "model"
                session.history.append({"role": role, "parts": [msg.content]})

            text = message.content.replace(f"<@{self.bot.user.id}>", "").strip()

            if not text:
                response = "I noticed you mentioned me, but didn't provide any message. How can I help you today?"
            else:
                response = session.send_message(content=text).text

            if len(response) > 2000:
                with open("response.txt", "w") as f:
                    f.write(response)
                await message.reply(file=File("response.txt"))
            else:
                await message.reply(response)

        except Exception as e:
            await self.log_to_channel(f"Exception:\n```{traceback.format_exc()}```", message)


# UI view for reset confirmation
class ResetConfirmView(ui.View):
    def __init__(self, chat_client: ChatClient, guild_id: int, timeout: int = 30):
        super().__init__(timeout=timeout)
        self.chat_client = chat_client
        self.guild_id = guild_id

    @ui.button(label="✅ Confirm Reset", style=ButtonStyle.danger)
    async def confirm(self, interaction: Interaction, button: ui.Button):
        self.chat_client._reset_session(self.guild_id)
        await interaction.response.edit_message(content="🔄 Chat session reset for this server!", view=None)
        # Log reset
        content = f"Chat session reset confirmed.\nGuild: {interaction.guild.name} ({interaction.guild.id})\nBy User: {interaction.user} ({interaction.user.id})"
        await self.chat_client.log_to_channel(content)

    @ui.button(label="❌ Cancel", style=ButtonStyle.secondary)
    async def cancel(self, interaction: Interaction, button: ui.Button):
        await interaction.response.edit_message(content="❎ Reset cancelled.", view=None)


# Slash command to trigger reset
@app_commands.command(name="reset", description="Reset AI chat memory for this server")
async def reset_chat(interaction: Interaction):
    view = ResetConfirmView(interaction.client.chat_client, interaction.guild.id)
    await interaction.response.send_message(
        content="⚠️ Are you sure you want to reset AI memory for this server?",
        view=view,
        ephemeral=True
    )
