import functools

from duHast.Utilities.benchmarking import measure_time_wrapper


def get_add_logger_decorator(log_obj_inst):
    def add_logger(my_logger=log_obj_inst, log_level=(10, 30), measure_time=False):
        def decorator_log(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Update the log levels
                logger = log_obj_inst.update_log_level(log_level)
                try:
                    logger = log_obj_inst.get_logger_obj()
                    logger.info(
                        "---- Started execution in function: {}. Log level set at: {}".format(
                            func.__name__, log_level
                        )
                    )
                    # Get the args passed into the function to log
                    args_repr = [repr(a) for a in args]
                    kwargs_repr = [
                        "{}={}".format(k, repr(v)) for k, v in kwargs.items()
                    ]
                    if len(args_repr + kwargs_repr) > 0:
                        signature = ", ".join(args_repr + kwargs_repr)
                        logger.debug(
                            "function {} called with args: {}".format(
                                func.__name__, signature
                            )
                        )
                    else:
                        logger.debug(
                            "function {} called with no arguments".format(func.__name__)
                        )

                except Exception as e:
                    pass

                try:
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
                            func.__name__, str(e)
                        )
                    )
                    raise e

            return wrapper

        return decorator_log

    return add_logger
