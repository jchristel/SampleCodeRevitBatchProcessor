"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a pyRevit file picker wrapper function. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

def get_file_path_from_user(forms, title, file_extension, multi_file=False):
    """
    Very simple wrapper function to get a file path from the user.

    :param forms: pyRevit forms
    :type forms: pyRevit forms module
    :param title: The title of the file picker dialog.
    :type title: str
    :param file_extension: The file extension to filter for. Example: "csv"
    :type file_extension: str
    :param multi_file: Single vs multi file selection, defaults to False (single file)
    :type multi_file: bool, optional

    :return: The file path(s) selected by the user. None if no file was selected.
    :rtype: str, [str],None
    """

    file_path = forms.pick_file(file_ext=file_extension, multi_file=multi_file, title=title)
    if file_path is None or file_path == "" or file_path == []:
        return None

    return file_path