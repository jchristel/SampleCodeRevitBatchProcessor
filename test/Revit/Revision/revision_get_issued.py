"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit get issued revisions tests . 
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
from duHast.Revit.Revisions.revisions import (
    create_revision,
    mark_revision_as_issued_by_revision_id,
    get_issued_revisions,
)
from duHast.Utilities import result as res


class GetIssuedRevisions(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetIssuedRevisions, self).__init__(doc=doc, test_name="get_issued_revisions")

    def test(self):
        """
        get_issued_revisions test

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
                    # test model has no issued revisions to start with, check for empty:
                    result = get_issued_revisions(doc)
                    expected_result = []
                    action_return_value.append_message(
                        "Issued revs in model: {} ".format(result)
                    )
                    assert result == expected_result

                    # set up a revision , mark it as issued
                    result = create_revision(doc, test_data)
                    # check revision was created
                    if result.status == False:
                        raise ValueError(result.message)
                    # mark revision as issued
                    result = mark_revision_as_issued_by_revision_id(
                        doc, result.result[0].Id
                    )
                    if result.status == False:
                        raise ValueError(result.message)

                    # check for issued revision again
                    result = get_issued_revisions(doc)
                    # there should be one issued revision in the model
                    expected_result = 1
                    action_return_value.append_message(
                        "{} vs {}".format(len(result), expected_result)
                    )
                    assert len(result) == expected_result

                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "An exception occurred in test {}: {}".format(
                            self.test_name,e
                        ),
                    )
                return action_return_value

            return_value = self.in_transaction_group(action)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in test {}: {}".format(
                    self.test_name,e
                ),
            )

        return return_value
