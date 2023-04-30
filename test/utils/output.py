"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains text output to console functions . 
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

from colorama import Fore
from utils.date_time import date_time
from utils.padding import pad_string, pad_header

#: overall debug flag. If False no messages from tests will be printed to console. If True messages will be printed.
IS_DEBUG = False


def out_header(header_name, padding_length=70):
    """
    Prints a padded header row to console.
    Header will be padded equally to both sides with '-' characters.

    :param header_name: The header to be printed.
    :type header_name: str
    :param padding_length: The overall row length, defaults to 70
    :type padding_length: int, optional
    """

    print(pad_header(header_name, padding_length))


def out_message(message=""):
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

    timestamp = date_time()

    # check for multi row messages
    if "/n" in message:
        message_chunks = message.split("\n")
        for message_chunk in message_chunks:
            if "False" in message_chunk:
                print(Fore.RED + "{} {}".format(timestamp, pad_string(message_chunk)))
            elif "True" in message_chunk:
                print(Fore.GREEN + "{} {}".format(timestamp, pad_string(message_chunk)))
            else:
                print("{} {}".format(timestamp, message_chunk))
    else:
        print("{} {}".format(timestamp, pad_string(message)))
