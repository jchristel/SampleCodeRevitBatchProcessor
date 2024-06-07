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

from duHast.Revit.Family.Data.family_report_reader import read_family_base_data
from duHast.Revit.Family.Data.family_base_data_utils import nested_family, read_overall_family_data_list_from_directory
from duHast.Utilities.files_io import get_directory_path_from_file_path

TEST_REPORT_DIRECTORY = os.path.join(get_directory_path_from_file_path(__file__), "ReadReport_01")

class DataReadFamiliesReport(test.Test):
    
    def __init__(self):
        # store document in base class
        super(DataReadFamiliesReport, self).__init__(test_name="read overall family data report")


    def test(self):
        """
        Reads overall family data report.

        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "\n-"
        try:
            
            # 4 test files
            test_files = {
                "FamilyBaseDataCombinedReport_empty_file.csv":(False,0,[]),
                "FamilyBaseDataCombinedReport_empty.csv":(False,0,[]),
                "FamilyBaseDataCombinedReport_multiple.csv":(True,4,[
                    ["Sample_Family_Eight,Furniture Systems,Sample_Family_Eight,C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa"],
                    [],
                    [],
                    [],
                ]),
                "FamilyBaseDataCombinedReport_single.csv":(True,1,[
                    ["Sample_Family_Eight,Furniture Systems,Sample_Family_Eight,C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa"]
                ]),
            }

            for test_file, test_result in test_files.items():
                # read overall family data
                family_base_data_result = read_family_base_data(os.path.join(TEST_REPORT_DIRECTORY, test_file))
                message = message + "\n" + family_base_data_result.message
            flag = False
                

            
            
            #assert "\n".join(sorted(compare_family_base_root_data))=="\n".join(sorted(expected_result_family_root_data))
            #assert "\n".join(sorted(compare_family_base_nested_data))=="\n".join(sorted(expected_result_family_nested_data))
            
        except Exception as e:
            flag = False
            message = (
                message
                + "\n"
                + ("An exception occurred in function {} : {}".format(self.test_name,e))
            )
        return flag, message
    
