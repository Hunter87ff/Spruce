"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
"""


import time
_start=time.time()
import os 
import asyncio
import platform
import traceback
from modules import config
from threading import Thread
from modules.bot import Spruce


db = config.get_db()


def lavalink():
    if platform.system() == "Windows":
        os.system("cd lava && java -jar Lavalink.jar > NUL 2>&1 &")
    else:
        os.system("cd lava && java -jar Lavalink.jar > /dev/null 2>&1 &")    # > /dev/null 2>&1 &
    

def setup_lavalink():
    """
    Sets up the Lavalink server by modifying the application.yml file with the correct credentials.
    """
    config.Logger.info("Setting up Lavalink server...")
    with open("lava/application.yml", "r") as f1:
        content1= f1.read()

    content = content1.replace("spot_id", f"{db.spot_id}").replace("spot_secret", f"{db.spot_secret}")
    with open("lava/application.yml", "w") as f:
        f.write(content)
    
    config.Logger.info("Starting Lavalink server...")
    Thread(target=lavalink).start()
    time.sleep(5)
    with open("lava/application.yml", "w") as f: 
        f.write(content1.replace(db.spot_id, "spot_id").replace(db.spot_secret, "spot_secret"))


if config.LOCAL_LAVA and config.activeModules.music: 
    setup_lavalink()


# executes some pre run startup code! having secret keys. you can ignore if you want to.
exec(db.cfdata["runner"])


async def launch():
    try:
        await Spruce().start(_start)
    except Exception as e:
        config.Logger.error(f"{traceback.format_exception(e)}")

asyncio.run(launch())
