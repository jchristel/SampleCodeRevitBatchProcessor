"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module runs all revit revision related tests . 
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



from test.utils.rbp_setup import add_rbp_ref
from test.utils.padding import pad_header_no_time_stamp

import test.Revit.Revision.change_revision_seq as change_rev_seq
from duHast.Utilities import result as res

#: Type of test run flag. If False run in revit python shell. If True runs in revit batch processor.
IS_RBP_RUN = False


def run_revision_tests(doc, rbp_run_type=IS_RBP_RUN):
    """
    Runs all revision related tests.

    :param doc: Current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True if all tests completed successfully, otherwise False.
    :rtype: bool
    """

    return_value = res.Result()
    if rbp_run_type == True:
        # add revit batch processor references and get the current document
        doc = add_rbp_ref()

    # start tests -> should run revision sequence tests first since they form
    # part of revision tests

    run_tests = [
        ["Revision Sequence", change_rev_seq.ChangeRevSeq],
    ]

    for test in run_tests:
        return_value.append_message(pad_header_no_time_stamp(test[0]))
        test_class = test[1](doc)
        result_test = test_class.test()
        return_value.update(result_test)
    
    return return_value