"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit schedule report data tests . 
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

from test.Revit.TestUtils import revit_test
from duHast.Revit.Views.Reporting.schedules_report import write_schedule_data
from duHast.Utilities.Objects import result as res

from test.Revit.Views.schedules_report import REVIT_TEST_FILE_NAME, OUTPUT_FILE_NAME


class WriteScheduleReportData(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(WriteScheduleReportData, self).__init__(
            doc=doc, test_name="Write all schedules data", requires_temp_dir=True
        )

    def test(self):
        """
        Write all schedules data test.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if schedule report data was written to file successfully, otherwise False
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
            # get sheet report headers
            result = write_schedule_data(
                self.document,
                self.get_full_file_path(OUTPUT_FILE_NAME),
                REVIT_TEST_FILE_NAME,
            )
            return_value.append_message(
                " file written: {} to: {}".format(result.status, result.message)
            )
            # check file was written
            assert result.status == True
            # double check...
            expected_result_file_read = []
            if self.revit_version_number == 2022:
                expected_result_file_read = [
                    [
                        "HOSTFILE",
                        "Id",
                        "View Template",
                        "View Name",
                        "Dependency",
                        "Visibility/Graphics Overrides",
                        "Phase Filter",
                        "Phase",
                        "Fields",
                        "Filter",
                        "Sorting/Grouping",
                        "Formatting",
                        "Appearance",
                        "Design Stage",
                        "None",
                    ],
                    [
                        REVIT_TEST_FILE_NAME,
                        "970420",
                        "-1",
                        "Wall Schedule",
                        "Independent",
                        "Invalid storage type: (NONE)",
                        "2029",
                        "3",
                        "Invalid storage type: (NONE)",
                        "Invalid storage type: (NONE)",
                        "Invalid storage type: (NONE)",
                        "Invalid storage type: (NONE)",
                        "Invalid storage type: (NONE)",
                        "None",
                        "-1",
                    ],
                ]
            elif self.revit_version_number > 2022:
                expected_result_file_read = [
                    [
                        "HOSTFILE",
                        "Id",
                        "View Template",
                        "View Name",
                        "Dependency",
                        "Visibility/Graphics Overrides",
                        "Phase Filter",
                        "Phase",
                        "Fields",
                        "Filter",
                        "Sorting/Grouping",
                        "Formatting",
                        "Appearance",
                        "Export to IFC", #2023
                        "Design Stage",
                        "None",
                    ],
                    [
                        "TEST.rvt",
                        "970420",
                        "-1",
                        "Wall Schedule",
                        "Independent",
                        "Invalid storage type: (NONE)",
                        "2029",
                        "3",
                        "Invalid storage type: (NONE)",
                        "Invalid storage type: (NONE)",
                        "Invalid storage type: (NONE)",
                        "Invalid storage type: (NONE)",
                        "Invalid storage type: (NONE)",
                        "By Type", #2023
                        "None",
                        "-1",
                    ],
                ]
            # check file content and perform temp directory clean up
            csv_check = self.test_csv_file(
                self.get_full_file_path(OUTPUT_FILE_NAME), expected_result_file_read
            )
            return_value.update(csv_check)

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
