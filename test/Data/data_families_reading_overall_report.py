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
                "root_family(name='Sample_Family_Eight', category='Furniture Systems', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Furniture Systems\\\\Sample_Family_Eight.rfa', parent=[], child=[], report_data=['Sample_Family_Eight', 'Furniture Systems', 'Sample_Family_Eight', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Furniture Systems\\\\Sample_Family_Eight.rfa', 'Furniture Systems'])",
                "root_family(name='Sample_Family_Eleven', category='Generic Models', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Generic Models\\\\Sample_Family_Eleven.rfa', parent=[], child=[], report_data=['Sample_Family_Eleven', 'Generic Models', 'Sample_Family_Eleven', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Generic Models\\\\Sample_Family_Eleven.rfa', 'Generic Models'])",
                "root_family(name='Sample_Family_Five', category='Specialty Equipment', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Five.rfa', parent=[], child=[], report_data=['Sample_Family_Five', 'Specialty Equipment', 'Sample_Family_Five', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Five.rfa', 'Specialty Equipment'])",
                "root_family(name='Sample_Family_Four', category='Plumbing Fixtures', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Plumbing Fixtures\\\\Sample_Family_Four.rfa', parent=[], child=[], report_data=['Sample_Family_Four', 'Plumbing Fixtures', 'Sample_Family_Four', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Plumbing Fixtures\\\\Sample_Family_Four.rfa', 'Plumbing Fixtures'])",
                "root_family(name='Sample_Family_Fourteen', category='Generic Annotations', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Generic Annotations\\\\Sample_Family_Fourteen.rfa', parent=[], child=[], report_data=['Sample_Family_Fourteen', 'Generic Annotations', 'Sample_Family_Fourteen', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Generic Annotations\\\\Sample_Family_Fourteen.rfa', 'Generic Annotations'])",
                "root_family(name='Sample_Family_Nine', category='Furniture Systems', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Nine.rfa', parent=[], child=[], report_data=['Sample_Family_Nine', 'Furniture Systems', 'Sample_Family_Nine', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Nine.rfa', 'Furniture Systems'])",
                "root_family(name='Sample_Family_One', category='Plumbing Fixtures', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_One.rfa', parent=[], child=[], report_data=['Sample_Family_One', 'Plumbing Fixtures', 'Sample_Family_One', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_One.rfa', 'Plumbing Fixtures'])",
                "root_family(name='Sample_Family_Seven', category='Electrical Fixtures', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Electrical Fixtures\\\\Sample_Family_Seven.rfa', parent=[], child=[], report_data=['Sample_Family_Seven', 'Electrical Fixtures', 'Sample_Family_Seven', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Electrical Fixtures\\\\Sample_Family_Seven.rfa', 'Electrical Fixtures'])",
                "root_family(name='Sample_Family_Six', category='Specialty Equipment', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Six.rfa', parent=[], child=[], report_data=['Sample_Family_Six', 'Specialty Equipment', 'Sample_Family_Six', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Six.rfa', 'Specialty Equipment'])",
                "root_family(name='Sample_Family_Ten', category='Generic Annotations', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Generic Annotations\\\\Sample_Family_Ten.rfa', parent=[], child=[], report_data=['Sample_Family_Ten', 'Generic Annotations', 'Sample_Family_Ten', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Generic Annotations\\\\Sample_Family_Ten.rfa', 'Generic Annotations'])",
                "root_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Section Marks\\\\Sample_Family_Thirteen.rfa', parent=[], child=[], report_data=['Sample_Family_Thirteen', 'Section Marks', 'Sample_Family_Thirteen', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Section Marks\\\\Sample_Family_Thirteen.rfa', 'Section Marks'])",
                "root_family(name='Sample_Family_Three', category='Specialty Equipment', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Three.rfa', parent=[], child=[], report_data=['Sample_Family_Three', 'Specialty Equipment', 'Sample_Family_Three', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Three.rfa', 'Specialty Equipment'])",
                "root_family(name='Sample_Family_Twelf', category='Generic Annotations', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Generic Annotations\\\\Sample_Family_Twelf.rfa', parent=[], child=[], report_data=['Sample_Family_Twelf', 'Generic Annotations', 'Sample_Family_Twelf', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\combined\\\\Generic Annotations\\\\Sample_Family_Twelf.rfa', 'Generic Annotations'])",
                "root_family(name='Sample_Family_Two', category='Furniture Systems', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Two.rfa', parent=[], child=[], report_data=['Sample_Family_Two', 'Furniture Systems', 'Sample_Family_Two', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Two.rfa', 'Furniture Systems'])",
            ]

            expected_result_family_nested_data = [
                "nested_family(name='Sample_Family_Eight', category='Furniture Systems', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Eight.rfa', rootPath=['Sample_Family_Nine', 'Sample_Family_Eight'], categoryPath=['Furniture Systems', 'Furniture Systems'], hostFamily=[], report_data=['Sample_Family_Nine :: Sample_Family_Eight', 'Furniture Systems :: Furniture Systems', 'Sample_Family_Eight', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Eight.rfa', 'Furniture Systems'])",
                "nested_family(name='Sample_Family_Eight', category='Furniture Systems', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Eight.rfa', rootPath=['Sample_Family_Two', 'Sample_Family_Eight'], categoryPath=['Furniture Systems', 'Furniture Systems'], hostFamily=[], report_data=['Sample_Family_Two :: Sample_Family_Eight', 'Furniture Systems :: Furniture Systems', 'Sample_Family_Eight', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Eight.rfa', 'Furniture Systems'])",
                "nested_family(name='Sample_Family_Eleven', category='Generic Models', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Eleven.rfa', rootPath=['Sample_Family_Six', 'Sample_Family_Eleven'], categoryPath=['Specialty Equipment', 'Generic Models'], hostFamily=[], report_data=['Sample_Family_Six :: Sample_Family_Eleven', 'Specialty Equipment :: Generic Models', 'Sample_Family_Eleven', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Eleven.rfa', 'Generic Models'])",
                "nested_family(name='Sample_Family_Four', category='Plumbing Fixtures', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Four.rfa', rootPath=['Sample_Family_One', 'Sample_Family_Four'], categoryPath=['Plumbing Fixtures', 'Plumbing Fixtures'], hostFamily=[], report_data=['Sample_Family_One :: Sample_Family_Four', 'Plumbing Fixtures :: Plumbing Fixtures', 'Sample_Family_Four', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Four.rfa', 'Plumbing Fixtures'])",
                "nested_family(name='Sample_Family_Fourteen', category='Generic Annotations', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Fourteen.rfa', rootPath=['Sample_Family_Seven', 'Sample_Family_Fourteen'], categoryPath=['Electrical Fixtures', 'Generic Annotations'], hostFamily=[], report_data=['Sample_Family_Seven :: Sample_Family_Fourteen', 'Electrical Fixtures :: Generic Annotations', 'Sample_Family_Fourteen', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Fourteen.rfa', 'Generic Annotations'])",
                "nested_family(name='Sample_Family_Fourteen', category='Generic Annotations', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Fourteen.rfa', rootPath=['Sample_Family_Six', 'Sample_Family_Seven', 'Sample_Family_Fourteen'], categoryPath=['Specialty Equipment', 'Electrical Fixtures', 'Generic Annotations'], hostFamily=[], report_data=['Sample_Family_Six :: Sample_Family_Seven :: Sample_Family_Fourteen', 'Specialty Equipment :: Electrical Fixtures :: Generic Annotations', 'Sample_Family_Fourteen', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Fourteen.rfa', 'Generic Annotations'])",
                "nested_family(name='Sample_Family_Seven', category='Electrical Fixtures', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Seven.rfa', rootPath=['Sample_Family_Six', 'Sample_Family_Seven'], categoryPath=['Specialty Equipment', 'Electrical Fixtures'], hostFamily=[], report_data=['Sample_Family_Six :: Sample_Family_Seven', 'Specialty Equipment :: Electrical Fixtures', 'Sample_Family_Seven', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Seven.rfa', 'Electrical Fixtures'])",
                "nested_family(name='Sample_Family_Ten', category='Generic Annotations', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Ten.rfa', rootPath=['Sample_Family_Seven', 'Sample_Family_Ten'], categoryPath=['Electrical Fixtures', 'Generic Annotations'], hostFamily=[], report_data=['Sample_Family_Seven :: Sample_Family_Ten', 'Electrical Fixtures :: Generic Annotations', 'Sample_Family_Ten', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Ten.rfa', 'Generic Annotations'])",
                "nested_family(name='Sample_Family_Ten', category='Generic Annotations', filePath='C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Ten.rfa', rootPath=['Sample_Family_Six', 'Sample_Family_Seven', 'Sample_Family_Ten'], categoryPath=['Specialty Equipment', 'Electrical Fixtures', 'Generic Annotations'], hostFamily=[], report_data=['Sample_Family_Six :: Sample_Family_Seven :: Sample_Family_Ten', 'Specialty Equipment :: Electrical Fixtures :: Generic Annotations', 'Sample_Family_Ten', 'C:\\\\Users\\\\jchristel\\\\dev\\\\test_lib\\\\Sample_Family_Ten.rfa', 'Generic Annotations'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Eight', 'Sample_Family_Thirteen'], categoryPath=['Furniture Systems', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_Eight :: Sample_Family_Thirteen', 'Furniture Systems :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Eleven', 'Sample_Family_Thirteen'], categoryPath=['Generic Models', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_Eleven :: Sample_Family_Thirteen', 'Generic Models :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Five', 'Sample_Family_Thirteen'], categoryPath=['Specialty Equipment', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_Five :: Sample_Family_Thirteen', 'Specialty Equipment :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Four', 'Sample_Family_Thirteen'], categoryPath=['Plumbing Fixtures', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_Four :: Sample_Family_Thirteen', 'Plumbing Fixtures :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Nine', 'Sample_Family_Eight', 'Sample_Family_Thirteen'], categoryPath=['Furniture Systems', 'Furniture Systems', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_Nine :: Sample_Family_Eight :: Sample_Family_Thirteen', 'Furniture Systems :: Furniture Systems :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Nine', 'Sample_Family_Thirteen'], categoryPath=['Furniture Systems', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_Nine :: Sample_Family_Thirteen', 'Furniture Systems :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_One', 'Sample_Family_Four', 'Sample_Family_Thirteen'], categoryPath=['Plumbing Fixtures', 'Plumbing Fixtures', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_One :: Sample_Family_Four :: Sample_Family_Thirteen', 'Plumbing Fixtures :: Plumbing Fixtures :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_One', 'Sample_Family_Thirteen'], categoryPath=['Plumbing Fixtures', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_One :: Sample_Family_Thirteen', 'Plumbing Fixtures :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Seven', 'Sample_Family_Thirteen'], categoryPath=['Electrical Fixtures', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_Seven :: Sample_Family_Thirteen', 'Electrical Fixtures :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Six', 'Sample_Family_Eleven', 'Sample_Family_Thirteen'], categoryPath=['Specialty Equipment', 'Generic Models', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_Six :: Sample_Family_Eleven :: Sample_Family_Thirteen', 'Specialty Equipment :: Generic Models :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Six', 'Sample_Family_Seven', 'Sample_Family_Thirteen'], categoryPath=['Specialty Equipment', 'Electrical Fixtures', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_Six :: Sample_Family_Seven :: Sample_Family_Thirteen', 'Specialty Equipment :: Electrical Fixtures :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Six', 'Sample_Family_Thirteen'], categoryPath=['Specialty Equipment', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_Six :: Sample_Family_Thirteen', 'Specialty Equipment :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Three', 'Sample_Family_Thirteen'], categoryPath=['Specialty Equipment', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_Three :: Sample_Family_Thirteen', 'Specialty Equipment :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Two', 'Sample_Family_Eight', 'Sample_Family_Thirteen'], categoryPath=['Furniture Systems', 'Furniture Systems', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_Two :: Sample_Family_Eight :: Sample_Family_Thirteen', 'Furniture Systems :: Furniture Systems :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Thirteen', category='Section Marks', filePath='', rootPath=['Sample_Family_Two', 'Sample_Family_Thirteen'], categoryPath=['Furniture Systems', 'Section Marks'], hostFamily=[], report_data=['Sample_Family_Two :: Sample_Family_Thirteen', 'Furniture Systems :: Section Marks', 'Sample_Family_Thirteen', '', 'Section Marks'])",
                "nested_family(name='Sample_Family_Twelf', category='Generic Annotations', filePath='', rootPath=['Sample_Family_Fourteen', 'Sample_Family_Twelf'], categoryPath=['Generic Annotations', 'Generic Annotations'], hostFamily=[], report_data=['Sample_Family_Fourteen :: Sample_Family_Twelf', 'Generic Annotations :: Generic Annotations', 'Sample_Family_Twelf', '', 'Generic Annotations'])",
                "nested_family(name='Sample_Family_Twelf', category='Generic Annotations', filePath='', rootPath=['Sample_Family_Seven', 'Sample_Family_Fourteen', 'Sample_Family_Twelf'], categoryPath=['Electrical Fixtures', 'Generic Annotations', 'Generic Annotations'], hostFamily=[], report_data=['Sample_Family_Seven :: Sample_Family_Fourteen :: Sample_Family_Twelf', 'Electrical Fixtures :: Generic Annotations :: Generic Annotations', 'Sample_Family_Twelf', '', 'Generic Annotations'])",
                "nested_family(name='Sample_Family_Twelf', category='Generic Annotations', filePath='', rootPath=['Sample_Family_Six', 'Sample_Family_Seven', 'Sample_Family_Fourteen', 'Sample_Family_Twelf'], categoryPath=['Specialty Equipment', 'Electrical Fixtures', 'Generic Annotations', 'Generic Annotations'], hostFamily=[], report_data=['Sample_Family_Six :: Sample_Family_Seven :: Sample_Family_Fourteen :: Sample_Family_Twelf', 'Specialty Equipment :: Electrical Fixtures :: Generic Annotations :: Generic Annotations', 'Sample_Family_Twelf', '', 'Generic Annotations'])",
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
    
