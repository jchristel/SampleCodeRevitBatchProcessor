"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit revision mark as issued tests . 
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
from duHast.Revit.Revisions.revisions import create_revision, mark_revision_as_issued
from duHast.Utilities import result as res


class MarkIssued(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(MarkIssued, self).__init__(doc=doc)

    def test(self):
        """
        mark_revision_as_issued test

        Creates a revision and then attempts to mark it as issued.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :return: True if revision was marked issued successfully, otherwise False
        :rtype: Boolean
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
                    if result.status:
                        action_return_value = mark_revision_as_issued(
                            doc, result.result[0]
                        )
                        assert action_return_value.status == True
                    else:
                        # throw an exception...
                        raise ValueError(result.message)
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "An exception occurred in function test mark revision as issued {}".format(
                            e
                        ),
                    )
                return action_return_value

            return_value = self.in_transaction_group(action)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function test mark revision as issued {}".format(
                    e
                ),
            )

        return return_value
