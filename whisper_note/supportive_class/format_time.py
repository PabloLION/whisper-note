from datetime import datetime


def format_local(time: datetime) -> str:
    return time.strftime("%H:%M:%S:%f")[:-3]  # milliseconds
