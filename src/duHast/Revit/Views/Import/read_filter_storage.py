"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view filters storage reading from file. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
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


from duHast.Utilities.files_json import read_json_data_from_file
from duHast.Revit.Views.Objects.Data.view_filter import ViewFilter

from duHast.Utilities.Objects.result import Result

DEBUG = False

def read_filter_storage_from_file(file_path, node_name=""):

    """
    Read the view filter storage from file.

    :param file_path: Full path to the file including file name.
    :type file_path: str

    :return: Result message and list of view filter storage objects.
    :rtype: tuple (result message, list of view filter storage objects)
    """

    return_value = Result()

    try:
        # attempt to read data from file
        data_result = read_json_data_from_file(file_path)

        # check if read was successful
        if not data_result.status:
            return_value.update(data_result)
            return return_value

        # check if any data was found
        if len(data_result.result) == 0:
            return_value.update_sep(False, "No view filter storage data found in file.")
            return return_value
        
        data = data_result.result[0]
        
        # check if node name exists
        if node_name not in data:
            return_value.update_sep(False, "No view filter storage data found in file for node: {}.".format(node_name))
            print(data)
            return return_value

        # get a list of view filter storage objects
        view_filter_storage_data = data[node_name]

        if not isinstance(view_filter_storage_data, list):
            return_value.update_sep(False, "Filter storage data found in file for node: {} should be a list. Got {}.".format(node_name, type(view_filter_storage_data)))
            return return_value
        
        # loop over all view filter storage entries and create objects
        for view_filter_entry in view_filter_storage_data:
            if DEBUG:
                print("view filter entry in json: {}\n".format(view_filter_entry))
            # attempt to create view filter storage object
            try:
                view_filter = ViewFilter(j=view_filter_entry)
                if DEBUG:
                    print("Created view filter storage object: {}\n".format(view_filter))
                return_value.result.append(view_filter)
            except Exception as e:
                return_value.update_sep(False, "Failed to create view filter storage object from data in file for node: {}. {}".format(node_name, str(e)))
                

        return_value.update_sep(True, "Successfully read view filter storage from file.")
    
    except Exception as e:
        return_value.update_sep(False, "Failed to read view filter storage from file. {}".format(str(e)))
       

    return return_value

