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
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
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
