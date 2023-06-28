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