"""
MIT License

Copyright (c) 2022 hunter87ff

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from discord import Embed, TextChannel
from discord.ext import commands
from modules import config
gbr = "https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/star_border.gif"




# Raw
ffemb = Embed(title="FREE FIRE", description="**Garena Free Fire is a battle royal game. Played by millions of people. Developed by 111 dots studio and published by Garena. React on the emoji to access this game!**", color=config.blurple)
ffemb.set_thumbnail(url="https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/freefire.png")
bgmiemb = Embed(title="BGMI", description="**Battlegrounds Mobile India(BGMI), Made for players in India. It is an online multiplayer battle royale game developed and published by Krafton. React on the emoji to access this game**", color=config.blurple)
bgmiemb.set_thumbnail(url="https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/bgmi.png")
codemb = Embed(title="CALL OF DUTY", description="**Call Of Duty is a multiplayer online battle royal game, developed by TiMi Studio Group and published by Activision.react on the emoji to access this game**", color=config.blurple)
codemb.set_thumbnail(url="https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/codm.png")
valoemb = Embed(title="VALORANT", description="**Valorant is a multiplayer online battle royal game made for pc, developed and published by Riot Games. react on the emoji to access this game**", color=config.blurple)
valoemb.set_thumbnail(url="https://raw.githubusercontent.com/Hunter87ff/atomic-8/main/Game_roles/valorant.png")
memb = Embed(title="MINECRAFT", description="**Minecraft is a sandbox video game developed by Mojang Studios. The game was created by Markus 'Notch' Persson in the Java programming language**", color=config.blurple)
memb.set_thumbnail(url="https://github.com/Hunter87ff/atomic-8/blob/main/Game_roles/minecraft.jpeg?raw=true")


class Templates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["grole"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(send_messages=True, manage_messages=True)
    @commands.bot_has_permissions(send_messages=True, manage_messages=True)
    async def game_role(self, ctx, channel:TextChannel=None):
        if channel == None:channel = ctx.channel
        await channel.send(embed=ffemb)
        await channel.send(gbr)
        await channel.send(embed=bgmiemb)
        await channel.send(gbr)
        await channel.send(embed=codemb)
        await channel.send(gbr)
        await channel.send(embed=valoemb)
        await channel.send(gbr)
        await channel.send(embed=memb)

async def setup(bot):
    await bot.add_cog(Templates(bot))