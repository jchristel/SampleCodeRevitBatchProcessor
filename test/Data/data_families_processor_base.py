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
from duHast.Revit.Family.Data.Objects.family_base_data_processor import FamilyBaseProcessor
from duHast.Revit.Family.Data.Objects.family_base_data_storage import FamilyBaseDataStorage
class DataProcessorBaseData(test.Test):
    
    def __init__(self):
        # store document in base class
        super(DataProcessorBaseData, self).__init__(test_name="read overall family data report")

    def test(self):
        """
        Reads overall family data report.

        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "\n-"
        try:

            # test family base data storage retrieval from processor
            # ini empty processor
            dummy = FamilyBaseProcessor()

            # test data format data_type, root_name_path, root_category_path, family_name, family_file_path
            storage_test_data = [
                [dummy.data_type,  "sample_root", "sample_category", "sample_family_name","sample_file_path"],
                [dummy.data_type,  "sample_root::sample_root_nested", "sample_category::sample_category_nested", "sample_family_name_nested","sample_file_path_nested"],
            ]

            # populate processor with sample data
            for sample_data in storage_test_data:
                sample_storage = FamilyBaseDataStorage(
                    data_type=sample_data[0],
                    root_name_path=sample_data[1],
                    root_category_path=sample_data[2],
                    family_name=sample_data[3],
                    family_file_path=sample_data[4]
                )
                dummy.data.append(sample_storage)


            # test output
            print(dummy.get_data())
            print(dummy.get_data_string_list())
            
        except Exception as e:
            flag = False
            message = (
                message
                + "\n"
                + ("An exception occurred in function {} : {}".format(self.test_name,e))
            )
        return flag, message