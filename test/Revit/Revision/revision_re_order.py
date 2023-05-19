"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit change revision sequence tests . 
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
from test.Revit.Revision.revision import TEST_DATA_2022, TEST_DATA_2023
from duHast.Revit.Revisions.revisions import create_revision
from duHast.Revit.Revisions.revisions import re_order_revisions
from duHast.Utilities import result as res

# import Autodesk
import Autodesk.Revit.DB as rdb

# required for .ToList()
import clr
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)

class ChangeRevOrder(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(ChangeRevOrder, self).__init__(doc=doc, test_name="re_order_revisions")

    def _get_id_integers_from_list(self, my_list):
        """
        Returns a list representing the integer values of ids list past in.

        :param my_list: A list of element ids
        :type my_list: [Autodesk.Revit.DB.ElementId]
        :return: A list of integers
        :rtype: [int]
        """

        ids = []
        for item in my_list:
            ids.append(item.IntegerValue)
        return ids

    def test(self):
        """
        re_order_revisions test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str
        
        :return:
            Result class instance.
                - .result = True if test past successfully, otherwise False
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
            # check which revit version
            test_data = None
            if self.revit_version_number <= 2022:
                test_data = TEST_DATA_2022
            else:
                test_data = TEST_DATA_2023

            # action to be executed in a transaction group so it can be rolled back at end of test
            def action(doc):
                action_return_value = res.Result()
                try:
                    result = create_revision(doc, test_data)
                    # check revision was created
                    if result.status == False:
                        raise ValueError(result.message)

                    # get revisions in model
                    revisions_in_model = rdb.Revision.GetAllRevisionIds(doc)
                    # and reverse the list because thats what the end result should look like
                    expected_result = list(reversed(revisions_in_model)).ToList[
                        rdb.ElementId
                    ]()

                    # apply new revisions order to model
                    result = re_order_revisions(doc, expected_result)

                    # get revisions now in the model
                    revisions_in_model_re_ordered = rdb.Revision.GetAllRevisionIds(doc)

                    action_return_value.append_message(
                        "from result: {} vs expected: {} vs model: {}".format(
                            self._get_id_integers_from_list(result.result),
                            self._get_id_integers_from_list(expected_result),
                            self._get_id_integers_from_list(
                                revisions_in_model_re_ordered
                            ),
                        )
                    )
                    # compare all three values
                    assert self._get_id_integers_from_list(
                        result.result
                    ) == self._get_id_integers_from_list(expected_result)
                    assert self._get_id_integers_from_list(
                        result.result
                    ) == self._get_id_integers_from_list(revisions_in_model_re_ordered)
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "An exception occurred in {}: {}".format(self.test_name, e),
                    )
                return action_return_value

            return_value = self.in_transaction_group(action)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(
                    self.test_name,e
                ),
            )

        return return_value
