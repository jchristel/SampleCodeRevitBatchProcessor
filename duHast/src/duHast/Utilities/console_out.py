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
