"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022-present hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""


import time
_start=time.time()
import asyncio
import traceback
from dotenv import load_dotenv
from core.bot import Spruce

load_dotenv()

async def launch():
    try:
        bot = Spruce()
        await bot.start(_start)
        
    except Exception as e:
        print("\n".join(traceback.format_exception(type(e), e, e.__traceback__)))

asyncio.run(launch())
