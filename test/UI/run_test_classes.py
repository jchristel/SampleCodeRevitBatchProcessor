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


from test.utils.run_tests import RunTest

# import test classes
from test.UI import (
    file_list_bucket_to_task_list_item_b360,
    file_list_is_back_up_file,
    file_list_get_revit_files,
    workloader,
    file_list_write_revit_task_file,
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
        ["Write Revit Task List", file_list_write_revit_task_file.WriteRevitTaskFile],
    ]

    # run tests
    runner = RunTest(run_tests)
    return_value = runner.run_tests()

    return return_value
