"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit independent report read data from file tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

import os

import revit_script_util
from test.Revit.TestUtils import revit_test
from duHast.Revit.Annotation.Reporting.tags_independent_report import (
    get_tag_instances_report_data,
)

# filter imports
from duHast.Revit.Common import custom_element_filter_actions as elCustomFilterAction
from duHast.Revit.Common import custom_element_filter_tests as elCustomFilterTest
from duHast.Revit.Common import custom_element_filter as rCusFilter
from duHast.Utilities.files_json import write_json_to_file, read_json_data_from_file

from duHast.Utilities.Objects import result as res
from duHast.Utilities.console_out import output
from test.Revit.Annotation.annotations_report import (
    REVIT_INDEPENDENT_TAG_TEST_FILE_NAME,
    MULTI_CATEGORY_TAG_TYPE_NAME,
)


class ReadIndependentTagReportDataFromFile(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(ReadIndependentTagReportDataFromFile, self).__init__(
            doc=doc,
            test_name="read_tag_independent_data_from_file",
            requires_temp_dir=True,
        )

    def action_out(self, message):
        """
        Output function for filter actions

        :param message: the message to be printed out
        :type message: str
        """
        output(
            message,
            revit_script_util.Output,
        )

    def action_family_type_name_contains(self, doc, element_id):
        """
        Set up a function checking whether tag type name contains

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param element_id: id of element to be checked against condition
        :type element_id: Autodesk.Revit.DB.ElementId

        :return: True if element name contain 'tbc', otherwise False
        :rtype: bool
        """

        test = elCustomFilterAction.action_element_property_contains_any_of_values(
            [MULTI_CATEGORY_TAG_TYPE_NAME],
            elCustomFilterTest.value_in_name,
            self.action_out,
        )

        flag = test(doc, element_id)
        return flag

    def test(self):
        """
        read_tag_independent_data_from_file test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if tag instance data was retrieved successfully, otherwise False
                - .message will contain result(s) vs expected result(s)
                - . result (empty list)

                on exception:

                - .result Will be False
                - .message will contain exception message.
                - . result (empty list)
        :rtype: :class:`.Result`
        """

        return_value = res.Result()

        # set up a tag filter by name
        FILTER_TAGS = rCusFilter.RevitCustomElementFilter(
            [self.action_family_type_name_contains]
        )
        try:

            # get instance report data
            tag_data = get_tag_instances_report_data(
                doc=self.document,
                revit_file_path=REVIT_INDEPENDENT_TAG_TEST_FILE_NAME,
                custom_element_filter=FILTER_TAGS,
            )

            data_file_name = os.path.join(
                self.tmp_dir, REVIT_INDEPENDENT_TAG_TEST_FILE_NAME
            )
            
            # write data to file
            write_json_file_result = write_json_to_file(json_data=tag_data, data_output_file_path=data_file_name)
            return_value.append_message(
                " writing json file: {}".format(write_json_file_result.status)
            )
            assert (write_json_file_result.status==True)
            # read data back in from file into a list of dictionaries
            read_data = read_json_data_from_file(data_file_name)
            # check what came back
            return_value.append_message(
                " result: {} \n expected: {} ".format(sorted(read_data), sorted(tag_data))
            )
            assert sorted(read_data) == sorted(tag_data)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name, e),
            )
        finally:
            # clean up temp directory
            clean_up = self.clean_up()
            return_value.update_sep(
                clean_up,
                "Attempted to clean up temp directory with result: {}".format(clean_up),
            )
        return return_value
