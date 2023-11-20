import functools

from duHast.Utilities.benchmarking import measure_time_wrapper


def get_add_logger_decorator(log_obj_inst):
    """
    This is a decorator factory that returns a decorator that can be used to add logging to a function.
    Pass this function an instance of the LoggerObject class from duHast.Utilities.Objects.logger_object.py.
    This will connect the decorator to the logger object application wide.
    Assign the return value to a variable called log, add_logger or the like.

    :param log_obj_inst: An instance of the LoggerObject class from duHast.Utilities.Objects.logger_object.py
    :type log_obj_inst: duHast.Utilities.Objects.logger_object.LoggerObject
    :return: A decorator that can be used to add logging to a function
    :rtype: function

    """

    def add_logger(logger_in=log_obj_inst, log_level=(10, 30), measure_time=False):
        """
        Decorator function to add logging to a function.
        By default it will log the start and end of the function, the arguments passed in and the return value.
        It will also log the elapsed time if measure_time is set to True.

        Use it like:
        @add_logger()
        def example_function():
            do_stuff()

        If using the decorator from the get_add_log_decorator factory you can override the logger object
        instance by passing in a different one to the decorator. This will only affect the function
        that the decorator is used on. NOT the application wide logger object.

        :param logger_in: An instance of the LoggerObject class from duHast.Utilities.Objects.logger_object.py.
        :type logger_in: duHast.Utilities.Objects.logger_object.LoggerObject
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
                    logger.error(
                        "Exception raised in {}. exception: {}".format(
                            func_name, str(e)
                        )
                    )
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
