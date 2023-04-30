from Utility import date_stamps
from Utility import files_get
from Utility import files_io
from Utility import utility

from utils.output import out_message, out_header

from colorama import init, Fore, Back, Style

#: overall debug flag. If False no messages from tests will be printed to console. If True messages will be printed.
IS_DEBUG = False


def out(func_name, result_flag, message):
    """
    Output to console

    :param func_name: the function name to be printed
    :type func_name: str
    :param result_flag: The test function result to be printed.
    :type result_flag: bool
    :param message: Any messages from the test function to be printed in debug mode.
    :type message: str
    """

    out_message("{} [{}]".format(func_name, result_flag))
    if IS_DEBUG:
        out_message(message)


#: colour coding for console output
init()

#: overall test status
OVERALL_STATUS = True


# run tests in all modules
out_header("date_stamps")
status = date_stamps.run_tests(output=out)
OVERALL_STATUS = OVERALL_STATUS & status
out("date_stamps completed with status", status, "")

out_header("files_get")
status = files_get.run_tests(output=out)
OVERALL_STATUS = OVERALL_STATUS & status
out("files_get completed with status", status, "")

out_header("files_io")
status = files_io.run_tests(output=out)
OVERALL_STATUS = OVERALL_STATUS & status
out("files_io completed with status", status, "")

out_header("utility")
status = utility.run_tests(output=out)
OVERALL_STATUS = OVERALL_STATUS & status
out("utility completed with status", status, "")

out_header("FINISHED")
print("All tests completed with [{}]".format(OVERALL_STATUS))