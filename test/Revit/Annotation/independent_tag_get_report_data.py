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

import revit_script_util

# import Autodesk.Revit.DB as rdb
from test.Revit.TestUtils import revit_test
from duHast.Revit.Annotation.Reporting.tags_independent_report import (
    get_tag_instances_report_data,
)

# filter imports
from duHast.Revit.Common import custom_element_filter_actions as elCustomFilterAction
from duHast.Revit.Common import custom_element_filter_tests as elCustomFilterTest
from duHast.Revit.Common import custom_element_filter as rCusFilter

from duHast.Revit.Common.revit_version import get_revit_version_number
from duHast.Utilities.Objects import result as res
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

    # result for Revit 2022
    EXPECTED_RESULT_2022 = [
        {
            "TAG_HAS_LEADER": True,
            "TAG_IS_ORPHANED": False,
            "IS_MULTICATEGORY_TAG": True,
            "TAG_ID": 971837,
            "MULTI_REFERENCE_ANNOTATION_ID": -1,
            "TAG_TEXT": "",
            "TAG_ROTATION_ANGLE": 0.0,
            "TAG_IS_MATERIAL_TAG": False,
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971454,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                }
            ],
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
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                }
            ],
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
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                }
            ],
            "HOST_FILE": "independent tags.rvt",
            "LEADER_PROPERTIES": None,
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
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                }
            ],
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
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                }
            ],
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
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
                {
                    "host_element_id": 971958,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
            ],
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
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971454,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
                {
                    "host_element_id": 971958,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
            ],
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
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
                {
                    "host_element_id": 971958,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
            ],
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
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
                {
                    "host_element_id": 971958,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
            ],
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
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
                {
                    "host_element_id": 971958,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
            ],
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
            "TAG_HEAD_LOCATION": [
                22.540629252017272,
                21.318994861757133,
                0.41010498687664038,
            ],
            "TAG_ORIENTATION": "Horizontal",
            "LEADER_END_CONDITION": "Free",
        },
    ]

    # result for Revit 2023
    EXPECTED_RESULT_2023 = [
        {
            "TAG_ID": 971837,
            "MULTI_REFERENCE_ANNOTATION_ID": -1,
            "TAG_HAS_LEADER": True,
            "TAG_PRESENTATION_MODE": "ShowAll",
            "TAG_HEAD_LOCATION": [
                6.4491434294134775,
                18.771160998835541,
                0.41010498687664038,
            ],
            "IS_MULTICATEGORY_TAG": True,
            "MERGE_ELBOWS": False,
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971454,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                }
            ],
            "TAG_ORIENTATION": "Horizontal",
            "LEADER_END_CONDITION": "Attached",
            "HOST_FILE": "independent tags.rvt",
            "TAG_TEXT": "",
            "TAG_IS_MATERIAL_TAG": False,
            "TAG_ROTATION_ANGLE": 0.0,
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
            "TAG_IS_ORPHANED": False,
        },
        {
            "TAG_ID": 971911,
            "MULTI_REFERENCE_ANNOTATION_ID": -1,
            "TAG_HAS_LEADER": True,
            "TAG_PRESENTATION_MODE": "ShowAll",
            "TAG_HEAD_LOCATION": [
                22.0765567353468,
                16.262428207494324,
                0.41010498687664038,
            ],
            "IS_MULTICATEGORY_TAG": True,
            "MERGE_ELBOWS": False,
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                }
            ],
            "TAG_ORIENTATION": "Horizontal",
            "LEADER_END_CONDITION": "Attached",
            "HOST_FILE": "independent tags.rvt",
            "TAG_TEXT": "TypeMark_value",
            "TAG_IS_MATERIAL_TAG": False,
            "TAG_ROTATION_ANGLE": 0.0,
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
            "TAG_IS_ORPHANED": False,
        },
        {
            "TAG_ID": 971917,
            "MULTI_REFERENCE_ANNOTATION_ID": -1,
            "TAG_HAS_LEADER": False,
            "TAG_PRESENTATION_MODE": "HideAll",
            "TAG_HEAD_LOCATION": [
                22.076556735346795,
                13.443927435018283,
                0.41010498687664038,
            ],
            "IS_MULTICATEGORY_TAG": True,
            "MERGE_ELBOWS": False,
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                }
            ],
            "TAG_ORIENTATION": "Horizontal",
            "LEADER_END_CONDITION": "None",
            "HOST_FILE": "independent tags.rvt",
            "TAG_TEXT": "TypeMark_value",
            "TAG_IS_MATERIAL_TAG": False,
            "TAG_ROTATION_ANGLE": 0.0,
            "LEADER_PROPERTIES": None,
            "TAG_IS_ORPHANED": False,
        },
        {
            "TAG_ID": 971921,
            "MULTI_REFERENCE_ANNOTATION_ID": -1,
            "TAG_HAS_LEADER": True,
            "TAG_PRESENTATION_MODE": "ShowAll",
            "TAG_HEAD_LOCATION": [
                22.076556735346792,
                9.956501312416821,
                0.41010498687664038,
            ],
            "IS_MULTICATEGORY_TAG": True,
            "MERGE_ELBOWS": False,
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                }
            ],
            "TAG_ORIENTATION": "Horizontal",
            "LEADER_END_CONDITION": "Attached",
            "HOST_FILE": "independent tags.rvt",
            "TAG_TEXT": "TypeMark_value",
            "TAG_IS_MATERIAL_TAG": False,
            "TAG_ROTATION_ANGLE": 0.0,
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
            "TAG_IS_ORPHANED": False,
        },
        {
            "TAG_ID": 971925,
            "MULTI_REFERENCE_ANNOTATION_ID": -1,
            "TAG_HAS_LEADER": True,
            "TAG_PRESENTATION_MODE": "ShowAll",
            "TAG_HEAD_LOCATION": [
                22.0765567353468,
                18.365894083177334,
                0.41010498687664038,
            ],
            "IS_MULTICATEGORY_TAG": True,
            "MERGE_ELBOWS": False,
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                }
            ],
            "TAG_ORIENTATION": "Horizontal",
            "LEADER_END_CONDITION": "Free",
            "HOST_FILE": "independent tags.rvt",
            "TAG_TEXT": "TypeMark_value",
            "TAG_IS_MATERIAL_TAG": False,
            "TAG_ROTATION_ANGLE": 0.0,
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
            "TAG_IS_ORPHANED": False,
        },
        {
            "TAG_ID": 971990,
            "MULTI_REFERENCE_ANNOTATION_ID": -1,
            "TAG_HAS_LEADER": True,
            "TAG_PRESENTATION_MODE": "ShowAll",
            "TAG_HEAD_LOCATION": [
                11.702540987315306,
                28.500522382310383,
                0.41010498687664038,
            ],
            "IS_MULTICATEGORY_TAG": True,
            "MERGE_ELBOWS": False,
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
                {
                    "host_element_id": 971958,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
            ],
            "TAG_ORIENTATION": "Horizontal",
            "LEADER_END_CONDITION": "Attached",
            "HOST_FILE": "independent tags.rvt",
            "TAG_TEXT": "TypeMark_value",
            "TAG_IS_MATERIAL_TAG": False,
            "TAG_ROTATION_ANGLE": 0.0,
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
            "TAG_IS_ORPHANED": False,
        },
        {
            "TAG_ID": 972003,
            "MULTI_REFERENCE_ANNOTATION_ID": -1,
            "TAG_HAS_LEADER": True,
            "TAG_PRESENTATION_MODE": "ShowAll",
            "TAG_HEAD_LOCATION": [
                10.025230182004806,
                3.3883042773634013,
                0.41010498687664038,
            ],
            "IS_MULTICATEGORY_TAG": True,
            "MERGE_ELBOWS": False,
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971454,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
                {
                    "host_element_id": 971958,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
            ],
            "TAG_ORIENTATION": "Horizontal",
            "LEADER_END_CONDITION": "Attached",
            "HOST_FILE": "independent tags.rvt",
            "TAG_TEXT": "<varies>",
            "TAG_IS_MATERIAL_TAG": False,
            "TAG_ROTATION_ANGLE": 0.0,
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
            "TAG_IS_ORPHANED": False,
        },
        {
            "TAG_ID": 972007,
            "MULTI_REFERENCE_ANNOTATION_ID": -1,
            "TAG_HAS_LEADER": True,
            "TAG_PRESENTATION_MODE": "ShowAll",
            "TAG_HEAD_LOCATION": [
                20.890537201597738,
                25.831832930732823,
                0.41010498687664038,
            ],
            "IS_MULTICATEGORY_TAG": True,
            "MERGE_ELBOWS": False,
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
                {
                    "host_element_id": 971958,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
            ],
            "TAG_ORIENTATION": "Horizontal",
            "LEADER_END_CONDITION": "Attached",
            "HOST_FILE": "independent tags.rvt",
            "TAG_TEXT": "TypeMark_value",
            "TAG_IS_MATERIAL_TAG": False,
            "TAG_ROTATION_ANGLE": 0.0,
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
            "TAG_IS_ORPHANED": False,
        },
        {
            "TAG_ID": 972016,
            "MULTI_REFERENCE_ANNOTATION_ID": -1,
            "TAG_HAS_LEADER": True,
            "TAG_PRESENTATION_MODE": "ShowAll",
            "TAG_HEAD_LOCATION": [
                22.540629252017276,
                23.477783473151881,
                0.41010498687664038,
            ],
            "IS_MULTICATEGORY_TAG": True,
            "MERGE_ELBOWS": False,
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
                {
                    "host_element_id": 971958,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
            ],
            "TAG_ORIENTATION": "Horizontal",
            "LEADER_END_CONDITION": "Attached",
            "HOST_FILE": "independent tags.rvt",
            "TAG_TEXT": "TypeMark_value",
            "TAG_IS_MATERIAL_TAG": False,
            "TAG_ROTATION_ANGLE": 0.0,
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
            "TAG_IS_ORPHANED": False,
        },
        {
            "TAG_ID": 972020,
            "MULTI_REFERENCE_ANNOTATION_ID": -1,
            "TAG_HAS_LEADER": True,
            "TAG_PRESENTATION_MODE": "ShowAll",
            "TAG_HEAD_LOCATION": [
                22.540629252017272,
                21.318994861757133,
                0.41010498687664038,
            ],
            "IS_MULTICATEGORY_TAG": True,
            "MERGE_ELBOWS": False,
            "TAGGED_ELEMENT_IDS": [
                {
                    "host_element_id": 971860,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
                {
                    "host_element_id": 971958,
                    "link_instance_id": -1,
                    "link_element_id": -1,
                },
            ],
            "TAG_ORIENTATION": "Horizontal",
            "LEADER_END_CONDITION": "Free",
            "HOST_FILE": "independent tags.rvt",
            "TAG_TEXT": "TypeMark_value",
            "TAG_IS_MATERIAL_TAG": False,
            "TAG_ROTATION_ANGLE": 0.0,
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
            "TAG_IS_ORPHANED": False,
        },
    ]

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
                - .status True if tag instance data was retrieved successfully, otherwise False
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
                # not supported in tests
                expected_result = []
            elif revit_version == 2022:
                expected_result = self.EXPECTED_RESULT_2022
            elif revit_version == 2023:
                expected_result = self.EXPECTED_RESULT_2023
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
