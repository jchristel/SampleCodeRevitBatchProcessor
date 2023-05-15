"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit create revision alphanumeric sequence tests . 
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
from test.Revit.Revision.sequence import ALPHA_SEQUENCE_NAME
from duHast.Revit.Revisions.sequence import create_revision_alpha_seq
from duHast.Utilities import result as res


class CreateAlphaSequence(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(CreateAlphaSequence, self).__init__(doc=doc)

    def test(self):
        """
        create_revision_alpha_seq test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :return: True if all tests pass, otherwise False
        :rtype: bool
        """

        return_value = res.Result()
        try:
            # create a mock revision sequence
            expected_result = ALPHA_SEQUENCE_NAME

            # action to be executed in a transaction group so it can be rolled back at end of test
            def action(doc):
                action_return_value = res.Result()
                try:
                    result = create_revision_alpha_seq(doc, expected_result)
                    action_return_value.append_message(" {} vs {}".format(result.Name, expected_result))
                    assert result.Name == expected_result
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "An exception occurred in test create revision alpha seq {}".format(
                            e
                        ),
                    )
                return action_return_value

            return_value = self.in_transaction_group(action)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in test create revision alpha seq {}".format(
                    e
                ),
            )

        return return_value
