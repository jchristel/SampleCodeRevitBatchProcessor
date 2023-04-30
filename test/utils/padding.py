from utils.date_time import date_time


def pad_header_no_time_stamp(header_name, padding_length=70):
    if padding_length > len(header_name) + 2:
        sides = (padding_length - len(header_name)) // 2
        # return the padded header text
        return(
            "\n"
            + "-".ljust(sides, "-")
            + header_name
            + "-".ljust(sides, "-")
        )
    else:
        return("\n" + header_name)

def pad_header(header_name, padding_length=70):

    if padding_length > len(header_name) + 2:
        sides = (padding_length - len(header_name)) // 2
        # return the padded header text
        return(
            "\n"
            + date_time()
            + "-".ljust(sides, "-")
            + header_name
            + "-".ljust(sides, "-")
        )
    else:
        return("\n" + header_name)


def pad_string(message, padding_length=70):
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