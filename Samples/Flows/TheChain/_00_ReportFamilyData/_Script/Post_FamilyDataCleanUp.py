"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains post reporting clean up functions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# --------------------------
# Imports
# --------------------------


import settings as settings  # sets up all commonly used variables and path locations!
from duHast.Utilities.console_out import output
from duHast.Utilities.files_get import get_files_single_directory
from duHast.Utilities.files_io import file_delete
from duHast.Utilities.directory_io import get_child_directories, directory_delete


# -------------
# my code here:
# -------------


def delete_file_in_input_directory():
    """
    Deletes any files in the input directory.
    """
    files = get_files_single_directory(
        folder_path=settings.INPUT_DIRECTORY,
        file_prefix="",
        file_suffix="",
        file_extension=settings.REPORT_FILE_EXTENSION,
    )
    if len(files) > 0:
        for f in files:
            flag_delete = file_delete(f)
            output("Deleted marker file: {} [{}]".format(f, flag_delete))
    else:
        output("Input directory did not contain any files.")


def delete_working_directories():
    """
    Deletes the session ID directories in which all the single reports are saved.
    """

    # clean up. get directories in output folder and delete them
    dirs = get_child_directories(settings.OUTPUT_FOLDER)
    for dir in dirs:
        flag_delete = directory_delete(dir)
        output("Deleted directory: {} [{}]".format(dir, flag_delete))
