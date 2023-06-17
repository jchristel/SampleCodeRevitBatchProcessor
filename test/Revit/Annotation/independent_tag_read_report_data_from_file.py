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
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import os

import revit_script_util
import Autodesk.Revit.DB as rdb
from test.Revit.TestUtils import revit_test
from duHast.Revit.Annotation.Reporting.tags_independent_report import (
    get_tag_instances_report_data,
)

# filter imports
from duHast.Revit.Common import custom_element_filter_actions as elCustomFilterAction
from duHast.Revit.Common import custom_element_filter_tests as elCustomFilterTest
from duHast.Revit.Common import custom_element_filter as rCusFilter
from duHast.Utilities.files_json import write_json_to_file, read_json_data_from_file

from duHast.Utilities import result as res
from duHast.Utilities.console_out import output
from test.Revit.Annotation.annotations_report import (
    REVIT_INDEPENDENT_TAG_TEST_FILE_NAME,
    MULTI_CATEGORY_TAG_TYPE_NAME,
    REVIT_INDEPENDENT_TAG_REPORT_FILE_NAME,
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

        return return_value
