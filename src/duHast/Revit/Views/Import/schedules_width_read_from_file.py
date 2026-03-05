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

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_csv import  read_csv_file

def read_column_width_data_file(file_path):
    """
    Reads the column width data from a csv file and returns it as a dictionary of dictionaries, where the key is the schedule id and the values are 
    the field name (key) and column width (value) to set.

    :param file_path: The file path of the csv file to read.
    :type file_path: str

    :return: A list of dictionaries containing the schedule name, field name and column width to set.
    :rtype: dict[int, dict[str, int]]
    """

    # set up return value
    return_value = Result()

    try:
        read_csv_file_result = read_csv_file(file_path)

        if not read_csv_file_result.status:
            raise Exception(read_csv_file_result.message)
        
        return_value.append_message("Successfully read column width data from file.")

        lines = read_csv_file_result.result

        # set up a list to hold the data
        data = {}

        if len(lines) == 0:
            raise Exception("No data found in file.")
        
        # loop through the lines and extract schedule id as integer, field name and column width as integer
        for line in lines:

            # check for sufficient data in line, should be at least 3 entries (schedule id, field name and column width)
            if len(line) < 3:
                return_value.append_message("Skipping line with insufficient data: {}".format(line))
                continue
            
            # first entry is the id, followed by pairs of column name and column width
            schedule_id = int(line[0])
            data[schedule_id] = {}
            column_data = line[1:]

            for i in range(0, len(column_data), 2):
                field_name = column_data[i]
               
                width_string = column_data[i+1]
                column_width = float(width_string)
                
                data[schedule_id][field_name] = column_width

        return_value.status = True
        return_value.result.append(data)

    except Exception as e:
        return_value.status = False
        return_value.append_message(str(e))

    return return_value