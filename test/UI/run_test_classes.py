"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module runs all revit UI related tests . 
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


from test.utils.run_tests import RunTest

# import test classes
from test.UI import (
    file_list_bucket_to_task_list_item_b360,
    file_list_is_back_up_file,
    file_list_get_revit_files,
    workloader
)


def run_tests():
    """
    Runs all UI related tests.

    :return: dictionary containing
         - the test name as key and as values
         - a flag (true if test completed successfully, otherwise false)
         - message string
    :rtype: {str:bool,str}
    """

    # list of tests to be run
    run_tests = [
        ['Is Back Up File', file_list_is_back_up_file.IsBackUpFile],
        ['Get Revit Files', file_list_get_revit_files.GetRevitFiles],
        ["File List Bucket To Task List Item BIM 360", file_list_bucket_to_task_list_item_b360.BucketToTaskListBIM360],
        ["Workloader", workloader.Workloader],
    ]

    # run tests
    runner = RunTest(run_tests)
    return_value = runner.run_tests()

    return return_value
