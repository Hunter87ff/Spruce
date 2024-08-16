"""
MIT License

Copyright (c) 2022 hunter87ff

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os, time, platform
from threading import Thread
from modules import config
with open("lava/application.yml", "r") as f1:content1= f1.read()
content = content1.replace("spot_id", f"{config.spot_id}").replace("spot_secret", f"{config.spot_secret}")
with open("lava/application.yml", "w") as f: f.write(content)

def lavalink():
    if platform.system() == "Windows":os.system("cd lava && java -jar Lavalink.jar > NUL 2>&1 &")
    else:os.system("cd lava && java -jar Lavalink.jar > /dev/null 2>&1 &")   
Thread(target=lavalink).start()


time.sleep(5)
with open("lava/application.yml", "w") as f: f.write(content1.replace(config.spot_id, "spot_id").replace(config.spot_secret, "spot_secret"))
try:os.system("python src/main.py")
except Exception:os.system("python3 src/main.py")