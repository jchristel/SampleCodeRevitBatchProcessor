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

from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.Objects.result import Result
from export.docManagerIntegration.Objects.DocManagerRevData import DocManagerRevData

def get_revision_data(file_path):
    
    return_value = Result()
    
    try:
        # read csv file
        csv_data_result = read_csv_file(file_path)
        
        if not csv_data_result.status:
            message = "Failed to read revision data from file: {}".format(file_path)
            return_value.update_sep(False, message)
            return return_value
        
        # get the csv data from the result
        csv_data = csv_data_result.result
        
        # process csv data
        revisions = []
        
        # loop over revision but skip the first row as it is the header
        for row in csv_data[1:]:
            revision = DocManagerRevData(
                date=row[DocManagerRevData.index_date],
                description=row[DocManagerRevData.index_description],
                database_id=row[DocManagerRevData.index_database_id]
            )
            revisions.append(revision)
        
        return_value.update_sep(True, "Successfully read revision data.")
        return_value.result.append(revisions)
        return return_value
    except Exception as e:
        message = "Error getting revision data from file: {}. Error: {}".format(file_path, str(e))
        return_value.update_sep(False, message)
        return return_value