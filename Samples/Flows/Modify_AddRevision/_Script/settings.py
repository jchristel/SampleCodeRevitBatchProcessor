"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing settings used in all flow scripts.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- adds the following directories to the environment

    - duHast library

- populates a number of variables used in all flow scripts
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#

#: duHast library
DU_HAST_DIRECTORY = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
# set path to common library
import sys

sys.path += [DU_HAST_DIRECTORY]

from duHast.Utilities.files_io import get_directory_path_from_file_path
from duHast.Utilities.directory_io import get_parent_directory

#: get the script location
SCRIPT_DIRECTORY = get_directory_path_from_file_path(__file__)
# add the script directory to path
sys.path += [SCRIPT_DIRECTORY]
#: build flow directory name
FLOW_DIRECTORY = get_parent_directory(SCRIPT_DIRECTORY)

#: any data output to go here
OUTPUT_FOLDER = FLOW_DIRECTORY + r"\_Output"

#: log marker file location
LOG_MARKER_DIRECTORY = FLOW_DIRECTORY + r"\_LogMarker"

#: WSM marker file location
WSM_MARKER_DIRECTORY = LOG_MARKER_DIRECTORY

#: debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r"C:\temp\Test_Files.rvt"

#: splash sceen sheet name
SPLASH_SCREEN_SHEET_NAME = "SPLASH SCREEN"
