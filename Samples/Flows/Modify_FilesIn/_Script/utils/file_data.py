"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a doc existing file data related helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- reads file data from csv file and converts it into a list of class objects
- gets file data by name matches the past in name to the start of the existing file name, and if found a match, returns the class object

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


import os
import settings as settings  # sets up all commonly used variables and path locations!
from docExFile import docExFile

from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.Objects.result import Result

def get_file_data():
    """
    Read file data from csv file and convert it into a list of class objects
    
    :return: instance of Result class

        - if successful, .result is a list of class objects
        - if failed, .result is an empty list

    :rtype: Result
    """
    return_value = Result()
    try:
        csv_data_rows = read_csv_file(os.path.join(settings.DATA_FILE_PATH))
        if(len(csv_data_rows) == 0):
            return_value.update_sep(False, "Error reading file data: No data found in file: {}".format(os.path.join(settings.FLOW_DIRECTORY, settings.DATA_FILE_NAME)))
            return return_value
        # read csv file
        row_counter = 0
        for d in csv_data_rows:
            # ignore the header row
            if(row_counter == 0):
                row_counter += 1
                continue
            return_value.result.append(docExFile(d))
        return_value.update_sep(True, "File data read successfully")
    except Exception as e:
        return_value.update_sep(False, "Error reading file data: " + str(e))
    return return_value

def get_file_data_by_name(data, name):
    """
    Get file data by existing file name ( converted to lower case) starts with the past in name (also converted to lower case), and if found a match, return the class object.

    :param data: list of docExFile class objects
    :type data: list
    :param name: file name
    :type name: str
    :return: class object, if match is found otherwise None!
    :rtype: class object docExFile
    """

    result = None
    for d in data:
        if(name.lower().startswith(d.existing_file_name.lower())):
            result = d
            break
    return result

def get_file_data_by_name_and_extension(data, name, file_extension):
    """
    Get file data by:

    - existing file name ( converted to lower case) starts with the past in name (also converted to lower case)
    - file extension matches the past in file_extension (also converted to lower case)
    
    and if found a match, return the class object.

    :param data: list of docExFile class objects
    :type data: list
    :param name: file name
    :type name: str
    :param file_extension: file extension
    :type file_extension: str
    :return: class object, if match is found otherwise None!
    :rtype: class object docExFile
    """

    result = None
    for d in data:
        if(name.lower().startswith(d.existing_file_name.lower()) and d.file_extension.lower() == file_extension.lower()):
            result = d
            break
    return result