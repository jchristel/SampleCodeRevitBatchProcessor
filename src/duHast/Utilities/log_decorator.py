import functools
import traceback
from duHast.Utilities.benchmarking import measure_time_wrapper


def get_add_logger_decorator(
    log_obj_inst, errors_in_console=True, suppress_exceptions=True
):
    """
    This is a decorator factory that returns a decorator that can be used to add logging to a function.
    Pass this function an instance of the LoggerObject class from duHast.Utilities.Objects.logger_object.py.
    Inherit and extend this class to the needs of your application. This will connect the decorator to
    the logger object application wide. Assign the return value to a variable called log or add_logger etc.

    :param log_obj_inst: An instance of the LoggerObject class from duHast.Utilities.Objects.logger_object.py
    :type log_obj_inst: duHast.Utilities.Objects.logger_object.LoggerObject
    :param errors_in_console: Whether to output errors to the console. Defaults to True. Turn off to handle
    in the application code
    :type errors_in_console: bool
    :return: A decorator that can be used to add logging to a function
    :rtype: function

    """

    def add_logger(
        log_level=(10, 30),
        measure_time=False,
    ):
        """
        Decorator function to add logging to a function.
        By default it will log the start and end of the function, the arguments passed in and the return value.
        It will also log the elapsed time if measure_time is set to True.

        Use it like:
        @add_logger()
        def example_function():
            do_stuff()

        :param log_level: A tuple of the python log levels for the file and console handlers. See
        https://docs.python.org/3/library/logging.html#levels for log levels
        :type log_level: tuple/list of int (file_log_level, console_log_level)
        :param measure_time: Whether to measure and log the time the function takes to execute
        :type measure_time: bool
        :return: The decorated function
        :rtype: function
        """

        def decorator_log(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_name = func.__name__
                logger_in = log_obj_inst
                # First check to see if the log levels passed in are different and update
                cur_file_log_level = logger_in.file_handler.level
                cur_console_log_level = logger_in.console_handler.level
                updated_levels = False
                if (
                    cur_file_log_level != log_level[0]
                    or cur_console_log_level != log_level[1]
                ):
                    # Update the log levels
                    logger = logger_in.update_log_level(log_level)
                    logger.info("Updated log levels to {}".format(log_level))
                    updated_levels = True
                try:
                    # Log the start of the function execution
                    logger = logger_in.get_logger_obj()
                    logger.info(
                        "------------ Started function: {}. Log level set at: {}".format(
                            func_name, log_level
                        )
                    )
                    # Get the args passed into the function to log
                    args_repr = [repr(a) for a in args]
                    kwargs_repr = [
                        "{}={}".format(k, repr(v)) for k, v in kwargs.items()
                    ]
                    # Log those arguments
                    if len(args_repr + kwargs_repr) > 0:
                        signature = ", ".join(args_repr + kwargs_repr)
                        logger.debug(
                            "function {} called with args: {}".format(
                                func_name, signature
                            )
                        )
                    else:
                        logger.info(
                            "function {} called with no arguments".format(func_name)
                        )

                except Exception as e:
                    pass

                result = None

                try:
                    # Execute the wrapped function either with or without time measurement
                    if measure_time:
                        result = measure_time_wrapper(
                            func, logger, measure=measure_time
                        )(*args, **kwargs)

                        return result
                    else:
                        result = func(*args, **kwargs)
                        return result

                except Exception as e:
                    msg = "ERROR raised in {}.\n\n{}\n".format(
                        func_name, traceback.format_exc()
                    )
                    if errors_in_console:
                        logger.error(msg)

                    else:
                        logger.error(msg, extra={"block": "console"})

                    if not suppress_exceptions:
                        raise e

                finally:
                    # Log the return value
                    if result:
                        logger.info(
                            "Finished function: {}. Return value is: {}".format(
                                func_name, repr(result)
                            )
                        )
                    else:
                        logger.info("Finished function: {}".format(func_name))
                    # Reset the log levels if they were updated
                    if updated_levels:
                        logger = logger_in.update_log_level(
                            (cur_file_log_level, cur_console_log_level)
                        )

            return wrapper

        return decorator_log

    return add_logger
