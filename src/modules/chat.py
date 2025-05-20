"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
 """
import traceback
from requests import post
from typing import TYPE_CHECKING
from discord import Message, File
from discord.ext import commands
import google.generativeai as genai
from ext import constants, db
from collections import defaultdict

if TYPE_CHECKING:
    from modules.bot import Spruce

class ChatClient:
    """
    An advanced AI chatbot client that uses Gemini API with contextual memory per user.
    """
    def __init__(self, bot: 'Spruce') -> None:
        self.bot = bot
        self.db: db.Database = bot.db
        self.sessions = defaultdict(lambda: None)  # user_id -> session
        self.histories = defaultdict(lambda: [])  # user_id -> history list

        generation_config = {
            "temperature": 1.2,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

        try:
            genai.configure(api_key=self.db.GEMAPI)
            self.model = genai.GenerativeModel(
                model_name="gemini-2.0-pro",  # advanced model
                generation_config=generation_config
            )
        except Exception as e:
            post(url=self.db.cfdata.get("dml", ""), json={"content": f"Gemini Init Failed: ```py\n{e}\n```"})

    def _is_valid(self, query: str) -> bool:
        """Block message with bad words."""
        if not query: return False
        query_words = set(query.lower().split())
        return not bool(set(self.db.bws or []).intersection(query_words))

    def _should_respond(self, ctx: commands.Context, message: Message) -> bool:
        """Check if the bot should respond to a given message."""
        if ctx.author.bot:
            return False
        if not message.guild:
            return True
        if message.reference and getattr(message.reference.resolved, "author", None) and message.reference.resolved.author.id == self.bot.user.id:
            return True
        return False

    def _get_or_create_session(self, user_id: int):
        """Ensure a dedicated session with history per user."""
        if self.sessions[user_id] is None:
            self.sessions[user_id] = self.model.start_chat(history=self.histories[user_id])
        return self.sessions[user_id]

    def _reset_user_session(self, user_id: int):
        """Reset session after too much history."""
        self.histories[user_id] = []
        self.sessions[user_id] = self.model.start_chat(history=[])

    async def chat(self, message: Message):
        try:
            ctx = await self.bot.get_context(message)
            if not self._should_respond(ctx, message):
                return

            await ctx.typing()
            user_id = message.author.id

            # Maintain recent history
            messages = [m async for m in ctx.channel.history(limit=16)][::-1]
            for m in messages:
                role = "user" if not m.author.bot else "model"
                self.histories[user_id].append({"role": role, "parts": [m.content]})

            # Reset if too long
            if len(self.histories[user_id]) > 30:
                self._reset_user_session(user_id)

            session = self._get_or_create_session(user_id)
            prompt = message.content.replace(f"<@{self.bot.user.id}>", "").strip()

            if not prompt:
                response = "You mentioned me, but I didn't catch any question. Could you try again?"
            elif not self._is_valid(prompt):
                response = "⚠️ Your message contains blocked or inappropriate words."
            else:
                response = session.send_message(prompt).text

            if len(response) > 1900:
                with open("ai_reply.txt", "w", encoding="utf-8") as f:
                    f.write(response)
                await message.reply(file=File("ai_reply.txt"))
            else:
                await message.reply(response)

        except Exception as e:
            error_report = traceback.format_exc()
            post(url=self.db.cfdata.get("dml", ""), json={"content": f"{message.author.mention}```py\n{error_report}\n```"})

            