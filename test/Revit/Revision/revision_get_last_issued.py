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
from test.Revit.Revision.revision import TEST_DATA_2022, TEST_DATA_2023
from duHast.Revit.Revisions.revisions import (
    create_revision,
    mark_revision_as_issued_by_revision_id,
    get_last_issued_revision,
)
from duHast.Utilities.Objects import result as res


class GetLastIssuedRevisions(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetLastIssuedRevisions, self).__init__(doc=doc, test_name="get_last_issued_revision")

    def test(self):
        """
        get_last_issued_revisions test

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
                    result = get_last_issued_revision(doc)
                    expected_result = None
                    action_return_value.append_message( " {} vs {}".format(result, expected_result) )
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

                    # should get a list one 1 back
                    # issued revision should have sequence number 2
                    result = get_last_issued_revision(doc)
                    expected_result = 2
                    action_return_value.append_message(" {} vs {}".format(result.SequenceNumber, expected_result))
                    assert result.SequenceNumber == expected_result

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
                    
                    # should get a list one 1 back
                    # issued revision should have sequence number 3
                    result = get_last_issued_revision(doc)
                    expected_result = 3
                    action_return_value.append_message( " {} vs {}".format(result.SequenceNumber, expected_result))
                    assert result.SequenceNumber == expected_result

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
                "An exception occurred in test {}: {}".format(self.test_name,e),
            )

        return return_value
