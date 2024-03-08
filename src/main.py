"""MIT License

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
SOFTWARE."""


import app, asyncio, discord
from modules import config
from modules.bot import bot
from threading import Thread

async def action():
    config.logger.info(f"Action Triggered")
    await asyncio.sleep(21474)
    headers = {
        "Authorization": f"token {config.gh_api}",
        "Content-Type": "application/vnd.github+json",
    }
    response = config.webpost(config.gh_action, headers=headers, json={"ref": "main"})
    if response.status_code == 204:
        config.webpost(url=config.stwbh, json=f"<@{config.owner_id}>\nSuccessfully Restarted!!")
    else:(f"<@{config.owner_id}>\nException during restart : {response.text}")
def trigger():asyncio.run(action())
Thread(target=trigger).start()

#discord.utils.setup_logging(level=20)

async def launch():await bot.start(config.token)
asyncio.run(launch())
