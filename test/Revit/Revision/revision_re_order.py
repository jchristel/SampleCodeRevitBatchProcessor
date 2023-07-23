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
from test.Revit.Revision.revision import TEST_DATA_2022, TEST_DATA_2023
from duHast.Revit.Revisions.revisions import create_revision
from duHast.Revit.Revisions.revisions import re_order_revisions
from duHast.Utilities.Objects import result as res

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
