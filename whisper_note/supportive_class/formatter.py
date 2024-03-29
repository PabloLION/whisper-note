from datetime import datetime
from warnings import warn


def format_local_time(time: datetime) -> str:
    """Format given time to "HH:MM:SS:fff" with local timezone."""
    return time.strftime("%H:%M:%S:%f")[:-3]  # milliseconds


def format_filename(s: str) -> str:
    """Replace reserved_chars with "-" for windows compatibility."""
    reserved_chars = r"""<>:""/\|?*"""
    for char in reserved_chars:
        s = s.replace(char, "-")
    return s


def format_bytes_str(byte_size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index, output_size = 0, byte_size

    while output_size >= 1000 and unit_index < len(units) - 1:
        output_size /= 1024
        unit_index += 1

    # Determine the number of decimal places based on the magnitude of the value
    if output_size > 10:
        decimal_places = 0
    elif output_size > 1:
        decimal_places = 2
    else:
        decimal_places = 2
        if output_size < 0.01 and byte_size != 0:
            warn(f"Value {byte_size} too small to be formatted")

    # Format the result as a string with the appropriate unit
    formatted_size = f"{output_size:.{decimal_places}f}{units[unit_index]}"
    return formatted_size
