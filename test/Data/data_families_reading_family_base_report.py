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
from duHast.Utilities.files_io import get_directory_path_from_file_path

TEST_REPORT_DIRECTORY = os.path.join(get_directory_path_from_file_path(__file__), "ReadReport_01")

class DataReadFamiliesBaseReport(test.Test):
    
    def __init__(self):
        # store document in base class
        super(DataReadFamiliesBaseReport, self).__init__(test_name="read overall family data report")


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
                "FamilyBaseDataCombinedReport_multiple.csv":(True,5,[
                    ["FamilyBase","Sample_Family_Eight","Furniture Systems","Sample_Family_Eight",r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa"],
                    ["FamilyBase","Sample_Family_Eight :: Sample_Family_Thirteen","Furniture Systems :: Section Marks","Sample_Family_Thirteen","-"],
                    ["FamilyBase","Sample_Family_Ten","Generic Annotations","Sample_Family_Ten",r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa"],
                    ["FamilyBase","Sample_Family_Six","Specialty Equipment","Sample_Family_Six",r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa"],
                    ["FamilyBase","Sample_Family_Six :: Sample_Family_Thirteen","Specialty Equipment :: Section Marks","Sample_Family_Thirteen","-"]
                ]),
                "FamilyBaseDataCombinedReport_single.csv":(True,1,[
                    ["FamilyBase","Sample_Family_Eight","Furniture Systems","Sample_Family_Eight",r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa"]
                ]),
            }

            for test_file, test_result in test_files.items():
                # read overall family data
                family_base_data_result = read_family_base_data(os.path.join(TEST_REPORT_DIRECTORY, test_file))
                message = message + "\n" + family_base_data_result.message

                message = message + "\n" + "...expecting status {} and got {}".format(test_result[0], family_base_data_result.status)
                assert family_base_data_result.status == test_result[0]
                message = message + "\n" + "...expecting number of entries {} and got {}".format(test_result[1], len(family_base_data_result.result))
                assert len(family_base_data_result.result) == test_result[1]
                
                # check conversion to storage data was successful
                if len(family_base_data_result.result) > 0:
                    for i in range(len(family_base_data_result.result)):
                        message = message + "\n" + "...expecting data {} in list but no match".format(family_base_data_result.result[i].get_data_values_as_list_of_strings())
                        assert family_base_data_result.result[i].get_data_values_as_list_of_strings() in test_result[2]

        except Exception as e:
            flag = False
            message = (
                message
                + "\n"
                + ("An exception occurred in function {} : {}".format(self.test_name,e))
            )
        return flag, message
    
