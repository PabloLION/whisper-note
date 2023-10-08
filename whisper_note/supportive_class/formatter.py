from datetime import datetime


def format_local_time(time: datetime) -> str:
    return time.strftime("%H:%M:%S:%f")[:-3]  # milliseconds


def format_bytes_str(byte_size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index, output_size = 0, byte_size

    while output_size >= 1024 and unit_index < len(units) - 1:
        output_size /= 1024
        unit_index += 1

    # Determine the number of decimal places based on the magnitude of the value
    if output_size >= 10:
        decimal_places = 0
    elif output_size >= 1:
        decimal_places = 1
    else:
        decimal_places = 2

    # Format the result as a string with the appropriate unit
    formatted_size = f"{output_size:.{decimal_places}f}{units[unit_index]}"
    return formatted_size
