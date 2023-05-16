"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains string padding functions for message formatting. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sample output without a time stamp:

------------------------------header------------------------------

or with a time stamp:

23-04-30 20_31_07 : -----------------header------------------------ 
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from duHast.Utilities import date_stamps

#: how long is a padded row
DEFAULT_PADDING_LENGTH = 90

def pad_header_no_time_stamp(header_name, padding_length=DEFAULT_PADDING_LENGTH):
    """
    Pads a header string to be centred in a row of dashes of a given length.

    :param header_name: The header
    :type header_name: str
    :param padding_length: the length of the padded header excluding time stamp, defaults to 70
    :type padding_length: int, optional
    :return: A padded header row.
    :rtype: str
    """
    if padding_length > len(header_name) + 2:
        sides = (padding_length - len(header_name)) // 2
        # return the padded header text
        return "\n" + "-".ljust(sides, "-") + header_name + "-".ljust(sides, "-")
    else:
        return "\n" + header_name


def pad_header_with_time_stamp(header_name, padding_length=DEFAULT_PADDING_LENGTH):
    """
    Pads a header string to be centred in a row of dashes of a given length.

    Will also add a time stamp to the beginning of the message.

    :param header_name: The header
    :type header_name: str
    :param padding_length: the length of the padded header excluding time stamp, defaults to 70
    :type padding_length: int, optional
    :return: A padded header row.
    :rtype: str
    """

    # get a time stamp
    time_stamp = date_stamps.get_date_stamp("%y-%m-%d %H_%M_%S : ")
    # check whether max length is not exceeded
    if padding_length > len(header_name) + 2 + len(time_stamp):
        sides = (padding_length - len(header_name) - len(time_stamp)) // 2
        # return the padded header text
        return (
            "\n"
            + date_stamps.get_date_stamp("%y-%m-%d %H_%M_%S : ")
            + "-".ljust(sides, "-")
            + header_name
            + "-".ljust(sides, "-")
        )
    else:
        return "\n" + header_name


def pad_string(message, padding_length=DEFAULT_PADDING_LENGTH):
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
