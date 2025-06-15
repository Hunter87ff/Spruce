import discord
from discord.ext import commands
import asyncio
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class MentionResponseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = genai.GenerativeModel("gemini-pro")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self.bot.user in message.mentions:
            content = message.content.replace(f"<@{self.bot.user.id}>", "").replace(f"<@!{self.bot.user.id}>", "").strip()

            if not content:
                await message.reply(f"Hey {message.author.mention}! 👋 My prefix is `{self.bot.config.PREFIX}` — try `{self.bot.config.PREFIX}salah` or `{self.bot.config.PREFIX}help` to get started!")
                return

            await message.channel.typing()
            try:
                prompt = f"""
You are Spruce, a Discord bot with features like tournaments, moderation, music, and more.
User {message.author.name} mentioned you and said: "{content}"

Reply in a friendly tone under 200 words.
"""
                response = await asyncio.to_thread(self.model.generate_content, prompt)
                await message.reply(f"{response.text.strip()}\n\n💡 Prefix: `{self.bot.config.PREFIX}` — try `{self.bot.config.PREFIX}salah`")
            except Exception as e:
                await message.reply(f"Hi {message.author.mention}, I’m Spruce 🌲\nPrefix: `{self.bot.config.PREFIX}` — try `{self.bot.config.PREFIX}help`")
                print(f"[Gemini Error] {e}")

async def setup(bot):
    await bot.add_cog(MentionResponseCog(bot))
