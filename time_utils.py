from datetime import datetime, timezone
from time import gmtime, strftime

def get_current_time():
    utc_dt = datetime.now(timezone.utc).astimezone()
    return utc_dt

def get_begin_unix_time():
    return datetime.fromtimestamp(0).astimezone()

def get_time_stamp(time):
    return time.strftime("%a %b %d %H:%M:%S %Y %z")