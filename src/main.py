
import app, os
from modules import config
from modules.bot import bot


app.keep_alive()
bot.remove_command("help")
bot.run(config.token)
