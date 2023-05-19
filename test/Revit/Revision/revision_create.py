"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit create revision tests . 
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
from duHast.Utilities import result as res


class CreateRevision(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(CreateRevision, self).__init__(doc=doc, test_name="create_revision")

    def test(self):
        """
        Attempts to create a revision in revit.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str
        
        :return:
            Result class instance.
                - .result = True if revision was created successfully, otherwise False
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
                    create_rev_value = create_revision(doc, test_data)
                    assert create_rev_value.status == True
                    assert len(create_rev_value.result) == 1
                    assert (
                        create_rev_value.result[0].Description == test_data.description
                    )
                    assert create_rev_value.result[0].IssuedTo == test_data.issued_to
                    assert create_rev_value.result[0].IssuedBy == test_data.issued_by
                    assert (
                        create_rev_value.result[0].RevisionDate
                        == test_data.revision_date
                    )
                    assert (
                        create_rev_value.result[0].Visibility
                        == test_data.tag_cloud_visibility
                    )
                    assert (
                        create_rev_value.result[0].NumberType
                        == test_data.revision_number_type
                    )
                    action_return_value.update_sep(
                        True, "Created revision successfully."
                    )
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "An exception occurred in function {}: {}".format(
                            self.test_name, e
                        ),
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
