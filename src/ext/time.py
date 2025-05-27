import pytz, dateparser
from datetime import datetime


class ClientTime:
    def __init__(self):
        self.timezone = pytz.timezone("Asia/Kolkata")
        

    def now(self) -> datetime:
        """Returns the current time in the specified timezone."""
        return datetime.now(self.timezone)



    def scrim_format(self, _time=None) -> str:
        """Returns the scrim time in the format 'HH:MM AM/PM'."""
        return (_time or self.now()).strftime("%H-%M").strip()

    def scrim_time_parse(self, time:str, from_tz:str = 'Asia/Kolkata', to_tz:str = 'Asia/Kolkata'):
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
                }
            )
            ist = pytz.timezone(to_tz)
            parsed_time = parsed_time.astimezone(ist).time().strftime("%H-%M")
            return parsed_time
        
        except Exception:
            return None
        

    def scrim_time_localize(self, time_str: str="18-00", from_tz: str = 'Asia/Kolkata', to_tz: str = 'Asia/Tokyo', format:int=12) -> str:
        """
        Localizes a time string from one timezone to another and returns it in the format "hour-minute".
        Args:
            time_str (str): The time string to be localized, in "HH-MM" format.
            from_tz (str): The timezone of the input time string. Default is 'Asia/Kolkata'.
            to_tz (str): The timezone to convert the time string to. Default is 'Asia/Tokyo'.

        Returns:
            str: The localized time in the format "hour-minute" or None if parsing fails.
        """
        try:
            _time_str = time_str.replace("-", ":")
            parsed_time = dateparser.parse(
                date_string=_time_str, 
                settings={
                    'TIMEZONE': from_tz, 
                    'RETURN_AS_TIMEZONE_AWARE': True
                },
                region="in"
            )
            ist = pytz.timezone(to_tz)
            parsed_time = parsed_time.astimezone(ist).time()

            if format == 12:
                return self.twelve_hour_format(f"{parsed_time.hour}:{parsed_time.minute}")
            
            return f"{parsed_time.hour}:{parsed_time.minute}"

        except Exception:
            return None
        

    def twelve_hour_format(self, time_str: str) -> str:
        """
        Converts a 24-hour time string to a 12-hour format.
        Args:
            time_str (str): The 24-hour time string to convert.

        Returns:
            str: The converted 12-hour time string.
        """
        try:
            return datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
        
        except ValueError:
            return time_str

