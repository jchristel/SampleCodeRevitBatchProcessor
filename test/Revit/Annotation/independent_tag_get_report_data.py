"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit independent report data tests . 
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
from duHast.Revit.Annotation.Reporting.tags_independent_report import (
    get_tag_instances_report_data,
)

# filter imports
from duHast.Revit.Common import custom_element_filter_actions as elCustomFilterAction
from duHast.Revit.Common import custom_element_filter_tests as elCustomFilterTest
from duHast.Revit.Common import custom_element_filter as rCusFilter

from duHast.Revit.Common.revit_version import get_revit_version_number
from duHast.Utilities import result as res
from duHast.Utilities.console_out import output
from test.Revit.Annotation.annotations_report import (
    REVIT_INDEPENDENT_TAG_TEST_FILE_NAME,
    MULTI_CATEGORY_TAG_TYPE_NAME,
)


class GetIndependentTagReportData(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetIndependentTagReportData, self).__init__(
            doc=doc, test_name="get_tag_instances_report_data"
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
        get_tag_instances_report_data test

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
            # tags changed behaviour in revit 2022...
            revit_version = get_revit_version_number(self.document)
            if revit_version <= 2021:
                expected_result = []
            else:
                expected_result = [
                    {
                        "TAG_HAS_LEADER": True,
                        "TAG_IS_ORPHANED": False,
                        "IS_MULTICATEGORY_TAG": True,
                        "TAG_ID": 971837,
                        "MULTI_REFERENCE_ANNOTATION_ID": -1,
                        "TAG_TEXT": "",
                        "TAG_ROTATION_ANGLE": 0.0,
                        "TAG_IS_MATERIAL_TAG": False,
                        "HOST_FILE": "independent tags.rvt",
                        "LEADER_PROPERTIES": [
                            {
                                "elbow_location": None,
                                "leader_end": None,
                                "leader_reference": {
                                    "leader_element_reference_id": 971454,
                                    "leader_linked_element_reference_id": -1,
                                },
                            }
                        ],
                        "TAGGED_ELEMENT_NAME": "NoTypeMark",
                        "TAG_HEAD_LOCATION": [
                            6.4491434294134775,
                            18.771160998835541,
                            0.41010498687664038,
                        ],
                        "TAG_ORIENTATION": "Horizontal",
                        "LEADER_END_CONDITION": "Attached",
                    },
                    {
                        "TAG_HAS_LEADER": True,
                        "TAG_IS_ORPHANED": False,
                        "IS_MULTICATEGORY_TAG": True,
                        "TAG_ID": 971911,
                        "MULTI_REFERENCE_ANNOTATION_ID": -1,
                        "TAG_TEXT": "TypeMark_value",
                        "TAG_ROTATION_ANGLE": 0.0,
                        "TAG_IS_MATERIAL_TAG": False,
                        "HOST_FILE": "independent tags.rvt",
                        "LEADER_PROPERTIES": [
                            {
                                "elbow_location": [
                                    14.720541614220954,
                                    16.262428207494288,
                                    0.41010498687664038,
                                ],
                                "leader_end": None,
                                "leader_reference": {
                                    "leader_element_reference_id": 971860,
                                    "leader_linked_element_reference_id": -1,
                                },
                            }
                        ],
                        "TAGGED_ELEMENT_NAME": "WithTypeMark",
                        "TAG_HEAD_LOCATION": [
                            22.0765567353468,
                            16.262428207494324,
                            0.41010498687664038,
                        ],
                        "TAG_ORIENTATION": "Horizontal",
                        "LEADER_END_CONDITION": "Attached",
                    },
                    {
                        "TAG_HAS_LEADER": False,
                        "TAG_IS_ORPHANED": False,
                        "IS_MULTICATEGORY_TAG": True,
                        "TAG_ID": 971917,
                        "MULTI_REFERENCE_ANNOTATION_ID": -1,
                        "TAG_TEXT": "TypeMark_value",
                        "TAG_ROTATION_ANGLE": 0.0,
                        "TAG_IS_MATERIAL_TAG": False,
                        "HOST_FILE": "independent tags.rvt",
                        "LEADER_PROPERTIES": None,
                        "TAGGED_ELEMENT_NAME": "WithTypeMark",
                        "TAG_HEAD_LOCATION": [
                            22.076556735346795,
                            13.443927435018283,
                            0.41010498687664038,
                        ],
                        "TAG_ORIENTATION": "Horizontal",
                        "LEADER_END_CONDITION": "None",
                    },
                    {
                        "TAG_HAS_LEADER": True,
                        "TAG_IS_ORPHANED": False,
                        "IS_MULTICATEGORY_TAG": True,
                        "TAG_ID": 971921,
                        "MULTI_REFERENCE_ANNOTATION_ID": -1,
                        "TAG_TEXT": "TypeMark_value",
                        "TAG_ROTATION_ANGLE": 0.0,
                        "TAG_IS_MATERIAL_TAG": False,
                        "HOST_FILE": "independent tags.rvt",
                        "LEADER_PROPERTIES": [
                            {
                                "elbow_location": None,
                                "leader_end": None,
                                "leader_reference": {
                                    "leader_element_reference_id": 971860,
                                    "leader_linked_element_reference_id": -1,
                                },
                            }
                        ],
                        "TAGGED_ELEMENT_NAME": "WithTypeMark",
                        "TAG_HEAD_LOCATION": [
                            22.076556735346792,
                            9.956501312416821,
                            0.41010498687664038,
                        ],
                        "TAG_ORIENTATION": "Horizontal",
                        "LEADER_END_CONDITION": "Attached",
                    },
                    {
                        "TAG_HAS_LEADER": True,
                        "TAG_IS_ORPHANED": False,
                        "IS_MULTICATEGORY_TAG": True,
                        "TAG_ID": 971925,
                        "MULTI_REFERENCE_ANNOTATION_ID": -1,
                        "TAG_TEXT": "TypeMark_value",
                        "TAG_ROTATION_ANGLE": 0.0,
                        "TAG_IS_MATERIAL_TAG": False,
                        "HOST_FILE": "independent tags.rvt",
                        "LEADER_PROPERTIES": [
                            {
                                "elbow_location": [
                                    14.419514202503763,
                                    18.365894083177295,
                                    0.41010498687664038,
                                ],
                                "leader_end": [
                                    12.354655240437099,
                                    14.604494332168855,
                                    0.41010498687664038,
                                ],
                                "leader_reference": {
                                    "leader_element_reference_id": 971860,
                                    "leader_linked_element_reference_id": -1,
                                },
                            }
                        ],
                        "TAGGED_ELEMENT_NAME": "WithTypeMark",
                        "TAG_HEAD_LOCATION": [
                            22.0765567353468,
                            18.365894083177334,
                            0.41010498687664038,
                        ],
                        "TAG_ORIENTATION": "Horizontal",
                        "LEADER_END_CONDITION": "Free",
                    },
                    {
                        "TAG_HAS_LEADER": True,
                        "TAG_IS_ORPHANED": False,
                        "IS_MULTICATEGORY_TAG": True,
                        "TAG_ID": 971990,
                        "MULTI_REFERENCE_ANNOTATION_ID": -1,
                        "TAG_TEXT": "TypeMark_value",
                        "TAG_ROTATION_ANGLE": 0.0,
                        "TAG_IS_MATERIAL_TAG": False,
                        "HOST_FILE": "independent tags.rvt",
                        "LEADER_PROPERTIES": [
                            {
                                "elbow_location": None,
                                "leader_end": None,
                                "leader_reference": {
                                    "leader_element_reference_id": 971860,
                                    "leader_linked_element_reference_id": -1,
                                },
                            },
                            {
                                "elbow_location": None,
                                "leader_end": None,
                                "leader_reference": {
                                    "leader_element_reference_id": 971958,
                                    "leader_linked_element_reference_id": -1,
                                },
                            },
                        ],
                        "TAGGED_ELEMENT_NAME": "WithTypeMark",
                        "TAG_HEAD_LOCATION": [
                            11.702540987315306,
                            28.500522382310383,
                            0.41010498687664038,
                        ],
                        "TAG_ORIENTATION": "Horizontal",
                        "LEADER_END_CONDITION": "Attached",
                    },
                    {
                        "TAG_HAS_LEADER": True,
                        "TAG_IS_ORPHANED": False,
                        "IS_MULTICATEGORY_TAG": True,
                        "TAG_ID": 972003,
                        "MULTI_REFERENCE_ANNOTATION_ID": -1,
                        "TAG_TEXT": "<varies>",
                        "TAG_ROTATION_ANGLE": 0.0,
                        "TAG_IS_MATERIAL_TAG": False,
                        "HOST_FILE": "independent tags.rvt",
                        "LEADER_PROPERTIES": [
                            {
                                "elbow_location": None,
                                "leader_end": None,
                                "leader_reference": {
                                    "leader_element_reference_id": 971958,
                                    "leader_linked_element_reference_id": -1,
                                },
                            },
                            {
                                "elbow_location": None,
                                "leader_end": None,
                                "leader_reference": {
                                    "leader_element_reference_id": 971860,
                                    "leader_linked_element_reference_id": -1,
                                },
                            },
                            {
                                "elbow_location": None,
                                "leader_end": None,
                                "leader_reference": {
                                    "leader_element_reference_id": 971454,
                                    "leader_linked_element_reference_id": -1,
                                },
                            },
                        ],
                        "TAGGED_ELEMENT_NAME": "WithTypeMark",
                        "TAG_HEAD_LOCATION": [
                            10.025230182004806,
                            3.3883042773634013,
                            0.41010498687664038,
                        ],
                        "TAG_ORIENTATION": "Horizontal",
                        "LEADER_END_CONDITION": "Attached",
                    },
                    {
                        "TAG_HAS_LEADER": True,
                        "TAG_IS_ORPHANED": False,
                        "IS_MULTICATEGORY_TAG": True,
                        "TAG_ID": 972007,
                        "MULTI_REFERENCE_ANNOTATION_ID": -1,
                        "TAG_TEXT": "TypeMark_value",
                        "TAG_ROTATION_ANGLE": 0.0,
                        "TAG_IS_MATERIAL_TAG": False,
                        "HOST_FILE": "independent tags.rvt",
                        "LEADER_PROPERTIES": [
                            {
                                "elbow_location": None,
                                "leader_end": None,
                                "leader_reference": {
                                    "leader_element_reference_id": 971860,
                                    "leader_linked_element_reference_id": -1,
                                },
                            },
                            {
                                "elbow_location": [
                                    12.651153894590518,
                                    23.425835621100937,
                                    0.41010498687664038,
                                ],
                                "leader_end": None,
                                "leader_reference": {
                                    "leader_element_reference_id": 971958,
                                    "leader_linked_element_reference_id": -1,
                                },
                            },
                        ],
                        "TAGGED_ELEMENT_NAME": "WithTypeMark",
                        "TAG_HEAD_LOCATION": [
                            20.890537201597738,
                            25.831832930732823,
                            0.41010498687664038,
                        ],
                        "TAG_ORIENTATION": "Horizontal",
                        "LEADER_END_CONDITION": "Attached",
                    },
                    {
                        "TAG_HAS_LEADER": True,
                        "TAG_IS_ORPHANED": False,
                        "IS_MULTICATEGORY_TAG": True,
                        "TAG_ID": 972016,
                        "MULTI_REFERENCE_ANNOTATION_ID": -1,
                        "TAG_TEXT": "TypeMark_value",
                        "TAG_ROTATION_ANGLE": 0.0,
                        "TAG_IS_MATERIAL_TAG": False,
                        "HOST_FILE": "independent tags.rvt",
                        "LEADER_PROPERTIES": [
                            {
                                "elbow_location": [
                                    14.320345002871903,
                                    21.089717297889269,
                                    0.41010498687664038,
                                ],
                                "leader_end": None,
                                "leader_reference": {
                                    "leader_element_reference_id": 971860,
                                    "leader_linked_element_reference_id": -1,
                                },
                            },
                            {
                                "elbow_location": [
                                    12.949339195063379,
                                    21.370709684415623,
                                    0.41010498687664038,
                                ],
                                "leader_end": None,
                                "leader_reference": {
                                    "leader_element_reference_id": 971958,
                                    "leader_linked_element_reference_id": -1,
                                },
                            },
                        ],
                        "TAGGED_ELEMENT_NAME": "WithTypeMark",
                        "TAG_HEAD_LOCATION": [
                            22.540629252017276,
                            23.477783473151881,
                            0.41010498687664038,
                        ],
                        "TAG_ORIENTATION": "Horizontal",
                        "LEADER_END_CONDITION": "Attached",
                    },
                    {
                        "TAG_HAS_LEADER": True,
                        "TAG_IS_ORPHANED": False,
                        "IS_MULTICATEGORY_TAG": True,
                        "TAG_ID": 972020,
                        "MULTI_REFERENCE_ANNOTATION_ID": -1,
                        "TAG_TEXT": "TypeMark_value",
                        "TAG_ROTATION_ANGLE": 0.0,
                        "TAG_IS_MATERIAL_TAG": False,
                        "HOST_FILE": "independent tags.rvt",
                        "LEADER_PROPERTIES": [
                            {
                                "elbow_location": [
                                    9.916006883522366,
                                    18.447302842139074,
                                    0.41010498687664038,
                                ],
                                "leader_end": [
                                    12.354655240437099,
                                    14.604494332168855,
                                    0.41010498687664038,
                                ],
                                "leader_reference": {
                                    "leader_element_reference_id": 971860,
                                    "leader_linked_element_reference_id": -1,
                                },
                            },
                            {
                                "elbow_location": [
                                    8.580125124029635,
                                    18.693171180349633,
                                    0.41010498687664038,
                                ],
                                "leader_end": [
                                    9.401899334925288,
                                    14.604494332168862,
                                    0.41010498687664038,
                                ],
                                "leader_reference": {
                                    "leader_element_reference_id": 971958,
                                    "leader_linked_element_reference_id": -1,
                                },
                            },
                        ],
                        "TAGGED_ELEMENT_NAME": "WithTypeMark",
                        "TAG_HEAD_LOCATION": [
                            22.540629252017272,
                            21.318994861757133,
                            0.41010498687664038,
                        ],
                        "TAG_ORIENTATION": "Horizontal",
                        "LEADER_END_CONDITION": "Free",
                    },
                ]

            # get instance report data
            result = get_tag_instances_report_data(
                doc=self.document,
                revit_file_path=REVIT_INDEPENDENT_TAG_TEST_FILE_NAME,
                custom_element_filter=FILTER_TAGS,
            )

            return_value.append_message(
                " result: {} \n expected: {} ".format(result, expected_result)
            )
            assert sorted(result) == sorted(expected_result)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name, e),
            )

        return return_value
