"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module runs all revit common related tests . 
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


from test.Revit.TestUtils.run_revit_tests import RevitRunTest
from duHast.Utilities import result as res

# import test classes
from test.Revit.Common import design_sets_get
from test.Revit.Common import design_options_get
from test.Revit.Common import custom_element_filter_action_name_contains_any_of_values


def run_design_set_options_tests(doc):
    """
    Runs all views related tests.

    :param doc: Current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True if all tests completed successfully, otherwise False.
    :rtype: bool
    """

    return_value = res.Result()

    # start tests -> should run ... tests first since they form
    # part of ... tests

    run_tests = [
        ["Get Design Sets" , design_sets_get.GetDesignSets],
        ["Get Design Options", design_options_get.GetDesignOptions ],
        ["Custom Element Filter Name Contains", custom_element_filter_action_name_contains_any_of_values.CustomElementFilterActionNameContains],
    ]

    runner = RevitRunTest(run_tests)
    return_value = runner.run_tests(doc)

    return return_value
