from datetime import datetime, timedelta
import asyncio

tz = "Asia/Kolkata"
_scrimCache = {
    "21:54:50" : [
        "Scrim1", "Scrim2"
    ],
    "21:29:30" : [
        "Scrim3", "Scrim4"
    ]
}

async def callback(scrim, _timedelta:float):
    print(f"Time Delta : {_timedelta}")
    while True:
        if _timedelta > 0:
            await asyncio.sleep(_timedelta)
            break
    print(f"Starting : {scrim}")


def getTimeDelta(target_time_str:str):
    now = datetime.now()
    target_time = datetime.strptime(target_time_str, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day)
    time_delta = target_time - now
    if time_delta.days < 0:
        target_time += timedelta(days=1)
        time_delta = target_time - now
    return time_delta



async def main():
    for s in _scrimCache.keys():
        time_delta = getTimeDelta(s).total_seconds()
        asyncio.create_task(await callback(_scrimCache[s], time_delta))

asyncio.run(main())