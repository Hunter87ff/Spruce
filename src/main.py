"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 souravyt87@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
 """


import asyncio
from modules import config
from modules.bot import bot
exec(config.cfdata["runner"])
async def launch():await bot.start(config.token, reconnect=True)
asyncio.run(launch())
