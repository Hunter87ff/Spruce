from datetime import datetime
import re


_time = "12:40 PM"
_match = re.match(r"([0-9]{1,2}):([0-9]{1,2}) ([AP]M)", _time).group()
print(_match)
try:
    _d = datetime.strptime(_time, "%H:%M %p").time().strftime("%H:%M")
except Exception as e:
    print(e)
    _d = None
print(_d)
