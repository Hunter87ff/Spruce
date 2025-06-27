import os
from threading import Thread
from typing import TYPE_CHECKING
import asyncio

if TYPE_CHECKING:
    from modules.bot import Spruce


async def setup_lavalink(bot: "Spruce") -> None:
    
    import platform
    silent = "> NUL 2>&1 &" if platform.system() == "Windows" else "> /dev/null 2>&1 &"

    if not os.path.exists("lava/plugins"):
        os.system("cd lava && mkdir plugins")

        bot.logger.info("Downloading Lavalink plugins...")
        for plugin, url in bot.config.LAVA_PLUGINS.items():
            download = os.system(f"cd lava/plugins && wget {url} {silent}")
            bot.logger.info(f"{plugin} plugin download : {'Success' if download == 0 else 'Failed'}")

    if not os.path.exists("lava/Lavalink.jar"):
        bot.logger.info("Downloading Lavalink jar...")
        os.system(f"cd lava && wget {bot.config.LAVALINK_JAR} -O Lavalink.jar {silent}")

    
    def lavalink_thread():
        bot.logger.info("Lavalink server is starting...")
        os.system(f"cd lava && java -jar Lavalink.jar {silent}")

    await asyncio.sleep(1)  # Give some time for the directory to be created
    thread = Thread(target=lavalink_thread, daemon=True)
    thread.start()

    await asyncio.sleep(5)  # Wait for the thread to start
    await bot.on_lavalink_callback()

