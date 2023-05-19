"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit design set tests . 
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

from test.Revit.TestUtils import revit_test
from test.Revit.Common.design_set_option import DESIGN_OPTION_DATA
from duHast.Revit.Common.design_set_options import get_design_sets
from duHast.Utilities import result as res

# import Autodesk
import Autodesk.Revit.DB as rdb


class GetDesignSets(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetDesignSets, self).__init__(doc=doc, test_name="get_design_sets")

    def test(self):
        """
        get design sets test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if design sets where retrieved successfully, otherwise False.
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
            result_sets = get_design_sets(self.document)
            # get the set names only
            result = list(rdb.Element.Name.GetValue(entry) for entry in result_sets)
            # get a unique list of design set names
            expected_result = list(set(do[1] for do in DESIGN_OPTION_DATA))
            return_value.append_message(
                " {} vs {}".format(sorted(result), sorted(expected_result))
            )

            assert sorted(result) == sorted(expected_result)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name,e),
            )

        return return_value
