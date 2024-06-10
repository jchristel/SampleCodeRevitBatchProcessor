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
    read_family_shared_parameter_data,
)
from duHast.Utilities.files_io import get_directory_path_from_file_path

TEST_REPORT_DIRECTORY = os.path.join(
    get_directory_path_from_file_path(__file__), "ReadReport_04"
)


class DataReadFamiliesSharedParametersReport(test.Test):

    def __init__(self):
        # store document in base class
        super(DataReadFamiliesSharedParametersReport, self).__init__(
            test_name="read overall family shared parameters data report"
        )

    def test(self):
        """
        Reads overall family shared parameters data report.

        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "\n-"
        try:

            # 4 test files
            test_files = {
                "FamilySharedParametersCombinedReport_empty_file.csv": (False, 0, []),
                "FamilySharedParametersCombinedReport_empty.csv": (False, 0, []),
                "FamilySharedParametersCombinedReport_multiple.csv": (
                    True,
                    34,
                    [
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "94e25b89-289e-43d7-bba9-c1c23be396e9",
                            "Author",
                            "118408",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 118408,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "3091b658-a4ec-4130-98c3-f9e7dfd4c071",
                            "ItemCode",
                            "1640398",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1640398,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "81cfdf2f-1f17-4a3e-a245-37a65b7b16a0",
                            "ItemDescription",
                            "1640399",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1640399,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "be50f510-c92c-4c52-9dcf-b152201710df",
                            "ItemGroup",
                            "1640401",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1640401,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "1d88889c-80d2-4aad-acbe-11076796e986",
                            "Copyright",
                            "1642131",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1642131,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "0e397bbd-a378-4824-b08a-3c03423f5545",
                            "HEIGHT_BVN",
                            "1642132",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1642132,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "980aef7a-c409-4f02-acb2-895aed435f26",
                            "DEPTH_BVN",
                            "1642133",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1642133,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "10fc5a92-3d94-4deb-b74a-23825ebce640",
                            "WIDTH_BVN",
                            "1642135",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1642135,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "6a99c82d-821c-4726-8c75-a4e0097f4441",
                            "DetailedCategory",
                            "1698538",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1698538,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "a65f6d59-9c87-44bc-866b-5644e8412a3f",
                            "ModifiedIssue",
                            "1698539",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1698539,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "bf4c7aa0-8e21-4b5c-922b-204d48970e70",
                            "Responsibility",
                            "1698541",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1698541,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "9fb538e8-0a21-47d8-aa80-79ca7db6dccc",
                            "UniqueID",
                            "1698542",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1698542,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "6cc0c155-4ff7-44e0-9ed0-2b7e49c17aeb",
                            "MOUNTING_HEIGHT_TOP_BVN",
                            "1698543",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1698543,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "f074bc9a-c650-42f4-aeb1-29de0255343f",
                            "MOUNTING_HEIGHT_US_BVN",
                            "1698544",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1698544,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "c26b60fc-38e7-410b-97ce-ab7c4c36ea01",
                            "CEILING_HEIGHT_BVN",
                            "1721566",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1721566,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight :: Sample_Family_Thirteen",
                            "Furniture Systems :: Section Marks",
                            "Sample_Family_Thirteen",
                            "-",
                            "",
                            "No shared parameter present in family.",
                            "-1",
                            "0",
                            "None",
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Ten",
                            "Generic Annotations",
                            "Sample_Family_Ten",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Generic Annotations\Sample_Family_Ten.rfa",
                            "",
                            "No shared parameter present in family.",
                            "-1",
                            "0",
                            "None",
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "94e25b89-289e-43d7-bba9-c1c23be396e9",
                            "Author",
                            "118408",
                            "3",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": 118408,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven",
                                    "element_id": 118408,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 118408,
                                },
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "3091b658-a4ec-4130-98c3-f9e7dfd4c071",
                            "ItemCode",
                            "1640398",
                            "2",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": 1640398,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 1640398,
                                },
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "81cfdf2f-1f17-4a3e-a245-37a65b7b16a0",
                            "ItemDescription",
                            "1640399",
                            "2",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": 1640399,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 1640399,
                                },
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "be50f510-c92c-4c52-9dcf-b152201710df",
                            "ItemGroup",
                            "1640401",
                            "2",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": 1640401,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 1640401,
                                },
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "1d88889c-80d2-4aad-acbe-11076796e986",
                            "Copyright",
                            "1642131",
                            "3",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": 1642131,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven",
                                    "element_id": 1642131,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 1642131,
                                },
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "0e397bbd-a378-4824-b08a-3c03423f5545",
                            "HEIGHT_BVN",
                            "1642132",
                            "2",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": 1642132,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 1642132,
                                },
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "980aef7a-c409-4f02-acb2-895aed435f26",
                            "DEPTH_BVN",
                            "1642133",
                            "2",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": 1642133,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 1642133,
                                },
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "10fc5a92-3d94-4deb-b74a-23825ebce640",
                            "WIDTH_BVN",
                            "1642135",
                            "2",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": 1642135,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 1642135,
                                },
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "6a99c82d-821c-4726-8c75-a4e0097f4441",
                            "DetailedCategory",
                            "1698538",
                            "2",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": 1698538,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 1698538,
                                },
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "a65f6d59-9c87-44bc-866b-5644e8412a3f",
                            "ModifiedIssue",
                            "1698539",
                            "2",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": 1698539,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 1698539,
                                },
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "bf4c7aa0-8e21-4b5c-922b-204d48970e70",
                            "Responsibility",
                            "1698541",
                            "2",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": 1698541,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 1698541,
                                },
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "9fb538e8-0a21-47d8-aa80-79ca7db6dccc",
                            "UniqueID",
                            "1698542",
                            "2",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": 1698542,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 1698542,
                                },
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "c26b60fc-38e7-410b-97ce-ab7c4c36ea01",
                            "CEILING_HEIGHT_BVN",
                            "1721566",
                            "2",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six",
                                    "element_id": 1721566,
                                },
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 1721566,
                                },
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "b74b295e-c1e3-4d7d-b98a-29a1af08d12d",
                            "Modified Issue",
                            "9133881",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Eleven",
                                    "element_id": 9133881,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "3f3f6ed3-c88f-443e-a0b0-b09bbb067881",
                            "MOUNTING_HEIGHT_CENTRE_BVN",
                            "9133882",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 9133882,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "6cc0c155-4ff7-44e0-9ed0-2b7e49c17aeb",
                            "MOUNTING_HEIGHT_TOP_BVN",
                            "9133883",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 9133883,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Six",
                            "Specialty Equipment",
                            "Sample_Family_Six",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\Sample_Family_Six.rfa",
                            "f074bc9a-c650-42f4-aeb1-29de0255343f",
                            "MOUNTING_HEIGHT_US_BVN",
                            "9133884",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Six :: Sample_Family_Seven",
                                    "element_id": 9133884,
                                }
                            ],
                        ],
                    ],
                ),
                "FamilySharedParametersCombinedReport_single.csv": (
                    True,
                    15,
                    [
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "94e25b89-289e-43d7-bba9-c1c23be396e9",
                            "Author",
                            "118408",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 118408,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "3091b658-a4ec-4130-98c3-f9e7dfd4c071",
                            "ItemCode",
                            "1640398",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1640398,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "81cfdf2f-1f17-4a3e-a245-37a65b7b16a0",
                            "ItemDescription",
                            "1640399",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1640399,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "be50f510-c92c-4c52-9dcf-b152201710df",
                            "ItemGroup",
                            "1640401",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1640401,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "1d88889c-80d2-4aad-acbe-11076796e986",
                            "Copyright",
                            "1642131",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1642131,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "0e397bbd-a378-4824-b08a-3c03423f5545",
                            "HEIGHT_BVN",
                            "1642132",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1642132,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "980aef7a-c409-4f02-acb2-895aed435f26",
                            "DEPTH_BVN",
                            "1642133",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1642133,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "10fc5a92-3d94-4deb-b74a-23825ebce640",
                            "WIDTH_BVN",
                            "1642135",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1642135,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "6a99c82d-821c-4726-8c75-a4e0097f4441",
                            "DetailedCategory",
                            "1698538",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1698538,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "a65f6d59-9c87-44bc-866b-5644e8412a3f",
                            "ModifiedIssue",
                            "1698539",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1698539,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "bf4c7aa0-8e21-4b5c-922b-204d48970e70",
                            "Responsibility",
                            "1698541",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1698541,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "9fb538e8-0a21-47d8-aa80-79ca7db6dccc",
                            "UniqueID",
                            "1698542",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1698542,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "6cc0c155-4ff7-44e0-9ed0-2b7e49c17aeb",
                            "MOUNTING_HEIGHT_TOP_BVN",
                            "1698543",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1698543,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "f074bc9a-c650-42f4-aeb1-29de0255343f",
                            "MOUNTING_HEIGHT_US_BVN",
                            "1698544",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1698544,
                                }
                            ],
                        ],
                        [
                            "SharedParameter",
                            "Sample_Family_Eight",
                            "Furniture Systems",
                            "Sample_Family_Eight",
                            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                            "c26b60fc-38e7-410b-97ce-ab7c4c36ea01",
                            "CEILING_HEIGHT_BVN",
                            "1721566",
                            "1",
                            [
                                {
                                    "data_type": "FamilySharedParameterDataStorageUsedBy",
                                    "root_name_path": "Sample_Family_Eight",
                                    "element_id": 1721566,
                                }
                            ],
                        ],
                    ],
                ),
            }

            for test_file, test_result in test_files.items():
                # read overall family data
                family_base_data_result = read_family_shared_parameter_data(
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
                        # check if entry at position nine is not "None" indicating a a used by entry
                        if (
                            family_base_data_result.result[
                                i
                            ].get_data_values_as_list_of_strings()[9]
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
                                pre_expected_result_list = expected_result_list[:8]
                                # there is no post since used by is the last entry
                                # post_expected_result_list = expected_result_list[7:]
                                if (
                                    retrieved_data[:8]
                                    == pre_expected_result_list
                                    # and retrieved_data[7:] == post_expected_result_list
                                ):
                                    message = (
                                        message
                                        + "\n"
                                        + ".........found match in list for pre and post used by entries"
                                    )
                                    try:
                                        # check if used by entry is a list
                                        dummy = json.loads(retrieved_data[9])
                                        # expected = json.loads(expected_result_list[9])
                                        assert dummy == expected_result_list[9]
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
                                                retrieved_data[9],
                                                expected_result_list[9],
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
                                    + "........found no match in list for pre used by entries: {} ".format(
                                        retrieved_data[:8]
                                    )
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
