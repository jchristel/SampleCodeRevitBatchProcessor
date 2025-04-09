"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions attempting to use .net library to read a text file whilst avoiding encoding errors. 
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

import clr
import os

from duHast.Utilities.Objects.result import Result

# load the wrapper dll from the libs folder
# the dll is located in the libs folder of the extension, which is one level up from the current file's directory
current_directory = os.path.dirname(__file__)
parent_directory = os.path.dirname(current_directory)
dll_path = os.path.join(parent_directory, "libs", "CSVHelperWrapper.dll")
clr.AddReference(dll_path)

# import the ReadFromFile class from the CSVHelperWrapper namespace
from CSVHelperWrapper import ReadFromFile

def read_from_delimited_text_file(file_path, delimiter=","):
    """
    Reads data from a text file using the CSVHelperWrapper library.
    
    :param file_path: Path to the text file.
    :type file_path: str
    :param delimiter: Delimiter used in the textfile. Default is ",".
    :type delimiter: str
    
    :return:
        Result class instance.

        - result.status (bool) True if file was read without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will contain a list of nested lists of string representing the data read from the file.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
         result.result be an empty list
    :rtype: :class:`.Result`
    """
    
    return_value = Result()
    
    try:
        
        # do some type checking to ensure the inputs are valid
        if not isinstance(file_path, str):
            raise ValueError("file_path must be a string")
        if not isinstance(delimiter, str):
            raise ValueError("delimiter must be a string")
        
        # read the text file using the ReadFromFile class from the CSVHelperWrapper library
        result_list = ReadFromFile.ReadFromTextFile(
            file_path, 
            delimiter=delimiter,
        )
        
        # get all error messages from the ReadFromFile class if the result list is empty
        # and set the overall status to False
        if result_list.Count == 0:
            for message in ReadFromFile.ErrorHistory:
                return_value.append_message(message)
            # set the overall status to False
            return_value.status = False
            # and get out
            return return_value
        
        # convert .net list to python list
        for i in range(result_list.Count):
            nested_list= []
            for j in range(result_list[i].Count):
                nested_list.append(result_list[i][j])
            return_value.result.append(nested_list)
        
        
        return_value.update_sep(True, "Text file read from {} with status: {}".format(file_path, True))
        return return_value

    except Exception as e:
        return_value.update_sep(False, "Error reading text file: {}".format(e))
        return return_value

