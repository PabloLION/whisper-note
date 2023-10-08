def convert_bytes(byte_size):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0

    while byte_size >= 1024 and unit_index < len(units) - 1:
        byte_size /= 1024
        unit_index += 1

    # Determine the number of decimal places based on the magnitude of the value
    if byte_size >= 10:
        decimal_places = 0
    elif byte_size >= 1:
        decimal_places = 1
    else:
        decimal_places = 2

    # Format the result as a string with the appropriate unit
    formatted_size = f"{byte_size:.{decimal_places}f}{units[unit_index]}"
    return formatted_size
