"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains data read from file tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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
import sys

from test.utils import test

from duHast.Revit.Family.Data.family_base_data_utils import cull_nested_base_data_blocks, read_overall_family_data_list_from_directory
from duHast.Utilities.files_io import get_directory_path_from_file_path

TEST_REPORT_DIRECTORY = os.path.join(get_directory_path_from_file_path(__file__), "ReadReport_01")

class DataCullingNestedFamilies(test.Test):
    
    def __init__(self):
        # store document in base class
        super(DataCullingNestedFamilies, self).__init__(test_name="data_culling_nested_families")


    def test(self):
        """
        Culls nested family data by removing all nested families from the data set but the longest uniques root path.

        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "-"
        try:

            (
            overall_family_base_root_data,
            overall_family_base_nested_data,
            ) = read_overall_family_data_list_from_directory(
                TEST_REPORT_DIRECTORY
            )

            
            # set up expected result
            expected_result = []

            cull = None
            try:
                # cull the data block
                cull = cull_nested_base_data_blocks(overall_family_base_root_data, overall_family_base_nested_data)
            except Exception as e:
                message += "\nexception in culling data block\n {} \n".format(e)
            
            compare_list = []
            for fam in cull:
                compare_list.append("{}".format(fam))
            
            message += "\nresult from data: {} \nvs \nexpected: {}".format(
                       "\n".join(sorted(compare_list)), "\n".join(sorted(expected_result))
            )
            
            
            # setup 
        except Exception as e:
            flag = False
            message = (
                message
                + "\n"
                + ("An exception occurred in function {} : {}".format(self.test_name,e))
            )
        return flag, message
    
