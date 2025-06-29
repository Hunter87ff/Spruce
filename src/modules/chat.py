"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""
import traceback
from requests import post
import aiofiles
from typing import TYPE_CHECKING
from discord import Message, File
from discord.ext import commands
import google.generativeai as genai
from ext import constants, db

if TYPE_CHECKING:
    from modules.bot import Spruce

class ChatClient:
    """
    A class to chat with user
    """
    def __init__(self, bot:'Spruce') -> None:
        self.bot= bot #Spruce instance
        self.db:db.Database = bot.db
        generation_config = {
            "temperature": 1.5,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 2000
        }

        try:
            genai.configure(api_key=self.db.GEMAPI)
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash", #"gemini-1.5-flash", 
                generation_config=generation_config
            )
            self.chat_session = model.start_chat(history=constants.history)

        except Exception as e:
            self.bot.logger.warning(message=f"Error initializing chat session: {e}")


    def is_bws(self, query:str) -> bool:
        """
        Check if the message contains blocked words such as slang, etc.
        """
        bw = set(query.lower().split())
        if len(set(self.db.blocked_words or []).intersection(bw)) > 0:return True


    def check_send(self, ctx:commands.Context, message:Message, bot:commands.Bot) -> bool|None:
        """return `True` if triggered dm or mentioned in channel, else `None`"""
        if ctx.author.bot:return None
        elif not message.guild:return True
        elif not message.reference or not message.reference.resolved:return False
        elif message.reference.resolved.author.id == bot.user.id:return True
        return None
    

    async def chat(self, message:Message):
        """
        Chat with user
        """
        try:
            ctx = await self.bot.get_context(message)
            if not self.check_send(ctx, message, self.bot):return
            await ctx.typing()

            self.chat_session.history = constants.history
            async for message in ctx.channel.history(limit=16):

                if not message.author.bot:
                    self.chat_session.history.append({"role": "user","parts": [message.content]})

                elif message.author.bot: 
                    self.chat_session.history.append({"role": "model","parts": [message.content]})

            text = message.content.replace(f"<@{self.bot.user.id}>", "").strip()

            # Check if the message is empty after stripping mentions and whitespace
            if not text:
                response = "I noticed you mentioned me, but didn't provide any message. How can I help you today?"
            else:
                response = self.chat_session.send_message(content=text).text

            # if the response is too long, send it as a file
            if len(response) > 2000:
                async with aiofiles.open("response.txt", "w") as f:
                    await f.write(response)
                return await message.reply(file=File("response.txt"))
            else:
                return await message.reply(response)
            
        except Exception as e:
            await self.bot.query_error_log.send(f"Error in chat: {e}")


