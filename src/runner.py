"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
"""
import os, time, platform
if platform.system() == "Windows": os.system("cls")
else: os.system("clear")
from threading import Thread
from modules import config

db = config.get_db()
def lavalink():
    if platform.system() == "Windows":os.system("cd lava && java -jar Lavalink.jar > NUL 2>&1 &")
    else:os.system("cd lava && java -jar Lavalink.jar > /dev/null 2>&1 &")    # > /dev/null 2>&1 &
    
if config.LOCAL_LAVA : 
    with open("lava/application.yml", "r") as f1:content1= f1.read()
    content = content1.replace("spot_id", f"{db.spot_id}").replace("spot_secret", f"{db.spot_secret}")
    with open("lava/application.yml", "w") as f: f.write(content)
    Thread(target=lavalink).start()
    time.sleep(5)
    with open("lava/application.yml", "w") as f: f.write(content1.replace(db.spot_id, "spot_id").replace(db.spot_secret, "spot_secret"))


import main