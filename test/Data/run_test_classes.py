"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module runs all utility related tests . 
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

from duHast.Utilities.Objects.result import Result
from test.utils.run_tests import RunTest

# import test classes
from test.Data import (
    data_families_reading_families,
    data_families_container_reading_single,
    data_families_container_reading_multiple,
    data_families_culling_nested_families,
    data_families_reading_family_base_report,
    data_families_reading_categories_report,
    data_families_reading_line_patterns_report,
    data_families_reading_shared_parameters_report,
    data_families_reading_family_warnings_report,
    data_families_circular_nesting,
    data_families_find_none_nested_root_families,
    data_families_find_host_families_needing_rename,
    data_families_combine_reports,
)


def run_tests():
    """
    Runs all data related tests.

    :return: dictionary containing
         - the test name as key and as values
         - a flag (true if test completed successfully, otherwise false)
         - message string
    :rtype: {str:bool,str}
    """

    return_value = {}
    # list of tests to be run
    run_tests = [
        ["Data Read Overall Family Data Report", data_families_reading_family_base_report.DataReadFamiliesBaseReport],
        ["Data Read Families Categories Report", data_families_reading_categories_report.DataReadFamiliesCategoriesReport],
        ["Data Read Families line patterns Report", data_families_reading_line_patterns_report.DataReadFamiliesLinePatternsReport],
        ["Data Read Families Shared Parameters Report", data_families_reading_shared_parameters_report.DataReadFamiliesSharedParametersReport],
        ["Data Read Families Warnings Report", data_families_reading_family_warnings_report.DataReadFamiliesWarningsReport],
        ["Data Read Families Container-single", data_families_container_reading_single.DataReadFamiliesIntoContainer],
        ["Data Read Families Container-multiple", data_families_container_reading_multiple.DataReadFamiliesIntoContainers],
        ["Data Read Families Into Family Instances", data_families_reading_families.DataReadFamiliesIntoFamilyInstances],
        #["Data Find None Nested Root families", data_families_find_none_nested_root_families.DataFindNoneNestedRootFamilies],
        ["Data Nested Family culling", data_families_culling_nested_families.DataCullingNestedFamilies],
        ["Data find circular nesting", data_families_circular_nesting.DataCircularNestingFamilies],
        #["Data Find Host Families With Families To Rename", data_families_find_host_families_needing_rename.DataFindHostFamiliesWithFamiliesToRename],
        #["Data Combine Reports", data_families_combine_reports.DataCombineFamiliesReports],
    ]

    try:
        # run tests
        runner = RunTest(run_tests)
        return_value = runner.run_tests()
    except Exception as e:
        return_value["Data Tests"] = [False, "Data Tests failed: {}".format(str(e))]

    return return_value
