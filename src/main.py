try:
  import app, os
  from modules import config
  from modules.bot import bot
except:
    os.system("pip install -r requirements.txt")

app.keep_alive()
bot.remove_command("help")
bot.run(config.token)
