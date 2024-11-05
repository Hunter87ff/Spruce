"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
 """


import os
import platform
import asyncio
import traceback
from modules import config
if platform.system() == "Windows": os.system("cls")
else: os.system("clear")
db = config.get_db()
from modules.bot import bot
exec(db.cfdata["runner"])
async def launch():
    try:
        await bot.start(bot.db.token, reconnect=True)
    except Exception:
        config.Logger.error(f"{traceback.format_exc()} ")

asyncio.run(launch())