"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit independent tag update location from report tests . 
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

import os
from test.Revit.TestUtils import revit_test

from duHast.Revit.Annotation.Reporting.gen_annotations_instance_report_header import (
    TAG_ID,
    TAG_HEAD_LOCATION,
)

from duHast.Revit.Annotation.independent_tags_modify_properties import (
    update_tag_locations_from_report,
)
from duHast.Revit.Annotation.Reporting.tags_independent_report import (
    get_tag_instances_report_data,
)
from test.Revit.Annotation.annotations_report import (
    REVIT_INDEPENDENT_TAG_TEST_FILE_NAME,
    MULTI_CATEGORY_TAG_TYPE_NAME,
)

# filter imports
from duHast.Revit.Common import custom_element_filter_actions as elCustomFilterAction
from duHast.Revit.Common import custom_element_filter_tests as elCustomFilterTest
from duHast.Revit.Common import custom_element_filter as rCusFilter

# utilities
from duHast.Utilities.Objects import result as res
from duHast.Utilities.console_out import output
from duHast.Utilities.files_json import write_json_to_file


class IndependentTagUpdateLocationFromReport(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(IndependentTagUpdateLocationFromReport, self).__init__(
            doc=doc,
            test_name="update_tag_locations_from_report",
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

        try:
            # set up a tag filter by name
            FILTER_TAGS = rCusFilter.RevitCustomElementFilter(
                [self.action_family_type_name_contains]
            )

            # get tag report
            report_tags = get_tag_instances_report_data(
                doc=self.document,
                revit_file_path=REVIT_INDEPENDENT_TAG_TEST_FILE_NAME,
                custom_element_filter=FILTER_TAGS,
            )

            # set all report locations to 0,0,0 before writing to file
            for report_tag in report_tags:
                report_tag[TAG_HEAD_LOCATION] = [0, 0, 0]

            # write data to file
            data_file_name = os.path.join(
                self.tmp_dir, REVIT_INDEPENDENT_TAG_TEST_FILE_NAME
            )

            # write data to file
            write_json_file_result = write_json_to_file(
                json_data=report_tags, data_output_file_path=data_file_name
            )
            return_value.append_message(
                " writing json file: {}".format(write_json_file_result.status)
            )
            assert write_json_file_result.status == True

            # action to be executed in a transaction group so it can be rolled back at end of test
            def action(doc):
                action_return_value = res.Result()
                try:
                    # move tags
                    result_update = update_tag_locations_from_report(
                        doc=self.document,
                        report_file_path=data_file_name,
                        distance_threshold=0,
                    )
                    action_return_value.append_message(
                        "moved tags with result: {} \n and message: {} ".format(
                            result_update.status, result_update.message
                        )
                    )
                    assert result_update.status == True

                    # read tag data and check they all have moved to 0,0,0
                    # get tag report
                    report_tags = get_tag_instances_report_data(
                        doc=self.document,
                        revit_file_path=REVIT_INDEPENDENT_TAG_TEST_FILE_NAME,
                        custom_element_filter=FILTER_TAGS,
                    )

                    # loop over dictionaries and check tag location is 0 ,0,0
                    for entry in report_tags:
                        action_return_value.append_message(
                            "Tag with id: {} is at location: {}".format(
                                entry[TAG_ID], entry[TAG_HEAD_LOCATION]
                            )
                        )
                        assert entry[TAG_HEAD_LOCATION] == [0, 0, 0]

                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "An exception occurred in function {}: {}".format(
                            self.test_name, e
                        ),
                    )
                return action_return_value

            return_value = self.in_transaction_group(action)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in outer block in function {}: {}".format(
                    self.test_name, e
                ),
            )
        finally:
            # clean up temp directory
            clean_up = self.clean_up()
            return_value.update_sep(
                clean_up,
                "Attempted to clean up temp directory with result: {}".format(clean_up),
            )
        return return_value
