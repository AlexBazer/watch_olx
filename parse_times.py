import pytz
import re
from datetime import datetime, timedelta


current_timezone = pytz.timezone('Europe/Kiev')
time_patt = re.compile(r'(вчера|сегодня) ([\d]{1,2}):([\d]{1,2})')


def now():
    return datetime.now(current_timezone).replace(microsecond=0)


datetime_base = {
    'вчера': now() - timedelta(days=1),
    'сегодня': now()
}


def parse(time_str):
    result = re.match(time_patt, time_str.lower())
    if not result:
        return None

    day_part, hour, minute = result.groups()
    return datetime_base[day_part].replace(hour=int(hour), minute=int(minute))
