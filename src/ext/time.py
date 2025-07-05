"""
This project is licensed under the GNU GPL v3.0.
Copyright (C) 2022-present hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""


import pytz, dateparser
from .constants import TimeZone
from datetime import datetime, timedelta


class ClientTime:
    def __init__(self):
        self.timezone = pytz.timezone(TimeZone.Asia_Kolkata.value)
        self.all_zones = pytz.all_timezones
        

    def now(self, tz=TimeZone.Asia_Kolkata.value) -> datetime:
        """Returns the current time in the specified timezone.
        Args:
            tz (str, optional): The timezone to use. Defaults is `Asia/Kolkata`, which uses the instance's timezone.
        Returns:
            datetime: The current time in the specified timezone.
        """
        return datetime.now(tz)
    
    
    def is_valid_tz(self, tz: str) -> bool:
        """
        Checks if the given timezone is valid.
        Args:
            tz (str): The timezone to check.
        Returns:
            bool: True if the timezone is valid, False otherwise.
        """
        return tz in self.all_zones


    @staticmethod
    def now(tz=TimeZone.Asia_Kolkata.value) -> datetime:
        """Returns the current time in the specified timezone."""
        return datetime.now(tz=pytz.timezone(tz))


    def by_seconds(self, seconds:int):
        """return the largest time unit and its value from the given seconds."""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minutes"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hours"
        else:
            days = seconds // 86400
            return f"{days} days"


    def scrim_format(self, _time=None) -> str:
        """Returns the scrim time in the format 'HH:MM AM/PM'."""
        return (_time or self.now()).strftime("%H-%M").strip()



    def parse_timestamp(self, timestamp: int | float, tz: str) -> datetime:
        """
        Parses a timestamp into a datetime object in the specified timezone.
        Args:
            timestamp (float): The timestamp to parse.
            tz (str): The timezone to use for parsing.
        Returns:
            datetime: The parsed datetime object in the specified timezone.

        Raises:
            ValueError: If the timestamp cannot be parsed in the specified timezone.
        """
        if not isinstance(timestamp, (int, float)):
            raise ValueError("Timestamp must be an integer or float.")
        
        try:
            local_tz = pytz.timezone(tz)
            return datetime.fromtimestamp(timestamp, local_tz)
        
        except Exception as e:
            raise ValueError(f"Unable to parse timestamp {timestamp} in timezone {tz}: {e}")
        

    def parse_datetime(self, time_str: str|datetime, tz: str) -> datetime:
        """
        Parses a time string into a datetime object in the specified timezone.
        Args:
            time_str (str): The time string to parse, e.g., "11 PM".
            tz (str): The timezone to use for parsing. Default is "Asia/Kolkata".
        Returns:
            datetime: The parsed datetime object, adjusted to the specified timezone.
        Raises:
            ValueError: If the time string cannot be parsed.
        """
        try:
            if isinstance(time_str, datetime):
                time_str =  time_str.strftime("%H:%M")
                    
            parsed_datetime = dateparser.parse(
                time_str, 
                
                settings={
                    'TIMEZONE': tz,
                    'PREFER_DATES_FROM': 'current_period',
                    'RETURN_AS_TIMEZONE_AWARE': True,
                    'TO_TIMEZONE': tz,
                    }
                )
            # Ensure parsed_datetime is not None
            if parsed_datetime is None:
                raise ValueError(f"Unable to parse {time_str}. Please provide a valid time in a valid format.")
            
            # If the parsed datetime is in the past, add a day to it
            if parsed_datetime < datetime.now(pytz.timezone(tz)):
                parsed_datetime += timedelta(days=1)

            return parsed_datetime
        
        except Exception as e:
            raise ValueError(str(e))

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

