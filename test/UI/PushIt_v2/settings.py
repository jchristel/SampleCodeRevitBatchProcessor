# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

import os
import sys

debug = True

DU_HAST_PATH = None
if debug:
    # setup duHast
    DU_HAST_PATH = (
        r"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\src"
    )

    # insert duHast dev version at the beginning of path in case a prod version is in path
    sys.path.insert(0, DU_HAST_PATH)


from duHast.Utilities.files_io import get_directory_path_from_file_path, file_exist
from duHast.Utilities.directory_io import get_parent_directory
from duHast.Utilities.utility import get_local_app_data_path

#: get the script location
SCRIPT_DIRECTORY = get_directory_path_from_file_path(__file__)
print("Script dir: {}".format(SCRIPT_DIRECTORY))

#: build flow directory name
FLOW_DIRECTORY = get_parent_directory(SCRIPT_DIRECTORY)
print("Flow dir: {}".format(FLOW_DIRECTORY))

# add the flow directory to the path in order for imports from PushIt name space to work
sys.path.insert(0, FLOW_DIRECTORY)

# get the extension lib directory
LIB_DIRECTORY = get_parent_directory(FLOW_DIRECTORY)
print("lib dir: {}".format(LIB_DIRECTORY))

# get the extension directory
DEPLOYMENT_EXTENSION_DIRECTORY = get_parent_directory(LIB_DIRECTORY)
print("deployment Extension dir: {}".format(DEPLOYMENT_EXTENSION_DIRECTORY))

# get the overall root folder of this repository
ROOT_DEVELOPMENT_DIRECTORY = get_parent_directory(DEPLOYMENT_EXTENSION_DIRECTORY)
print("root development dir: {}".format(ROOT_DEVELOPMENT_DIRECTORY))

if DU_HAST_PATH is None:
    # get the duHast directory within the lib directory
    DU_HAST_DIRECTORY = os.path.join(ROOT_DEVELOPMENT_DIRECTORY, r"global.lib\duHast")
else:
    DU_HAST_DIRECTORY = os.path.join(DU_HAST_PATH, "duHast")

print("duHast dir: {}".format(DU_HAST_DIRECTORY))

# duHast settings directory name
DU_HAST_SETTINGS_DIRECTORY_NAME = "duHast"

# settings directory
DU_HAST_SETTINGS_DIRECTORY = os.path.join(
    get_local_app_data_path(), DU_HAST_SETTINGS_DIRECTORY_NAME
)

# settings file name
APP_SETTINGS_FILE_NAME = os.path.join(DU_HAST_SETTINGS_DIRECTORY, "pushIt.json")
