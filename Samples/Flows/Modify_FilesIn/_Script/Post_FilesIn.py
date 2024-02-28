"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the post processing script of this flow.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script runs inside of Revit and the Revit Batch Processor Environment. It is used to 

- move files to the correct filing location
- maintain a current directory of nwdc, itc, etc files ( as specified in file data in csv file)
- update the revision tracker file.

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


# --------------------------
# default file path locations
# --------------------------
import clr, sys, os


import settings as settings
from utils.file_data import get_file_data
from utils.revision_tracker import save_files_received_list
from utils.files_move_copy import copy_other_files, move_files_to_filing_location

from duHast.Utilities.console_out import output

import script_util

# -------------
# my code here:
# -------------

# -------------
# main:
# -------------


def output_(message):
    """
    output message wrapper for utility functions
    
    :param message: the message
    :type message: str
    """
    output(message, script_util.Output)

output("Building files received mapping table.... start", script_util.Output)
# read all settings
_current_document_data = []
_current_document_data_result = get_file_data()

if _current_document_data_result.status:
    output(
        "Reading file data.... status: " + str(_current_document_data_result.message),
        script_util.Output,
    )
    _current_document_data = _current_document_data_result.result
else:
    output(
        "Failed to read file data: ".format(_current_document_data_result.message),
        script_util.Output,
    )
    # get out!
    sys.exit(1)

# save files received list
_result_save_file_stats = save_files_received_list(_current_document_data, output_)
output(
    "Writing files received mapping table.... status [{}]".format(
        _result_save_file_stats
    ),
    script_util.Output,
)

# copy any *.nwc files into the navis current folder
output("\nCopy .nwc files to current folder .... start", script_util.Output)
_copy_nwc_flag = copy_other_files(
    _current_document_data, settings.NWC_FILE_EXTENSION, output=output_
)
output("Copy nwc files .... status: [{}]".format(_copy_nwc_flag), script_util.Output)

# copy any *.ifc files into the ifc folder
output("\nCopy .ifc files to current folder .... start", script_util.Output)
_copy_ifc_flag = copy_other_files(
    _current_document_data, settings.IFC_FILE_EXTENSION, output=output_
)
output("Copy ifc files .... status: [{}]".format(_copy_ifc_flag), script_util.Output)

# move files from temp input location to filing location
output("Moving files .... start", script_util.Output)
_move_files_flag = move_files_to_filing_location(
    file_data=_current_document_data, output=output_
)
output("Moving files .... status: [{}]".format(_move_files_flag), script_util.Output)
