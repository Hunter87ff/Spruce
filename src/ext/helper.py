from discord import Interaction
from pytz import timezone
import dateparser
from ext import Database
from discord.ext import commands


def get_db():
    """
    Returns a Database Object
    """
    return Database()


async def is_dev(ctx: commands.Context | Interaction):
    """
    Checks if the user is a developer
    """
    user_id = ctx.user.id if isinstance(ctx, Interaction) else ctx.author.id
    if user_id not in get_db().cfdata["devs"]:
        response = ctx.response.send_message if isinstance(ctx, Interaction) else ctx.send
        await response("Command is under development", ephemeral=True if isinstance(ctx, Interaction) else False)
        return False
    return True
     



def time_parser(time:str, from_tz:str = 'Asia/Kolkata', to_tz:str = 'Asia/Kolkata'):
    """
    Parses a time string from one timezone to another and returns it in the format "hour-minute".
    Args:
        time (str): The time string to be parsed. for example, "12:56 pm".
        from_tz (str): The timezone of the input time string. Default is 'Asia/Kolkata'.
        to_tz (str): The timezone to convert the time string to. Default is 'Asia/Kolkata'.

    Returns:
        str: The converted time in the format "hour-minute" or None if parsing fails.
    """
    try:
        parsed_time = dateparser.parse(
            date_string=time, 
            settings={
                'TIMEZONE': from_tz, 
                'RETURN_AS_TIMEZONE_AWARE': True
            },
            region="in"
        )
        ist = timezone(to_tz)
        parsed_time = parsed_time.astimezone(ist).time()
        return f"{parsed_time.hour}-{parsed_time.minute}"
    
    except Exception:
        return None
    

def get_event_channel_prefix(name:str):
  li = []
  for i in name.split()[0:2]:li.append(i[0])
  return str("".join(li) + "-")