import logging


class FilterFile(logging.Filter):
    """
    Filter to stop logs to file handler.

    To use change your log call to something like:
    my_logger.info("This is a console only output", extra={"block": "file"})
    """

    def filter(self, record):
        if "block" in record.__dict__.keys():
            if record.block == "file":
                return False
        return True


class FilterConsole(logging.Filter):
    """
    Filter to stop logs to console handler.

    To use change your log call to something like:
    my_logger.info("This is a file only output", extra={"block": "console"})
    """

    def filter(self, record):
        if "block" in record.__dict__.keys():
            if record.block == "console":
                return False
        return True
