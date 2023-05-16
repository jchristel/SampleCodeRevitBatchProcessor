"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A function used to output messages to a console.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.Utilities import date_stamps as dateStamp
from duHast.Utilities import padding as pad


def default_out_print(message):
    """
    Default pip out method: print to console.

    :param message: A message
    :type message: str
    """

    print(message)


def output(message="", pipe_out=default_out_print):
    """
    Print message to pipe.

    Note:

    - If message is not a string it will convert it to a string.
    - Multi line strings will pe printed line by line.
    - strings containing [true] ot [false] will be padded to have [true] or [false] to the right hand side.

    :param message: The message, defaults to ''
    :type message: str, optional
    """

    # make sure message is a string:
    if type(message) != str:
        message = str(message)

    # check for multi row messages
    if "\n" in message:
        message_chunks = message.split("\n")
        for message_chunk in message_chunks:
            pipe_out("{}".format(pad.pad_string(message_chunk)))
    else:
        pipe_out("{}".format(pad.pad_string(message)))


def output_with_time_stamp(message="", pipe_out=default_out_print):
    """
    Print message to console.

    Note:

    - The message will be prefixed with a date stamp in format '2022-08-09 19_09_19 :'
    - If message is not a string it will convert it to a string.
    - Multi line strings will pe printed line by line
    - strings containing [true] ot [false] will be padded to have [true] or [false] to the right hand side.

    :param message: The message, defaults to ''
    :type message: str, optional
    """

    # make sure message is a string:
    if type(message) != str:
        message = str(message)

    # get the current time string
    # 2022-08-09 19:09:19 :
    timestamp = dateStamp.get_date_stamp("%y-%m-%d %H_%M_%S :")

    # check for multi row messages
    if "\n" in message:
        message_chunks = message.split("\n")
        for message_chunk in message_chunks:
            pipe_out("{} {}".format(timestamp, pad.pad_string(message_chunk)))
    else:
        pipe_out("{} {}".format(timestamp, pad.pad_string(message)))


def output_header(message="", pipe_out=default_out_print):
    """
    Prints header message to pipe.

    Note:

    - If message is not a string it will convert it to a string.

    :param message: The message, defaults to ''
    :type message: str, optional
    """

    # make sure message is a string:
    if type(message) != str:
        message = str(message)

    pipe_out("{}".format(pad.pad_header_no_time_stamp(message)))


def output_header_with_time_stamp(message="", pipe_out=default_out_print):
    """
    Prints header message to pipe.

    Note:

    - If message is not a string it will convert it to a string.
    - The header will be prefixed with a date stamp in format '2022-08-09 19_09_19 :'

    :param message: The message, defaults to ''
    :type message: str, optional
    """

    # make sure message is a string:
    if type(message) != str:
        message = str(message)

    pipe_out("{}".format(pad.pad_header_with_time_stamp(message)))
