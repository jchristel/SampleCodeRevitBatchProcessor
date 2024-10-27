import logging
import datetime


def level_time_utc_msg_formatter():
    """Standard output formatting for console and file handlers"""
    # Format the date and time
    utc_now = datetime.datetime.utcnow()
    return logging.Formatter("%(levelname)s | {} | %(message)s".format(utc_now))


def level_time_local_msg_formatter():
    return logging.Formatter(
        "%(levelname)s | %(asctime)s.%(msecs)03d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def msg_only():
    """Output formatting for presentation"""
    return logging.Formatter("%(message)s")
