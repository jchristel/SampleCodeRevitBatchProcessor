"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A collection of common UI elements 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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
from Autodesk.Revit.UI import TaskDialog


class AlertDialog(TaskDialog):
    def __init__(self, content):
        self.Title = "BVN"
        TaskDialog.__init__(self.Title)
        self.MainContent = content


def alert(content, exitscript=True, additional_content=None):
    """
    This will display a task dialog with the given content. If exitscript
    is True, the script will terminate after the dialog is closed. Additional
    content input will be put in an expander. This could be more technical
    output
    :param content: The main content of the dialog
    :type content: str
    :param exitscript: If True, the script will terminate after dialog close, defaults to True
    :type exitscript: bool, optional
    :param additional_content: Additional content to be put in an expander, defaults to None
    :type additional_content: str, optional
    """
    if exitscript:
        dialog = AlertDialog(content)
        dialog.MainInstruction = "Error from script:"
        dialog.FooterText = "(Script will stop after this message)"
    else:
        dialog = AlertDialog(content)
        dialog.MainInstruction = "Notification:"

    # Turn off the Title prefix
    dialog.TitleAutoPrefix = False

    # Set additional content if provided
    if additional_content:
        dialog.ExpandedContent = additional_content

    # Show the dialog
    dialog.Show()

    # Exit script if required
    if exitscript:
        if additional_content:
            raise SystemExit(
                "Script terminated because {}\n\nFurther details:\n{}".format(
                    content, additional_content
                )
            )
        else:
            raise SystemExit("Script terminated because {}".format(content))
