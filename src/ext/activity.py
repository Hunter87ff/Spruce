from typing import TYPE_CHECKING
from discord.activity import ActivityType
from discord import Activity

if TYPE_CHECKING:
    from core.bot import Spruce



class Activities:
    def __init__(self, bot : "Spruce") -> None:
        self.bot = bot

        if not self.bot.is_ready():
            return

        self.LISTENING = Activity(type=ActivityType.listening, name="&help")
        self.PLAYING = Activity(type=ActivityType.playing, name="Daily Scrims")
        self.COMPETING = Activity(type=ActivityType.competing, name="League Tournaments")
        self.STREAMING = Activity(type=ActivityType.streaming, name="Autoroles")
        self.WATCHING = Activity(type=ActivityType.watching, name="Tickets")

        self.activities = [
            self.LISTENING,
            self.PLAYING,
            self.COMPETING,
            self.STREAMING,
            self.WATCHING
        ]
        self.current_activity = 0
        self.bot.loop.create_task(self.update_activity())


    def get_activity(self):
        if self.current_activity >= len(self.activities):
            self.current_activity = 0

        activity = self.activities[self.current_activity]
        self.current_activity += 1

        return activity
    

    async def update_activity(self):
        activity = self.get_activity()
        if not self.bot.is_ready():
            return
        
        await self.bot.change_presence(activity=activity)
        await self.bot.sleep(30)  # Wait for 10 seconds before changing the activity again
        await self.update_activity()  # Recursively call to keep updating the activity

