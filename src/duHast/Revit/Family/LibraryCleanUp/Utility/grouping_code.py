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

from duHast.Utilities.files_csv import read_csv_file

def clean_code(code):
    """
    Cleans the grouping code by removing any sub codes after a dot.
    """
    if code is None:
        return None
    
    # remove any sub codes after a dot
    if '.' in code:
        code = code.split('.')[0]
    
    return code


def convert_to_file_name_code(code):
    """
    Converts the grouping code to a file name safe format.
    """

    # return code as is for now
    return code

    # if code is None:
    #     return None
    
    # # replace "-" with "_"
    # code = code.replace('-', '_')
    
    # return code


def load_group_code_description(file_path):
    """
    Loads the grouping code and description from a CSV file.
    
    :param file_path: The path to the CSV file containing the grouping codes and descriptions.
    :return: A dictionary mapping cleaned grouping codes to their descriptions.
    """

    code_description_map = {}
    try:
        read_result = read_csv_file(file_path=file_path)
        
        if not read_result.status:
            return None
        
        code_description_map = {}
        
        # ignore header row
        if len(read_result.result) == 0:
            return  None
        
        # iterate over the rows and create a map of code to description
        # ignore header row
        for i in range(1, len(read_result.result)):
            row = read_result.result[i]
            if len(row) < 2:
                continue
            code = row[0]
            family_code = row[1]
            description = row[2]
            
            # add to map
            code_description_map[code] = (family_code, description)
    
    except Exception as e:
        print("Error loading grouping codes from file {}: {}".format(file_path, e))
        return None
    

    return code_description_map