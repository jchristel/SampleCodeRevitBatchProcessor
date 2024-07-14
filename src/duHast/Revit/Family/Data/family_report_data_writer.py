"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing functions to write report files from data previously read from file.
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

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import file_exist
from duHast.Utilities.directory_io import directory_exists


# import report names and identifiers
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_family_base_processor,
)
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_family_base_report_name,
)

from duHast.Revit.Categories.Data.Objects.category_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_category_processor,
)
from duHast.Revit.Categories.Data.Objects.category_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_category_report_name,
)

from duHast.Revit.LinePattern.Data.Objects.line_pattern_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_line_pattern_processor,
)
from duHast.Revit.LinePattern.Data.Objects.line_pattern_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_line_pattern_report_name,
)

from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_shared_parameter_processor,
)
from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_shared_parameter_report_name,
)

from duHast.Revit.Warnings.Data.Objects.warnings_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_warnings_processor,
)
from duHast.Revit.Warnings.Data.Objects.warnings_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_warnings_report_name,
)


# contains the report name depending on data type
REPORT_NAME_BY_DATA_TYPE = {
    data_type_family_base_processor:data_type_family_base_report_name,
    data_type_category_processor:data_type_category_report_name,
    data_type_line_pattern_processor:data_type_line_pattern_report_name,
    data_type_shared_parameter_processor:data_type_shared_parameter_report_name,
    data_type_warnings_processor:data_type_warnings_report_name,
}



def get_storage_data(family_data):
    pass



def write_data_from_families_to_files(family_data, directory_path):
    
    return_value = Result()

    try:
        # tests first
        if isinstance(family_data, list)==False:
            raise TypeError("family_data needs to be a list. Got {} instead.".format(type(family_data)))
        
        if isinstance(directory_path,str)==False:
            raise TypeError("directory_path needs to be a string. Got {} instead".format(type(directory_path)))
        
        if (directory_exists(directory_path=directory_path) == False):
            raise ValueError("Directory: {} does not exist.".format(directory_path))
    
        # get storage data
        storage_data_dic = get_storage_data(family_data)
        
        # need to have at least one entry:
        if(len(storage_data_dic)<1):
            raise ValueError("Failed to get any storage data from family data past in.")
        
        for key, item in storage_data_dic.items():
            # write to file
            pass
    
    except Exception as e:
        return_value.update_sep(False, "Failed to write family storage data to file with exception: {}".format(e))
