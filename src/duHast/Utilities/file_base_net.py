"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions attempting to use .net library ro write to file to avoid encoding errors. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

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
#

import clr
import os
from System.Collections.Generic import List

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.Objects.file_encoding_bom import BOMValue as bom_value


# load the wrapper dll from the libs folder
# the dll is located in the libs folder of the extension, which is one level up from the current file's directory
current_directory = os.path.dirname(__file__)
parent_directory = os.path.dirname(current_directory)
dll_path = os.path.join(parent_directory, "libs", "CSVHelperWrapper.dll")
clr.AddReference(dll_path)

# import the WriteToFile class from the CSVHelperWrapper namespace
from CSVHelperWrapper import WriteToFile
from CSVHelperWrapper import BOMValue

def write_to_csv(file_path, header, data, write_type="w", bom=None, delimiter=","):
    """
    Write data to a CSV file using the CSVHelperWrapper library.
    
    :param file_path: Path to the CSV file.
    :type file_path: str
    :param header: List of strings representing the header of the CSV file.
    :type header: List[str]
    :param data: List of list of strings representing the data to write to file.
    :type data: List[List[str]]
    :param data: List of list of string representing the data to write to file.
    :return: True if successful, otherwise False.
    """
    
    return_value = Result()
    
    try:
        
        # do so me type checking to ensure the inputs are valid
        if not isinstance(file_path, str):
            raise ValueError("file_path must be a string")
        if not isinstance(header, list) or not all(isinstance(item, str) for item in header):
            raise ValueError("header must be a list of strings")
        if not isinstance(data, list) or not all(isinstance(row, list) and all(isinstance(item, str) for item in row) for row in data):
            raise ValueError("data must be a list of lists of strings")
        
        
        # map bom values to the BOMValue enum
        if bom is not None:
            if bom == bom_value.UTF_8:
                bom = BOMValue.UTF8
            elif bom == bom_value.UTF_16_LITTLE_ENDIAN:
                bom = BOMValue.UTF_16_LITTLE_ENDIAN
            elif bom == bom_value.UTF_16_BIG_ENDIAN:
                bom = BOMValue.UTF_16_BIG_ENDIAN
            elif bom == bom_value.UTF_32_LITTLE_ENDIAN:
                bom = BOMValue.UTF_32_LITTLE_ENDIAN
            elif bom == bom_value.UTF_32_BIG_ENDIAN:
                bom = BOMValue.UTF_32_BIG_ENDIAN
            else:
                raise ValueError("Invalid BOM value. Must be one of the BOMValue enum values.")
        
        
        # convert the header and data to .NET List types
        header_net = List[str]()  # Convert to List[str]
        for item in header:
            header_net.Add(item)  # Add each item to the List[str]
        
        data_net = List[List[str]]()  # Convert to List[List[str]]
        for row in data:
            row_net = List[str]()  # Create a new List[str] for each row
            for item in row:
                row_net.Add(item)  # Add each item to the List[str]
            data_net.Add(row_net)  # Add the row to the List[List[str]]
        
        # Write to CSV using the WriteToFile class from the CSVHelperWrapper library
        result = WriteToFile.WriteToCsv(
            file_path, 
            header_net, 
            data_net, 
            writeType=write_type, 
            bom=bom, delimiter=delimiter
        )
        
        # get all error messages from the WriteToFile class
        if not result:
            for message in WriteToFile.ErrorHistory:
                return_value.append_message(message)
            # set the overall status to False
            return_value.status = False
            # and get out
            return return_value
        
        return_value.update_sep(result, "CSV file written to {} with status: {}".format(file_path, result))
        return return_value

    except Exception as e:
        return_value.update_sep(False, "Error writing to CSV: {}".format(e))
        return return_value

