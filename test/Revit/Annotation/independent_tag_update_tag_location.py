"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit independent tag update location tests . 
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

import revit_script_util

import Autodesk.Revit.DB as rdb
from test.Revit.TestUtils import revit_test
from duHast.Revit.Annotation.Reporting.gen_annotations_instance_report_header import (
    TAG_ID,
    TAG_HEAD_LOCATION,
)
from duHast.Revit.Annotation.independent_tags import get_all_independent_tags
from duHast.Revit.Annotation.independent_tags_modify_properties import (
    update_tag_location,
    move_tag,
)
from duHast.Revit.Annotation.Reporting.tags_independent_report import (
    get_tag_instances_report_data,
)

# filter imports
from duHast.Revit.Common import custom_element_filter_actions as elCustomFilterAction
from duHast.Revit.Common import custom_element_filter_tests as elCustomFilterTest
from duHast.Revit.Common import custom_element_filter as rCusFilter

from duHast.Utilities import result as res
from duHast.Utilities.console_out import output

from test.Revit.Annotation.annotations_report import (
    REVIT_INDEPENDENT_TAG_TEST_FILE_NAME,
    MULTI_CATEGORY_TAG_TYPE_NAME,
)


class IndependentTagUpdateLocation(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(IndependentTagUpdateLocation, self).__init__(
            doc=doc, test_name="update_tag_location"
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
        update_tag_location test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if all tag instance where moved to 0,0,0 successfully, otherwise False
                - .message will contain result(s) vs expected result(s)
                - . result (empty list)

                on exception:

                - .result Will be False
                - .message will contain exception message.
                - . result (empty list)
        :rtype: :class:`.Result`
        """

        return_value = res.Result()

        # build tag move data ( all tags to be moved from current position to 0,0,0 )
        tag_data = []
        # set up a tag filter by name
        FILTER_TAGS = rCusFilter.RevitCustomElementFilter(
            [self.action_family_type_name_contains]
        )
        # get tags in model:
        tag_instances = get_all_independent_tags(self.document)
        for tag_instance in tag_instances:
            if FILTER_TAGS.check_element(self.document, tag_instance.Id):
                tag_data.append(
                    move_tag(
                        tag=tag_instance,
                        new_location=rdb.XYZ(0, 0, 0),
                        old_location=tag_instance.TagHeadPosition,
                    )
                )

        try:
            result_move = update_tag_location(doc=self.document, tag_data=tag_data)
            return_value.append_message(
                "moved tags with result: {} \n and message: {} ".format(
                    result_move.status, result_move.message
                )
            )

            # get tag report
            report_tags = get_tag_instances_report_data(
                doc=self.document,
                revit_file_path=REVIT_INDEPENDENT_TAG_TEST_FILE_NAME,
                custom_element_filter=FILTER_TAGS,
            )

            # loop over dictionaries and check location is 0 ,0,0
            for entry in report_tags:
                return_value.append_message(
                    "Tag with id: {} is at location: {}".format(
                        entry[TAG_ID], entry[TAG_HEAD_LOCATION]
                    )
                )
                assert entry[TAG_HEAD_LOCATION] == [0, 0, 0]

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name, e),
            )

        return return_value
