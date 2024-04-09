"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit design options tests . 
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

from test.Revit.TestUtils import revit_test
from test.Revit.Common.design_set_option import DESIGN_OPTION_DATA
from duHast.Revit.Common.design_set_options import get_design_options
from duHast.Utilities.Objects import result as res

# import Autodesk
import Autodesk.Revit.DB as rdb


class GetDesignOptions(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetDesignOptions, self).__init__(doc=doc, test_name="get_design_options")

    def _strip_primary(self, option_name):
        """
        Strips anything after ' <' from an option name. ie. <primary> if in option name. Otherwise the name will be returned unchanged.

        :param option_name: The design option name.
        :type option_name: str
        :return: Option name without the primary indicator
        :rtype: str
        """

        if "<" in option_name:
            option_name = option_name[: option_name.index("<") - 2]
        return option_name

    def test(self):
        """
        get design options test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .status True if design options where retrieved successfully, otherwise False.
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
            result_sets = get_design_options(self.document)
            # get the option names only
            result = list(
                [
                    self._strip_primary(rdb.Element.Name.GetValue(entry))
                    for entry in result_sets
                ]
            )
            # get all option names
            expected_result = list(do[0] for do in DESIGN_OPTION_DATA)
            return_value.append_message(
                " {} vs {}".format(sorted(result), sorted(expected_result))
            )

            assert sorted(result) == sorted(expected_result)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(
                    self.test_name,e
                ),
            )

        return return_value
