import logging
import datetime


class _UtcFormatter(logging.Formatter):
    """A formatter showing the time of each record in UTC."""

    def formatTime(self, record, datefmt=None):
        record_time = datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc)
        if datefmt:
            return record_time.strftime(datefmt)
        return record_time.strftime("%Y-%m-%d %H:%M:%S")


def level_time_utc_msg_formatter():
    """
    Standard output formatting for console and file handlers: level, UTC time of the record, message.
    The time is that of each record (it used to be the time the formatter was created).
    """
    return _UtcFormatter(
        "%(levelname)s | %(asctime)s.%(msecs)03d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def level_time_local_msg_formatter():
    return logging.Formatter(
        "%(levelname)s | %(asctime)s.%(msecs)03d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def msg_only():
    """Output formatting for presentation"""
    return logging.Formatter("%(message)s")
