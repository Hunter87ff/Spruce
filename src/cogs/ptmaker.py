import discord
from discord.ext import commands
import asyncio
import os
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class PTMaker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sessions = {}  # user_id: session dict

    @commands.command(name="creatept", help="Start PT creation for BGMI matches step-by-step.")
    async def create_pt(self, ctx: commands.Context):
        self.sessions[ctx.author.id] = {
            "step": "awaiting_slotlist",
            "slotlist": None,
            "lobby_images": [],
            "result_images": [],
        }
        await ctx.send(f"🗂️ PT Session started for {ctx.author.mention}.\nPlease upload the **slot list** (text or image).")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.author.id not in self.sessions:
            return

        session = self.sessions[message.author.id]
        step = session["step"]

        if step == "awaiting_slotlist":
            if message.attachments:
                session["slotlist"] = message.attachments[0].url
                session["step"] = "awaiting_lobby"
                await message.channel.send("📸 Got slotlist image. Now upload one or more **lobby screenshots** (send `done` when finished).")
            elif message.content:
                session["slotlist"] = message.content
                session["step"] = "awaiting_lobby"
                await message.channel.send("📝 Got slotlist text. Now upload one or more **lobby screenshots** (send `done` when finished).")

        elif step == "awaiting_lobby":
            if message.content.lower() == "done":
                if session["lobby_images"]:
                    session["step"] = "awaiting_result"
                    await message.channel.send("📥 Now upload one or more **result screenshots** (send `done` when finished).")
                else:
                    await message.channel.send("⚠️ Please upload at least one lobby screenshot before sending `done`.")
            elif message.attachments:
                session["lobby_images"].extend([a.url for a in message.attachments])
                await message.channel.send("✅ Lobby screenshot added. Send more or type `done`.")

        elif step == "awaiting_result":
            if message.content.lower() == "done":
                if session["result_images"]:
                    await message.channel.send("🔄 Processing PT...")
                    await self.process_pt(message)
                    del self.sessions[message.author.id]
                else:
                    await message.channel.send("⚠️ Please upload at least one result screenshot before sending `done`.")
            elif message.attachments:
                session["result_images"].extend([a.url for a in message.attachments])
                await message.channel.send("✅ Result screenshot added. Send more or type `done`.")

    async def process_pt(self, message: discord.Message):
        user_id = message.author.id
        session = self.sessions[user_id]

        # Gemini OCR on slotlist (skipped if text)
        slotlist = session["slotlist"]
        if isinstance(slotlist, str) and slotlist.startswith("http"):
            slot_text = await self.extract_text_from_image(slotlist)
        else:
            slot_text = slotlist

        result_text = []
        for img_url in session["result_images"]:
            text = await self.extract_text_from_image(img_url)
            result_text.append(text)

        # Dummy team points (replace with real logic)
        teams = self.extract_teams_from_text(result_text, slot_text)
        image = self.generate_pt_image(teams)
        with io.BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await message.channel.send("🏁 Final PT:", file=discord.File(fp=image_binary, filename='pt_result.png'))

    async def extract_text_from_image(self, image_url: str) -> str:
        try:
            image = Image.open(await self.download_image(image_url))
            response = await asyncio.to_thread(
                genai.GenerativeModel("gemini-2.0-flash").generate_content,
                [image]
            )
            return response.text
        except Exception as e:
            print(f"[OCR Error]: {e}")
            return ""

    async def download_image(self, url: str) -> io.BytesIO:
        async with self.bot.session.get(url) as resp:
            data = await resp.read()
            return io.BytesIO(data)

    def extract_teams_from_text(self, result_texts: list[str], slot_text: str) -> list[dict]:
        # Example dummy logic (replace with real placement/kill extraction)
        return [
            {"team": "Team A", "placement": 15, "kills": 10},
            {"team": "Team B", "placement": 10, "kills": 8},
            {"team": "Team C", "placement": 5, "kills": 12}
        ]

    def generate_pt_image(self, teams: list[dict]) -> Image.Image:
        # Base image
        img = Image.new("RGB", (800, 600), (30, 30, 30))
        draw = ImageDraw.Draw(img)

        # Optional: blur a background image instead of solid color

        # Title
        font = ImageFont.truetype("arial.ttf", 36)
        draw.text((250, 30), "Points Table", fill="white", font=font)

        # Headers
        header_font = ImageFont.truetype("arial.ttf", 24)
        draw.text((50, 100), "Team", fill="white", font=header_font)
        draw.text((300, 100), "Placement", fill="white", font=header_font)
        draw.text((500, 100), "Kills", fill="white", font=header_font)
        draw.text((650, 100), "Total", fill="white", font=header_font)

        # Rows
        row_font = ImageFont.truetype("arial.ttf", 22)
        y = 140
        for team in teams:
            total = team["placement"] + team["kills"]
            draw.text((50, y), team["team"], fill="white", font=row_font)
            draw.text((300, y), str(team["placement"]), fill="white", font=row_font)
            draw.text((500, y), str(team["kills"]), fill="white", font=row_font)
            draw.text((650, y), str(total), fill="white", font=row_font)
            y += 40

        return img


async def setup(bot):
    await bot.add_cog(PTMaker(bot))
    bot.logger.info("PTMaker Cog loaded successfully.")