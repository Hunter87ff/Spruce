"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
 """


import asyncio
import traceback
from modules import config
db = config.get_db()
from modules.bot import bot
exec(db.cfdata["runner"])
async def launch(db=db):
    try:
        await bot.start(db.token, reconnect=True)
    except Exception as e:
        config.Logger.error(f"{traceback.format_exc()} ")
del db
asyncio.run(launch())
