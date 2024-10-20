import logging


def get_standard_formatter():
    """Standard output formatting for console and file handlers"""
    return logging.Formatter(
        "%(levelname)s | %(asctime)s.%(msecs)03d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_presentation_formatter():
    """Output formatting for presentation"""
    return logging.Formatter("%(message)s")
