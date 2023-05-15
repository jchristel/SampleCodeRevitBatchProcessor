"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit batch processor set up steps. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are required when running tests in Revit batch processor.

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


import clr
from padding import pad_string
# Add batch processor scripting references
import revit_script_util
import revit_file_util

def add_rbp_ref():
    """
    Imports revit batch processor dlls and gets the current document.

    :return: Current Revit model document.
    :rtype: Autodesk.Revit.DB.Document
    """
    clr.AddReference("RevitAPI")
    clr.AddReference("RevitAPIUI")
    # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    return doc


def output(message=""):
    """
    Prints message to revit batch processor log window.

    :param message: A message, defaults to ""
    :type message: str, optional
    """

    # make sure message is a string:
    if type(message) != str:
        message = str(message)

    # check for multi row messages
    if "\n" in message:
        message_chunks = message.split("\n")
        for message_chunk in message_chunks:
            revit_script_util.Output(pad_string(message_chunk))
    else:
        revit_script_util.Output(pad_string(message))
