from Utility import date_stamps
from Utility import files_get
from Utility import files_io
from Utility import utility

from colorama import init, Fore, Back, Style
import datetime

#: overall debug flag. If False no messages from tests will be printed to console. If True messages will be printed.
IS_DEBUG = False


def _date_time():
    """
    Get the current time string in format 2022-08-09 19:09:19 :

    :return: current date and time.
    :rtype: str
    """

    d = datetime.datetime.now()
    timestamp = d.strftime("%y-%m-%d %H_%M_%S : ")
    return timestamp


def _pad_string(message, padding_length=70):
    """
    Pads a string message to be formatted: left hand side message, right hand side status (if any)
    Maximum length 70 characters (excludes time stamp!)
    If message is longer then 70-2 characters it will be returned un-changed.

    :param message: The message to be padded
    :type message: str
    :param padding_length: Length of message string after padding, defaults to 70
    :type padding_length: int, optional
    :return: Padded message
    :rtype: str
    """

    if len(message) < padding_length:
        status_length = 0
        status = ""
        if "[False]" in message:
            status_length = len("[False]")
            status = "[False]"
        elif "[True]" in message:
            status_length = len("[True]")
            status = "[True]"
        if status_length > 0:
            message_left = message[:-status_length]
            message_left = message_left.ljust(padding_length - status_length, ".")
            message = message_left + status
            return message
        else:
            return message
    else:
        return message


def _header(header_name, padding_length=70):
    """
    Prints a padded header row to console.
    Header will be padded equally to both sides with '-' characters.

    :param header_name: The header to be printed.
    :type header_name: str
    :param padding_length: The overall row length, defaults to 70
    :type padding_length: int, optional
    """

    if padding_length > len(header_name) + 2:
        sides = (padding_length - len(header_name)) // 2
        print(
            "\n"
            + _date_time()
            + "-".ljust(sides, "-")
            + header_name
            + "-".ljust(sides, "-")
        )
    else:
        print("\n" + header_name)


def output(message=""):
    """
    Print message to console.

    Note:

    - The message will be prefixed with a date stamp in format '2022-08-09 19:09:19 :'
    - If message is not a string it will convert it to a string.
    - Multiline strings will pe printed line by line

    :param message: The message, defaults to ''
    :type message: str, optional
    """

    # make sure message is a string:
    if type(message) != str:
        message = str(message)

    timestamp = _date_time()

    # check for multi row messages
    if "/n" in message:
        message_chunks = message.split("\n")
        for message_chunk in message_chunks:
            if "False" in message_chunk:
                print(Fore.RED + "{} {}".format(timestamp, _pad_string(message_chunk)))
            elif "True" in message_chunk:
                print(
                    Fore.GREEN + "{} {}".format(timestamp, _pad_string(message_chunk))
                )
            else:
                print("{} {}".format(timestamp, message_chunk))
    else:
        print("{} {}".format(timestamp, _pad_string(message)))


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

    output("{} [{}]".format(func_name, result_flag))
    if IS_DEBUG:
        output(message)


#: colour coding for console output
init()

#: overall test status
OVERALL_STATUS = True


# run tests in all modules
_header("date_stamps")
status = date_stamps.run_tests(output=out)
OVERALL_STATUS = OVERALL_STATUS & status
out("date_stamps completed with status", status, "")

_header("files_get")
status = files_get.run_tests(output=out)
OVERALL_STATUS = OVERALL_STATUS & status
out("files_get completed with status", status, "")

_header("files_io")
status = files_io.run_tests(output=out)
OVERALL_STATUS = OVERALL_STATUS & status
out("files_io completed with status", status, "")

_header("utility")
status = utility.run_tests(output=out)
OVERALL_STATUS = OVERALL_STATUS & status
out("utility completed with status", status, "")

_header("FINISHED")
print("All tests completed with [{}]".format(OVERALL_STATUS))