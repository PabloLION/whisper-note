import datetime

from whisper_note.supportive_class import format_bytes_str, format_local_time


def test_format_bytes_str():
    assert format_bytes_str(0) == "0.00B"
    assert format_bytes_str(1023) == "1.00KB"
    assert format_bytes_str(1024) == "1.00KB"
    assert format_bytes_str(1024 * 1024) == "1.00MB"
    assert format_bytes_str(1024 * 1024 * 1024) == "1.00GB"
    assert format_bytes_str(1024 * 1024 * 1024 * 1024) == "1.00TB"
    assert format_bytes_str(1024 * 1024 * 1024 * 1024 * 1024) == "1.00PB"
    assert format_bytes_str(123456789) == "118MB"


def test_format_local_time():
    # Test with a time that has milliseconds
    time_with_ms = datetime.datetime(2022, 1, 1, 12, 30, 45, 678000)
    assert format_local_time(time_with_ms) == "12:30:45:678"

    # Test with a time that has no milliseconds
    time_without_ms = datetime.datetime(2022, 1, 1, 12, 30, 45)
    assert format_local_time(time_without_ms) == "12:30:45:000"

    # Test with a time that has microseconds
    time_with_us = datetime.datetime(2022, 1, 1, 12, 30, 45, 678900)
    assert format_local_time(time_with_us) == "12:30:45:678"

    # Test with a time that has nanoseconds
    time_with_ns = datetime.datetime(2022, 1, 1, 12, 30, 45, 678901)
    assert format_local_time(time_with_ns) == "12:30:45:678"

    # Test with a time that has a different format
    time_different_format = datetime.datetime(2022, 1, 1, 12, 30, 45, 678000)
    assert format_local_time(time_different_format) != "12:30:45.678"

    print("All test cases pass")
