"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains data combine reports tests . 
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

from duHast.Revit.Family.Data.family_base_data_utils import (
    nested_family,
    read_overall_family_data_list_from_directory,
)
from duHast.Revit.Family.Data.family_report_utils import combine_reports
from duHast.Utilities.files_io import get_directory_path_from_file_path

TEST_REPORT_DIRECTORY_ONE = os.path.join(
    get_directory_path_from_file_path(__file__), "CombineReports_01"
)
TEST_REPORT_DIRECTORY_TWO = os.path.join(
    get_directory_path_from_file_path(__file__), "CombineReports_02"
)
TEST_REPORT_DIRECTORY_THREE = os.path.join(
    get_directory_path_from_file_path(__file__), "CombineReports_03"
)
TEST_REPORT_DIRECTORY_FOUR = os.path.join(
    get_directory_path_from_file_path(__file__), "CombineReports_04"
)


REPORTS_TO_COMBINE = {
    TEST_REPORT_DIRECTORY_ONE: [
        (
            [
                "FamilyWarningsCombinedReport_previous.csv",
                "FamilyWarningsCombinedReport_new.csv",
            ],
            [
                [
                    "root",
                    "rootCategory",
                    "familyName",
                    "familyFilePath",
                    "warningText",
                    "warningGUID",
                    "warningRelatedIds",
                    "warningOtherIds",
                ]
            ],
        ),
        (
            [
                "FamilySharedParametersCombinedReport_previous.csv",
                "FamilySharedParametersCombinedReport_new.csv",
            ],
            [
                [
                    "root",
                    "rootCategory",
                    "familyName",
                    "familyFilePath",
                    "parameterName",
                    "parameterGUID",
                    "parameterId",
                    "usageCounter",
                    "usedBy",
                ]
            ],
        ),
        (
            [
                "FamilyLinePatternsCombinedReport_previous.csv",
                "FamilyLinePatternsCombinedReport_new.csv",
            ],
            [
                [
                    "root",
                    "rootCategory",
                    "familyName",
                    "familyFilePath",
                    "usageCounter",
                    "usedBy",
                    "patternName",
                    "patternId",
                ]
            ],
        ),
        (
            [
                "FamilyCategoriesCombinedReport_previous.csv",
                "FamilyCategoriesCombinedReport_new.csv",
            ],
            [
                [
                    "root",
                    "rootCategory",
                    "familyName",
                    "familyFilePath",
                    "usageCounter",
                    "usedBy",
                    "categoryName",
                    "subCategoryName",
                    "subCategoryId",
                    "graphicProperty_3D",
                    "graphicProperty_Cut",
                    "graphicProperty_Projection",
                    "graphicProperty_MaterialName",
                    "graphicProperty_MaterialId",
                    "graphicProperty_LineWeightCut",
                    "graphicProperty_LineWeightProjection",
                    "graphicProperty_Red",
                    "graphicProperty_Green",
                    "graphicProperty_Blue",
                ]
            ],
        ),
        (
            [
                "FamilyBaseDataCombinedReport_previous.csv",
                "FamilyBaseDataCombinedReport_new.csv",
            ],
            [
                [
                    "root",
                    "rootCategory",
                    "familyName",
                    "familyFilePath",
                    "categoryName",
                ]
            ],
        ),
    ],
}


class DataCombineFamiliesReports(test.Test):

    def __init__(self):
        # store document in base class
        super(DataCombineFamiliesReports, self).__init__(
            test_name="combine family data report"
        )

    def test(self):
        """
        Combines family data report.

        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "\n-"
        try:
            # test previous report empty and new report empty (01)

            # test previous report empty but new report not empty (02)

            # test previous report not empty but new report empty (03)

            # test previous report not empty and new report not empty (04)

            for directory, reports in REPORTS_TO_COMBINE.items():
                for report in reports:
                    previous_report = os.path.join(directory, report[0][0])
                    new_report = os.path.join(directory, report[0][1])
                    # attempt to combine reports
                    result_combined = combine_reports(previous_report, new_report)

                    # check if successful
                    if not result_combined.status:
                        flag = False
                        message += "\nfailed to combine reports: {} and {} with message: \n{}\n{}".format(
                            previous_report,
                            new_report,
                            result_combined.message,
                            result_combined.status,
                        )
                        break

                    # message logs if something goes wrong
                    message += "\nresult from data: {} \nvs \nexpected: {}".format(
                        "\n".join(
                            " ".join(sublist)
                            for sublist in sorted(result_combined.result)
                        ),
                        "\n".join(" ".join(sublist) for sublist in sorted(report[1])),
                    )

                    # check if equal
                    assert sorted(result_combined.result) == sorted(report[1])

                    # debug print
                    print(result_combined)

            pass

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
