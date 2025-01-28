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
#

import os
from duHast.Utilities.files_io import get_directory_path_from_file_path, file_exist
from duHast.Utilities.directory_io import create_target_directory
from duHast.Utilities.directory_io import get_parent_directory
from duHast.pyRevit.console_output import print_header
from duHast.Utilities.utility import get_local_app_data_path
from duHast.Utilities.files_json import read_json_data_from_file, write_json_to_file

from families.reload.Objects.Settings import Settings


print_header("File Path in Settings")

#: get the script location
SCRIPT_DIRECTORY = get_directory_path_from_file_path(__file__)
print("Script dir: {}".format(SCRIPT_DIRECTORY))

#: build flow directory name
FLOW_DIRECTORY = get_parent_directory(SCRIPT_DIRECTORY)
print("Flow dir: {}".format(FLOW_DIRECTORY))

# get the extension lib directory
LIB_DIRECTORY = get_parent_directory(FLOW_DIRECTORY)
print("lib dir: {}".format(LIB_DIRECTORY))

# get the extension directory
DEPLOYMENT_EXTENSION_DIRECTORY = get_parent_directory(LIB_DIRECTORY)
print("deployment Extension dir: {}".format(DEPLOYMENT_EXTENSION_DIRECTORY))

# get the overall root folder of this repository
ROOT_DEVELOPMENT_DIRECTORY = get_parent_directory(DEPLOYMENT_EXTENSION_DIRECTORY)
print("root development dir: {}".format(ROOT_DEVELOPMENT_DIRECTORY))

# get the duHast directory within the extension lib directory
# not required if duHast is installed as a package
DU_HAST_DIRECTORY = os.path.join(ROOT_DEVELOPMENT_DIRECTORY, r"lib\duHast")
print("duHast dir: {}".format(DU_HAST_DIRECTORY))

DU_HAST_SETTINGS_DIRECTORY_NAME = "duHast"
# settings directory
DU_HAST_SETTINGS_DIRECTORY = os.path.join(
    get_local_app_data_path(), DU_HAST_SETTINGS_DIRECTORY_NAME
)
# settings file name
APP_SETTINGS_FILE_NAME = os.path.join(DU_HAST_SETTINGS_DIRECTORY, "reloader.json")


def get_settings():
    # look for settings file in %AppData/Local/duHast%

    if create_target_directory(
        get_local_app_data_path(), DU_HAST_SETTINGS_DIRECTORY_NAME
    ):
        if file_exist(APP_SETTINGS_FILE_NAME):
            # load settings file
            read_result = read_json_data_from_file(APP_SETTINGS_FILE_NAME)
            if read_result.status is False:
                print(
                    "failed to read settings file: {} with: {}".format(
                        APP_SETTINGS_FILE_NAME, read_result.message
                    )
                )
                return None
            data = read_result.result[0]
            
            settings_instance = Settings(j=data)
            return settings_instance
        else:
            print(
                "failed to get settings file: {}. First time usage?".format(
                    APP_SETTINGS_FILE_NAME
                )
            )
            return None
    else:
        print(
            "failed to create settings directory: {}".format(DU_HAST_SETTINGS_DIRECTORY)
        )
        return None


def write_settings(settings_instance):

    # save json settings to file
    write_result = write_json_to_file(settings_instance, APP_SETTINGS_FILE_NAME)
    # return the outcome of the operation
    return write_result
