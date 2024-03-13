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

from duHast.Revit.Family.Data.family_base_data_utils import nested_family, _check_data_blocks_for_overlap, _cull_data_block

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
            # set up test family instances
            test_fam_1 = nested_family(
                    name="test 1",
                    category = "a category",
                    filePath=r"\a test path\test 1",
                    rootPath="a host family::test 1",
                    categoryPath ="a_category::a_category",
                    hostFamily="a host family"
                )
            test_fam_2 = nested_family(
                    name="test 2",
                    category = "a category",
                    filePath=r"\a test path\test 2",
                    rootPath="a host family::test 1::test 2",
                    categoryPath ="a_category::a_category::a_category",
                    hostFamily="test 1"
                )
            test_fam_3 = nested_family(
                    name="test 3",
                    category = "a category",
                    filePath=r"\a test path\test 3",
                    rootPath="a host family::test 1::test 2::test 3",
                    categoryPath ="a_category::a_category::a_category::a_category",
                    hostFamily="test 2"
                )
            test_fam_4 = nested_family(
                    name="test 4",
                    category = "a category",
                    filePath=r"\a test path\test 3",
                    rootPath="a host family::test 1::test 2::test 4",
                    categoryPath ="a_category::a_category::a_category::a_category",
                    hostFamily="test 2"
                )
            test_fam_5 = nested_family(
                    name="test 5",
                    category = "a category",
                    filePath=r"\a test path\test 3",
                    rootPath="a host family::test 1::test 5",
                    categoryPath ="a_category::a_category::a_category::a_category",
                    hostFamily="test 1"
                )
            
            # setup test data block
            data = [
                test_fam_1,
            ]

            # set up expected result
            expected_result = [test_fam_1]

            cull = None
            try:
                # cull the data block
                cull = _cull_data_block(family_base_nested_data_block=data)
            except Exception as e:
                message += "\nexception in culling data block\n {} \n".format(e)
                

            message += "\nresult from data: {} \nvs \nexpected: {}".format(
                        sorted(cull), sorted(expected_result)
            )
            
            # it should only return the longest unique root path which is family 3 in the test data
            assert sorted(cull) == sorted(expected_result)

            # setup test data block
            data = [
                test_fam_1,
                test_fam_2,
                test_fam_3,
            ]

            # set up expected result
            expected_result = [test_fam_3]

            cull = None
            try:
                # cull the data block
                cull = _cull_data_block(family_base_nested_data_block=data)
            except Exception as e:
                message += "\nexception in culling data block\n {} \n".format(e)
                

            message += "\nresult from data: {} \nvs \nexpected: {}".format(
                        sorted(cull), sorted(expected_result)
            )
            
            # it should only return the longest unique root path which is family 3 in the test data
            assert sorted(cull) == sorted(expected_result)
            
            # test nesting with multiple branches
            data = [
                test_fam_1,
                test_fam_2,
                test_fam_3,
                test_fam_4,
                test_fam_5
            ]

            # set up expected result
            expected_result = [test_fam_3, test_fam_4, test_fam_5]

            cull = None
            try:
                # cull the data block
                cull = _cull_data_block(family_base_nested_data_block=data)
            except Exception as e:
                message += "\nexception in culling data block\n {} \n".format(e)
            
            message += "\nresult from data: {} \nvs \nexpected: {}".format(
                        sorted(cull), sorted(expected_result)
            )

            # it should only return the longest unique root path which are 3 families in the test data
            assert sorted(cull) == sorted(expected_result)

            flag = False
        except Exception as e:
            flag = False
            message = (
                message
                + "\n"
                + ("An exception occurred in function {} : {}".format(self.test_name,e))
            )
        return flag, message
    
