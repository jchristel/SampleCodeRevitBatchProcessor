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


from test.Revit.TestUtils.run_revit_tests import RevitRunTest
from duHast.Utilities.Objects import result as res

# import test classes
from test.Revit.Common import design_sets_get
from test.Revit.Common import design_options_get
from test.Revit.Common import custom_element_filter_action_contains_any_of_values
from test.Revit.Common import custom_element_filter_action_does_not_contain_values
from test.Revit.Common import colour_base


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
        ["Get Design Sets", design_sets_get.GetDesignSets],
        ["Get Design Options", design_options_get.GetDesignOptions],
        [
            "Custom Element Filter Name Contains",
            custom_element_filter_action_contains_any_of_values.CustomElementFilterActionPropertyContains,
        ],
        [
            "Custom Element Filter Name Does Not Contains",
            custom_element_filter_action_does_not_contain_values.CustomElementFilterActionPropertyDoesNotContains,
        ],
        [
            "Colour base ini test",
            colour_base.ColourB,
        ],
    ]

    runner = RevitRunTest(run_tests)
    return_value = runner.run_tests(doc)

    return return_value
