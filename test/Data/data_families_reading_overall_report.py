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

from duHast.Revit.Family.Data.family_base_data_utils import nested_family, read_overall_family_data_list_from_directory


TEST_REPORT_DIRECTORY = r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData"

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
            
            (
            overall_family_base_root_data,
            overall_family_base_nested_data,
            ) = read_overall_family_data_list_from_directory(
                TEST_REPORT_DIRECTORY
            )
            
            message += "\noverall_family_base_root_data: {}".format(len(overall_family_base_root_data))
            message += "\noverall_family_base_nested_data: {}".format(len(overall_family_base_nested_data))

            # convert to string for comparison
            compare_family_base_root_data = []
            for entry in overall_family_base_root_data:
                compare_family_base_root_data.append("{}".format(entry))
            
            compare_family_base_nested_data=[]
            for entry in overall_family_base_nested_data:
                compare_family_base_nested_data.append("{}".format(entry))
            
            # set up expected result
            expected_result_family_root_data = [
                "root_family(name='Sample_Family_Twelf', category='Generic Annotations', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Generic Annotations\\\\Sample_Family_Twelf.rfa', parent=[], child=[])",
                "root_family(name='Sample_Family_Eleven', category='Generic Models', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Generic Models\\\\Sample_Family_Eleven.rfa', parent=[], child=[])",
                "root_family(name='Sample_Family_One', category='Plumbing Fixtures', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_One.rfa', parent=[], child=[])",
                "root_family(name='Sample_Family_Two', category='Furniture Systems', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Two.rfa', parent=[], child=[])",
                "root_family(name='Sample_Family_Fourteen', category='Generic Annotations', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Generic Annotations\\\\Sample_Family_Fourteen.rfa', parent=[], child=[])",
                "root_family(name='Sample_Family_Three', category='Specialty Equipment', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Three.rfa', parent=[], child=[])",
                "root_family(name='Sample_Family_Four', category='Plumbing Fixtures', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Plumbing Fixtures\\\\Sample_Family_Four.rfa', parent=[], child=[])",
                "root_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Section Marks\\\\Sample_Family_Thirteen.rfa', parent=[], child=[])",
                "root_family(name='Sample_Family_Five', category='Specialty Equipment', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Five.rfa', parent=[], child=[])",
                "root_family(name='Sample_Family_Six', category='Specialty Equipment', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Six.rfa', parent=[], child=[])",
                "root_family(name='Sample_Family_Seven', category='Electrical Fixtures', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Electrical Fixtures\\\\Sample_Family_Seven.rfa', parent=[], child=[])",
                "root_family(name='Sample_Family_Eight', category='Furniture Systems', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Furniture Systems\\\\Sample_Family_Eight.rfa', parent=[], child=[])",
                "root_family(name='Sample_Family_Nine', category='Furniture Systems', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Nine.rfa', parent=[], child=[])",
                "root_family(name='Sample_Family_Ten', category='Generic Annotations', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Generic Annotations\\\\Sample_Family_Ten.rfa', parent=[], child=[])",
            ]

            expected_result_family_nested_data = [
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Eleven', 'Sample_Family_Thirteen'], categoryPath=['Generic Models', 'Section Marks'], hostFamily=[])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_One', 'Sample_Family_Thirteen'], categoryPath=['Plumbing Fixtures', 'Section Marks'], hostFamily=[])",
                "nested_family(name='Sample_Family_Four', category='Plumbing Fixtures', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Four.rfa', rootPath=['Sample_Family_One', 'Sample_Family_Four'], categoryPath=['Plumbing Fixtures', 'Plumbing Fixtures'], hostFamily=[])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_One', 'Sample_Family_Four', 'Sample_Family_Thirteen'], categoryPath=['Plumbing Fixtures', 'Plumbing Fixtures', 'Section Marks'], hostFamily=[])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Two', 'Sample_Family_Thirteen'], categoryPath=['Furniture Systems', 'Section Marks'], hostFamily=[])",
                "nested_family(name='Sample_Family_Eight', category='Furniture Systems', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Eight.rfa', rootPath=['Sample_Family_Two', 'Sample_Family_Eight'], categoryPath=['Furniture Systems', 'Furniture Systems'], hostFamily=[])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Two', 'Sample_Family_Eight', 'Sample_Family_Thirteen'], categoryPath=['Furniture Systems', 'Furniture Systems', 'Section Marks'], hostFamily=[])",
                "nested_family(name='Sample_Family_Twelf', category='Generic Annotations', filePath='', rootPath=['Sample_Family_Fourteen', 'Sample_Family_Twelf'], categoryPath=['Generic Annotations', 'Generic Annotations'], hostFamily=[])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Three', 'Sample_Family_Thirteen'], categoryPath=['Specialty Equipment', 'Section Marks'], hostFamily=[])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Four', 'Sample_Family_Thirteen'], categoryPath=['Plumbing Fixtures', 'Section Marks'], hostFamily=[])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Five', 'Sample_Family_Thirteen'], categoryPath=['Specialty Equipment', 'Section Marks'], hostFamily=[])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Six', 'Sample_Family_Thirteen'], categoryPath=['Specialty Equipment', 'Section Marks'], hostFamily=[])",
                "nested_family(name='Sample_Family_Eleven', category='Generic Models', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Eleven.rfa', rootPath=['Sample_Family_Six', 'Sample_Family_Eleven'], categoryPath=['Specialty Equipment', 'Generic Models'], hostFamily=[])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Six', 'Sample_Family_Eleven', 'Sample_Family_Thirteen'], categoryPath=['Specialty Equipment', 'Generic Models', 'Section Marks'], hostFamily=[])",
                "nested_family(name='Sample_Family_Seven', category='Electrical Fixtures', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Seven.rfa', rootPath=['Sample_Family_Six', 'Sample_Family_Seven'], categoryPath=['Specialty Equipment', 'Electrical Fixtures'], hostFamily=[])",
                "nested_family(name='Sample_Family_Ten', category='Generic Annotations', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Ten.rfa', rootPath=['Sample_Family_Six', 'Sample_Family_Seven', 'Sample_Family_Ten'], categoryPath=['Specialty Equipment', 'Electrical Fixtures', 'Generic Annotations'], hostFamily=[])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Six', 'Sample_Family_Seven', 'Sample_Family_Thirteen'], categoryPath=['Specialty Equipment', 'Electrical Fixtures', 'Section Marks'], hostFamily=[])",
                "nested_family(name='Sample_Family_Fourteen', category='Generic Annotations', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Fourteen.rfa', rootPath=['Sample_Family_Six', 'Sample_Family_Seven', 'Sample_Family_Fourteen'], categoryPath=['Specialty Equipment', 'Electrical Fixtures', 'Generic Annotations'], hostFamily=[])",
                "nested_family(name='Sample_Family_Twelf', category='Generic Annotations', filePath='', rootPath=['Sample_Family_Six', 'Sample_Family_Seven', 'Sample_Family_Fourteen', 'Sample_Family_Twelf'], categoryPath=['Specialty Equipment', 'Electrical Fixtures', 'Generic Annotations', 'Generic Annotations'], hostFamily=[])",
                "nested_family(name='Sample_Family_Ten', category='Generic Annotations', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Ten.rfa', rootPath=['Sample_Family_Seven', 'Sample_Family_Ten'], categoryPath=['Electrical Fixtures', 'Generic Annotations'], hostFamily=[])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Seven', 'Sample_Family_Thirteen'], categoryPath=['Electrical Fixtures', 'Section Marks'], hostFamily=[])",
                "nested_family(name='Sample_Family_Fourteen', category='Generic Annotations', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Fourteen.rfa', rootPath=['Sample_Family_Seven', 'Sample_Family_Fourteen'], categoryPath=['Electrical Fixtures', 'Generic Annotations'], hostFamily=[])",
                "nested_family(name='Sample_Family_Twelf', category='Generic Annotations', filePath='', rootPath=['Sample_Family_Seven', 'Sample_Family_Fourteen', 'Sample_Family_Twelf'], categoryPath=['Electrical Fixtures', 'Generic Annotations', 'Generic Annotations'], hostFamily=[])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Eight', 'Sample_Family_Thirteen'], categoryPath=['Furniture Systems', 'Section Marks'], hostFamily=[])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Nine', 'Sample_Family_Thirteen'], categoryPath=['Furniture Systems', 'Section Marks'], hostFamily=[])",
                "nested_family(name='Sample_Family_Eight', category='Furniture Systems', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Eight.rfa', rootPath=['Sample_Family_Nine', 'Sample_Family_Eight'], categoryPath=['Furniture Systems', 'Furniture Systems'], hostFamily=[])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Nine', 'Sample_Family_Eight', 'Sample_Family_Thirteen'], categoryPath=['Furniture Systems', 'Furniture Systems', 'Section Marks'], hostFamily=[])",
            ]

            message += "\nroot result from data: {} \nvs \nexpected: {}".format(
                        "\n".join(sorted(compare_family_base_root_data)), "\n".join(sorted(expected_result_family_root_data))
            )

            message += "\nnested result from data: {} \nvs \nexpected: {}".format(
                        "\n".join(sorted(compare_family_base_nested_data)), "\n".join(sorted(expected_result_family_nested_data))
            )
            
            assert "\n".join(sorted(compare_family_base_root_data))=="\n".join(sorted(expected_result_family_root_data))
            assert "\n".join(sorted(compare_family_base_nested_data))=="\n".join(sorted(expected_result_family_nested_data))
            
        except Exception as e:
            flag = False
            message = (
                message
                + "\n"
                + ("An exception occurred in function {} : {}".format(self.test_name,e))
            )
        return flag, message
    