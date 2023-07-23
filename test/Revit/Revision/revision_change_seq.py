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
from duHast.Revit.Revisions.revisions import change_revision_sequence_number
from duHast.Utilities.Objects import result as res


class ChangeRevSeq(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(ChangeRevSeq, self).__init__(doc=doc, test_name="change_revision_sequence_number")

    def test(self):
        """
        Change revision sequence test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if revision sequence was changed successfully, otherwise False
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
                    # add another few revision to model
                    revisions = []
                    for i in range(5):
                        result = create_revision(doc, test_data)
                        if result.status:
                            revisions.append(result.result[0])
                        else:
                            raise ValueError(result.message)

                    # move revisions around...
                    # first test -> pass in same sequence number

                    expected_result = revisions[0].SequenceNumber
                    result = change_revision_sequence_number(
                        doc, revisions[0], expected_result
                    )
                    action_return_value.append_message(
                        " {} vs {} vs status: {} message: {}".format(
                            revisions[0].SequenceNumber,
                            expected_result,
                            result.status,
                            result.message,
                        )
                    )
                    assert result.status == True
                    assert revisions[0].SequenceNumber == expected_result

                    # second test -> pass in sequence number + 1
                    expected_result = revisions[1].SequenceNumber + 1
                    result = change_revision_sequence_number(
                        doc, revisions[1], expected_result
                    )
                    action_return_value.append_message(
                        " {} vs {} vs status: {} message: {}".format(
                            revisions[1].SequenceNumber,
                            expected_result,
                            result.status,
                            result.message,
                        )
                    )
                    assert result.status == True
                    assert revisions[1].SequenceNumber == expected_result

                    # third test -> pass in invalid sequence number (outside of range)
                    expected_result = revisions[2].SequenceNumber
                    result = change_revision_sequence_number(doc, revisions[2], 10)
                    action_return_value.append_message(
                        " {} vs {} vs status: {} message: {}".format(
                            revisions[2].SequenceNumber,
                            expected_result,
                            result.status,
                            result.message,
                        )
                    )
                    assert result.status == False
                    assert revisions[2].SequenceNumber == expected_result
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
