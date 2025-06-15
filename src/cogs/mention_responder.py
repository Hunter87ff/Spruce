import discord
from discord.ext import commands
import asyncio
import os
import random
import re
import google.generativeai as genai

# Load Gemini API key from environment
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class MentionResponseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self.bot.user in message.mentions:
            content = message.content.replace(f"<@{self.bot.user.id}>", "").replace(f"<@!{self.bot.user.id}>", "").strip()

            # Bot mentioned without message
            if not content:
                await self.send_greeting(message)
                return

            # Bot mentioned with a message → Use Gemini AI
            await message.channel.typing()
            try:
                is_hindi = self.is_hindi(content)
                prompt = self.build_prompt(content, message.author.name, is_hindi)
                response = await asyncio.to_thread(self.model.generate_content, prompt)
                await message.reply(self.styled_reply(response.text.strip(), is_hindi))
            except Exception as e:
                await message.reply(
                    f"Hey {message.author.mention}, I'm Spruce 🌲\n"
                    f"My prefix is **`{self.bot.config.PREFIX}`** — try `/help` or `{self.bot.config.PREFIX}help`\n"
                    f"*Gemini AI isn't responding right now. Please try again later!*"
                )
                print(f"[Gemini Error]: {e}")

    @commands.hybrid_command(name="ask", description="Ask Spruce a question using Gemini AI 🤖")
    async def ask(self, ctx: commands.Context, *, question: str):
        await ctx.defer()
        try:
            is_hindi = self.is_hindi(question)
            prompt = self.build_prompt(question, ctx.author.name, is_hindi)
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            await ctx.reply(self.styled_reply(response.text.strip(), is_hindi))
        except Exception as e:
            await ctx.reply("Sorry, I couldn't process your question right now.")
            print(f"[Slash /ask Error]: {e}")

    def is_hindi(self, text: str) -> bool:
        """Detect if text is likely Hindi based on Unicode."""
        return bool(re.search(r'[\u0900-\u097F]', text))

    def build_prompt(self, user_message: str, username: str, is_hindi: bool) -> str:
        if is_hindi:
            return f"""
तुम Spruce हो, एक Discord बोट जो tournaments, moderation, music, और utilities में मदद करता है।
एक यूज़र {username} ने पूछा: "{user_message}"

सहायता पूर्ण और स्पष्ट उत्तर दो। 400 शब्दों के अंदर रखो।
जैसे कमांड सुझाओ: `{self.bot.config.PREFIX}help`, `/help`, या `/ask`
"""
        else:
            return f"""
You are Spruce, a helpful Discord bot with features like tournaments, moderation, music, and utilities.
User {username} asked: "{user_message}"

Respond clearly and helpfully. Keep it under 400 words.
Suggest commands like `{self.bot.config.PREFIX}help`, `/help`, or `/ask` where relevant.
"""

    def styled_reply(self, text: str, is_hindi: bool = False) -> str:
        prefix = self.bot.config.PREFIX
        if is_hindi:
            return (
                f"{text}\n\n💡 मेरा prefix है `**{prefix}**` — `/help`, `{prefix}help`, या `/ask` आज़माएं!"
            )
        else:
            return (
                f"{text}\n\n💡 My prefix is `**{prefix}**` — try `/help`, `{prefix}help`, or `/ask` to explore commands!"
            )

    async def send_greeting(self, message: discord.Message):
        greetings = [
            f"Hey {message.author.mention}! 👋",
            f"Hi there {message.author.mention}! 😊",
            f"Yo {message.author.mention}! What's up? 😎",
            f"Greetings {message.author.mention}! 🌟",
            f"Spruce here at your service {message.author.mention} 🌲"
        ]
        selected = random.choice(greetings)
        prefix = self.bot.config.PREFIX

        await message.reply(
            f"{selected}\n\n"
            f"✨ My prefix is **`{prefix}`**\n"
            f"🔧 Use `{prefix}help` or `/help` to explore all commands\n"
            f"💬 Want to chat with AI? Try `/ask` to ask me anything!"
        )

async def setup(bot):
    await bot.add_cog(MentionResponseCog(bot))
