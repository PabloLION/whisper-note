from datetime import datetime


def format_local_time(time: datetime) -> str:
    return time.strftime("%H:%M:%S:%f")[:-3]  # milliseconds
