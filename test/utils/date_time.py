import datetime


def date_time():
    """
    Get the current time string in format 2022-08-09 19:09:19 :
    :return: current date and time.
    :rtype: str
    """

    d = datetime.datetime.now()
    timestamp = d.strftime("%y-%m-%d %H_%M_%S : ")
    return timestamp