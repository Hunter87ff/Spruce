"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022 hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""


import time
_start=time.time()
import asyncio
import traceback
from modules import config
from modules.bot import Spruce


db = config.get_db()

# executes some pre run startup code! having secret keys. you can ignore if you want to.
exec(db.config_data["runner"])


async def launch():
    try:
        bot = Spruce()
        await bot.start(_start)
        
    except Exception as e:
        bot.logger.error(traceback.format_exception(e))

asyncio.run(launch())
