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
# Copyright 2024, Jan Christel
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
import json

from test.utils import test

from duHast.Revit.Family.Data.family_report_reader import (
    read_family_line_pattern_base_data,
)
from duHast.Utilities.files_io import get_directory_path_from_file_path

TEST_REPORT_DIRECTORY = os.path.join(
    get_directory_path_from_file_path(__file__), "ReadReport_03"
)


class DataReadFamiliesLinePatternsReport(test.Test):

    def __init__(self):
        # store document in base class
        super(DataReadFamiliesLinePatternsReport, self).__init__(
            test_name="read overall family line pattern data report"
        )

    def test(self):
        """
        Reads overall family line patterns data report.

        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "\n-"
        try:

            # 4 test files
            test_files = {
                "FamilyLinePatternsCombinedReport_empty_file.csv": (False, 0, []),
                "FamilyLinePatternsCombinedReport_empty.csv": (False, 0, []),
                "FamilyLinePatternsCombinedReport_multiple.csv": (
                    True,
                    14,
                    [
                        [
                            "LinePattern",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "1",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": -2009518,
                                }
                            ],
                            "Hidden 04_BVN",
                            "1428068",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "2",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": -2000530,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight :: Sample_Family_Thirteen",
                                    "element_id": -2000530,
                                },
                            ],
                            "Reference Plane 02_BVN",
                            "1428069",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "2",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": -2000083,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight :: Sample_Family_Thirteen",
                                    "element_id": -2000083,
                                },
                            ],
                            "Dash 06_BVN",
                            "1436489",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "1",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 10600768,
                                }
                            ],
                            "Dash dot",
                            "1499753",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Eight :: Sample_Family_Thirteen",
                            "Furniture Systems :: Section Marks",
                            "Sample_Family_Thirteen",
                            "-",
                            "0",
                            "None",
                            "Hidden 04_BVN",
                            "1428068",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Eight :: Sample_Family_Thirteen",
                            "Furniture Systems :: Section Marks",
                            "Sample_Family_Thirteen",
                            "-",
                            "1",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight :: Sample_Family_Thirteen",
                                    "element_id": -2000530,
                                }
                            ],
                            "Reference Plane 02_BVN",
                            "1428069",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Eight :: Sample_Family_Thirteen",
                            "Furniture Systems :: Section Marks",
                            "Sample_Family_Thirteen",
                            "-",
                            "1",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight :: Sample_Family_Thirteen",
                                    "element_id": -2000083,
                                }
                            ],
                            "Dash 06_BVN",
                            "1436489",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Ten",
                            "Generic Annotations",
                            "Sample_Family_Ten",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa",
                            "0",
                            "None",
                            "Hidden 04_BVN",
                            "1428068",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Ten",
                            "Generic Annotations",
                            "Sample_Family_Ten",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa",
                            "1",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Ten",
                                    "element_id": -2000530,
                                }
                            ],
                            "Reference Plane 02_BVN",
                            "1428069",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Ten",
                            "Generic Annotations",
                            "Sample_Family_Ten",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa",
                            "1",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Ten",
                                    "element_id": -2000083,
                                }
                            ],
                            "Dash 06_BVN",
                            "1436489",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "3",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": -2009527,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven",
                                    "element_id": -2009512,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": -2009517,
                                },
                            ],
                            "Hidden 04_BVN",
                            "1428068",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "9",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": -2000530,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Thirteen",
                                    "element_id": -2000530,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven",
                                    "element_id": -2000530,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven :: Section Tail - Upgrade",
                                    "element_id": -2000530,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": -2000530,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Symbol_Outlet_GPO_Single_Emergency_ANN",
                                    "element_id": -2000530,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Section Tail - Upgrade",
                                    "element_id": -2000530,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Label_Text_Rotation_1_5mm_ANN",
                                    "element_id": -2000530,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Label_Text_Rotation_1_5mm_ANN :: Label_Text_1_5mm_ANN",
                                    "element_id": -2000530,
                                },
                            ],
                            "Reference Plane 02_BVN",
                            "1428069",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "9",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": -2000083,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Thirteen",
                                    "element_id": -2000083,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven",
                                    "element_id": -2000083,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven :: Section Tail - Upgrade",
                                    "element_id": -2000083,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": -2000083,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Symbol_Outlet_GPO_Single_Emergency_ANN",
                                    "element_id": -2000083,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Section Tail - Upgrade",
                                    "element_id": -2000083,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Label_Text_Rotation_1_5mm_ANN",
                                    "element_id": -2000083,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven :: Label_Text_Rotation_1_5mm_ANN :: Label_Text_1_5mm_ANN",
                                    "element_id": -2000083,
                                },
                            ],
                            "Dash 06_BVN",
                            "1436489",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "3",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": 8485759,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven",
                                    "element_id": 9152387,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 9156917,
                                },
                            ],
                            "Dash dot",
                            "1499753",
                        ],
                    ],
                ),
                "FamilyLinePatternsCombinedReport_single.csv": (
                    True,
                    4,
                    [
                        [
                            "LinePattern",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "1",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": -2009518,
                                }
                            ],
                            "Hidden 04_BVN",
                            "1428068",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "2",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": -2000530,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight :: Sample_Family_Thirteen",
                                    "element_id": -2000530,
                                },
                            ],
                            "Reference Plane 02_BVN",
                            "1428069",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "2",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": -2000083,
                                },
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight :: Sample_Family_Thirteen",
                                    "element_id": -2000083,
                                },
                            ],
                            "Dash 06_BVN",
                            "1436489",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "1",
                            [
                                {
                                    "data_type": "FamilyLinePatternDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 10600768,
                                }
                            ],
                            "Dash dot",
                            "1499753",
                        ],
                        [
                            "LinePattern",
                            "Sample_Family_Eight :: Sample_Family_Thirteen",
                            "Furniture Systems :: Section Marks",
                            "Sample_Family_Thirteen",
                            "-",
                            "0",
                            "None",
                            "Hidden 04_BVN",
                            "1428068",
                        ],
                    ],
                ),
            }

            for test_file, test_result in test_files.items():
                # read overall family data
                family_base_data_result = read_family_line_pattern_base_data(
                    os.path.join(TEST_REPORT_DIRECTORY, test_file)
                )
                message = message + "\n" + family_base_data_result.message

                message = (
                    message
                    + "\n"
                    + "...expecting status {} and got {}".format(
                        test_result[0], family_base_data_result.status
                    )
                )
                assert family_base_data_result.status == test_result[0]
                message = (
                    message
                    + "\n"
                    + "...expecting number of entries {} and got {}".format(
                        test_result[1], len(family_base_data_result.result)
                    )
                )
                assert len(family_base_data_result.result) == test_result[1]

                # check conversion to storage data was successful
                if len(family_base_data_result.result) > 0:
                    for i in range(len(family_base_data_result.result)):
                        message = (
                            message
                            + "\n"
                            + "...checking data conversion\n{}".format(
                                family_base_data_result.result[
                                    i
                                ].get_data_values_as_list_of_strings()
                            )
                        )
                        found_match = False
                        # check if entry at position six is not "None" indicating a a used by entry
                        if (
                            family_base_data_result.result[
                                i
                            ].get_data_values_as_list_of_strings()[6]
                            == "None"
                        ):
                            message = message + "\n" + "......used by entry is None"
                            # no used by entry found, a simple check if data is in list
                            assert (
                                family_base_data_result.result[
                                    i
                                ].get_data_values_as_list_of_strings()
                                in test_result[2]
                            )
                            message = message + "\n" + ".........found match in list"
                            found_match = True
                            continue
                        else:
                            message = (
                                message
                                + "\n"
                                + "......used by entry is list of entries"
                            )
                            # a used by test result was found, check result list before and after used by entry if equal and then compare used by entry
                            retrieved_data = family_base_data_result.result[
                                i
                            ].get_data_values_as_list_of_strings()
                            found_match = False
                            for expected_result_list in test_result[2]:
                                pre_expected_result_list = expected_result_list[:6]
                                post_expected_result_list = expected_result_list[7:]
                                if (
                                    retrieved_data[:6] == pre_expected_result_list
                                    and retrieved_data[7:] == post_expected_result_list
                                ):
                                    message = (
                                        message
                                        + "\n"
                                        + ".........found match in list for pre and post used by entries"
                                    )
                                    try:
                                        # check if used by entry is a list
                                        dummy = json.loads(retrieved_data[6])
                                        # expected = json.loads(expected_result_list[6])
                                        assert dummy == expected_result_list[6]
                                        message = (
                                            message
                                            + "\n"
                                            + ".........used by entries are match"
                                        )
                                        found_match = True
                                        break
                                    except Exception as e:
                                        message = (
                                            message
                                            + "\n"
                                            + "...error comparing used by entries: {}\n{}\n{}".format(
                                                e,
                                                retrieved_data[6],
                                                expected_result_list[6],
                                            )
                                        )
                                else:
                                    # no match move on
                                    pass
                            # set a return flag if no match was found
                            if not found_match:
                                flag = False
                                message = (
                                        message
                                        + "\n"
                                        + "........found no match in list for pre and post used by entries: {} and {}".format( retrieved_data[:6], retrieved_data[7:])
                                    )

        except Exception as e:
            flag = False
            message = (
                message
                + "\n"
                + (
                    "An exception occurred in function {} : {}".format(
                        self.test_name, e
                    )
                )
            )
        return flag, message
