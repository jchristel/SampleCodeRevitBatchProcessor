"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains data read file names . 
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

# set path to sample file directory
import os

# get the script location
MODULE_DIRECTORY = os.path.dirname(__file__)
# build flow directory name
TEST_DIRECTORY = os.path.dirname(MODULE_DIRECTORY)
# build duHast and duHast sample directories
DU_HAST_TEST_DIRECTORY = os.path.dirname(os.path.dirname(TEST_DIRECTORY))
SAMPLE_FILES_DIRECTORY = os.path.join(DU_HAST_TEST_DIRECTORY, r"test/_rbp_flow/_sampleFiles")

# data test file name
JSON_GEO_DATA_TEST_FILE = "geo_data.json"
# data fully qualified file path
JSON_GEO_DATA_TEST_FILE_FULL = os.path.join(SAMPLE_FILES_DIRECTORY,JSON_GEO_DATA_TEST_FILE)