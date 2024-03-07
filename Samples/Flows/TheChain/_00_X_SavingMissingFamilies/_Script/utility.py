"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of global variables.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Apart from defining a number of variable values this module also updates path variable with directories containing modules required to 
run this script.

"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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


import sys
import os

import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Utilities.files_io import file_exist
from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.directory_io import directory_exists

def save_out_missing_families_check():
    """
    Check whether a marker file exists, which specifies: where family base report is located and the directory to save missing families to.

    :return: True if marker file exists, otherwise False. The file path of the family base data report. The root directory path to where families are to be saved to.
    :rtype: bool, string, string
    """

    save_out = False
    family_base_data_file_path = ""
    family_out_directory = ""

    # build marker file path
    marker_file_path = os.path.join(settings.INPUT_DIRECTORY ,settings.FILE_NAME_MARKER_SAVEOUT_MISSING_FAMILIES)
    # check if file exists in input location
    if file_exist(marker_file_path):
        # read file
        rows =  read_csv_file(marker_file_path)
        # should be at least two rows...
        if len(rows) >= 2:
            got_base_data = False
            got_dir_out = False
            # assign family base data file path
            if file_exist(rows[0][0]):
                family_base_data_file_path = rows[0][0]
                got_base_data = True
            # assign family out file path
            if directory_exists(rows[1][0]):
                family_out_directory = rows[1][0]
                got_dir_out = True
            save_out = got_base_data and got_dir_out
    return save_out, family_base_data_file_path, family_out_directory
